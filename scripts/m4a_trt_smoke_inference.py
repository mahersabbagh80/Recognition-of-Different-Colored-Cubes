"""
M4a TensorRT FP16 engine smoke inference on the Jetson.

Loads models/best.engine on the Orin Nano, runs it on a saved validation
image (the same image used by the M3 ORT smoke check), decodes YOLOv5
output0 [1, 7, 8400] (xywh + per-class sigmoid scores), does per-class
conf filtering + torchvision NMS, then prints the detections in the
original image frame.

This proves the engine: (1) loads, (2) executes on the Jetson GPU,
(3) produces detections consistent with the M3 ORT baseline on the same
input. It does NOT replace live-camera accuracy work -- that is M4b.

Usage:
    python3 scripts/m4a_trt_smoke_inference.py \
        --engine ~/jetson_ws/best.engine \
        --image  ~/jetson_ws/valid_smoke.jpg \
        --imgsz 640 --conf 0.25 --iou 0.45
"""

import argparse
import time
from pathlib import Path

import numpy as np
from PIL import Image
import torch
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit  # noqa: F401 -- initializes the CUDA context


CLASS_NAMES = ["blue_cube", "green_cube", "red_cube"]


def letterbox(im: np.ndarray, new_shape: int = 640):
    """Resize+pad to a square new_shape, preserving aspect ratio."""
    h0, w0 = im.shape[:2]
    r = min(new_shape / h0, new_shape / w0)
    new_w, new_h = int(round(w0 * r)), int(round(h0 * r))
    pad_w, pad_h = new_shape - new_w, new_shape - new_h
    pad_l, pad_t = pad_w // 2, pad_h // 2
    pad_r = pad_w - pad_l
    pad_b = pad_h - pad_t
    img = np.array(
        Image.fromarray(im).resize((new_w, new_h), 1)  # 1 = PIL bilinear
    )
    img = np.pad(
        img,
        ((pad_t, pad_b), (pad_l, pad_r), (0, 0)),
        mode="constant",
        constant_values=114,
    )
    return img, r, (pad_l, pad_t)


def load_engine(path: str):
    trt_logger = trt.Logger(trt.Logger.WARNING)
    with open(path, "rb") as f:
        engine_bytes = f.read()
    runtime = trt.Runtime(trt_logger)
    engine = runtime.deserialize_cuda_engine(engine_bytes)
    if engine is None:
        raise RuntimeError(f"Failed to deserialize engine at {path}")
    return engine


def _binding_attrs(engine, i):
    """TensorRT 8.6 vs 10.x compatibility shim for binding accessors."""
    if hasattr(engine, "get_tensor_name"):
        # TensorRT 10.x API: pass the *name* to get_tensor_shape/dtype/mode,
        # get_tensor_name returns the binding name by index.
        name = engine.get_tensor_name(i)
        shape = tuple(engine.get_tensor_shape(name))
        dtype = trt.nptype(engine.get_tensor_dtype(name))
        is_input = engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT
    else:
        # TensorRT 8.x API: index-based accessors.
        name = engine.get_binding_name(i)
        shape = tuple(engine.get_binding_shape(i))
        dtype = trt.nptype(engine.get_binding_dtype(i))
        is_input = engine.binding_is_input(i)
    return name, shape, dtype, is_input


def allocate_buffers(engine):
    """Allocate host + device buffers for all I/O bindings."""
    h_inputs, d_inputs, h_outputs, d_outputs, bindings = [], [], [], [], []
    stream = cuda.Stream()
    for i in range(engine.num_bindings):
        name, shape, dtype, is_input = _binding_attrs(engine, i)
        size = int(np.prod(shape))
        host_mem = cuda.pagelocked_empty(size, dtype)
        device_mem = cuda.mem_alloc(host_mem.nbytes)
        bindings.append(int(device_mem))
        if is_input:
            h_inputs.append((name, host_mem, shape, dtype))
            d_inputs.append(device_mem)
        else:
            h_outputs.append((name, host_mem, shape, dtype))
            d_outputs.append(device_mem)
    return h_inputs, d_inputs, h_outputs, d_outputs, bindings, stream


def decode_yolov5_output(out: np.ndarray, conf_thres: float, iou_thres: float,
                          orig_wh: tuple, ratio: float, pad: tuple):
    """
    out shape: [1, 7, 8400]
    rows: x, y, w, h, c0, c1, c2  (xywh in 640x640 grid, class scores already
    sigmoid-activated -- Ultralytics fused decode head).
    Returns list of (class_name, conf, xyxy_in_orig_image).
    """
    pred = out[0]              # [7, 8400]
    pred = pred.transpose()    # [8400, 7]
    boxes = pred[:, :4]        # xywh in 640x640
    scores = pred[:, 4:]       # [8400, 3] sigmoid-activated class probs
    cls_conf = scores.max(axis=1)
    cls_id = scores.argmax(axis=1)
    mask = cls_conf >= conf_thres
    boxes, cls_conf, cls_id = boxes[mask], cls_conf[mask], cls_id[mask]
    if boxes.shape[0] == 0:
        return []

    # xywh -> xyxy in 640x640
    xyxy = np.zeros_like(boxes)
    xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2

    # undo letterbox -> original image coordinates
    pad_l, pad_t = pad
    xyxy[:, [0, 2]] -= pad_l
    xyxy[:, [1, 3]] -= pad_t
    xyxy /= ratio
    ow, oh = orig_wh
    xyxy[:, [0, 2]] = xyxy[:, [0, 2]].clip(0, ow - 1)
    xyxy[:, [1, 3]] = xyxy[:, [1, 3]].clip(0, oh - 1)

    # per-class NMS via torchvision
    from torchvision.ops import nms
    keep = []
    for c in np.unique(cls_id):
        idx = np.where(cls_id == c)[0]
        if idx.size == 0:
            continue
        b_c = torch.from_numpy(xyxy[idx]).float()
        s_c = torch.from_numpy(cls_conf[idx]).float()
        k = nms(b_c, s_c, iou_thres).numpy().tolist()
        keep.extend(idx[k])

    detections = []
    for i in sorted(keep):
        detections.append((
            CLASS_NAMES[int(cls_id[i])],
            float(cls_conf[i]),
            tuple(float(v) for v in xyxy[i]),
        ))
    return detections


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--engine", required=True)
    p.add_argument("--image", required=True)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou", type=float, default=0.45)
    args = p.parse_args()

    engine_path = Path(args.engine)
    image_path = Path(args.image)
    print(f"[m4a] engine: {engine_path} ({engine_path.stat().st_size} bytes)")
    print(f"[m4a] image:  {image_path} ({image_path.stat().st_size} bytes)")

    # 1. Load + letterbox
    pil = Image.open(image_path).convert("RGB")
    im0 = np.array(pil)
    orig_h, orig_w = im0.shape[:2]
    print(f"[m4a] image size: {orig_w}x{orig_h}")
    img, r, (pad_l, pad_t) = letterbox(im0, args.imgsz)
    img = img.astype(np.float32) / 255.0
    img = img.transpose(2, 0, 1)  # HWC -> CHW
    img = np.ascontiguousarray(img)
    img = img[np.newaxis, ...]     # [1, 3, 640, 640]

    # 2. Load engine + alloc
    engine = load_engine(str(engine_path))
    ctx = engine.create_execution_context()
    h_in, d_in, h_out, d_out, bindings, stream = allocate_buffers(engine)
    print(f"[m4a] inputs:  {[n for n, *_ in h_in]}")
    print(f"[m4a] outputs: {[n for n, *_ in h_out]}")

    # 3. Copy input to device
    input_name, input_host, input_shape, _ = h_in[0]
    print(f"[m4a] input binding '{input_name}' shape={input_shape}")
    assert tuple(input_shape) == img.shape, (
        f"engine expects {input_shape} but image tensor is {img.shape}")
    np.copyto(input_host, img.ravel())
    cuda.memcpy_htod_async(d_in[0], input_host, stream)

    # 4. Execute (timed)
    t0 = time.perf_counter()
    ctx.execute_async_v2(bindings=bindings, stream_handle=stream.handle)
    stream.synchronize()
    t1 = time.perf_counter()
    print(f"[m4a] forward pass (first, incl. CUDA context warmup): "
          f"{(t1 - t0) * 1000:.2f} ms")

    # 5. Copy output back
    output_name, output_host, output_shape, _ = h_out[0]
    cuda.memcpy_dtoh_async(output_host, d_out[0], stream)
    stream.synchronize()
    out = output_host.reshape(output_shape)
    print(f"[m4a] output binding '{output_name}' shape={output_shape}")

    # 6. Decode + NMS
    dets = decode_yolov5_output(out, args.conf, args.iou,
                                 (orig_w, orig_h), r, (pad_l, pad_t))
    print(f"[m4a] detections after conf>={args.conf} + NMS iou<={args.iou}: "
          f"{len(dets)}")
    for name, conf, box in dets:
        print(f"  {name:11s}  conf={conf:.3f}  "
              f"xyxy=({box[0]:6.1f},{box[1]:6.1f},{box[2]:6.1f},{box[3]:6.1f})")

    if not dets:
        print(f"[m4a] WARN: zero detections at conf={args.conf}. "
              "Try a lower conf (e.g. 0.10) or check input image content.")

    # 7. Steady-state timing: run 10 more forward passes
    timings = []
    for _ in range(10):
        t0 = time.perf_counter()
        ctx.execute_async_v2(bindings=bindings, stream_handle=stream.handle)
        stream.synchronize()
        timings.append((time.perf_counter() - t0) * 1000.0)
    timings = np.array(timings)
    print(f"[m4a] steady-state forward pass (10 runs): "
          f"min={timings.min():.2f} ms  median={np.median(timings):.2f} ms  "
          f"max={timings.max():.2f} ms")


if __name__ == "__main__":
    main()