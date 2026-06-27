#!/usr/bin/env python3
"""M4b: run the TensorRT FP16 engine on saved JetRover camera frames.

Loads ``models/best.engine`` (or any path passed via ``--engine``), runs it
on every JPG in ``--input-dir``, and writes:

- one annotated PNG per input frame (``--output-dir/<stem>_pred.png``)
- a single ``detections.json`` containing per-frame detection lists and
  per-frame engine latency (forward pass only, in milliseconds)

The script intentionally has no ROS 2 dependency so it can run on either
the dev PC (OR CPU ORT fallback would need ``--provider`` flag, NOT
implemented here) or the Jetson Orin Nano (real target -- this is M4b's
primary backend). Latency numbers on the Jetson are the realistic numbers
to use for the M5 ROS node budget.

Implementation notes (M4b 2026-06-27):

The TensorRT engine produces correct non-zero outputs in three places:
  1. fresh Python interpreter per invocation (probe subprocess)
  2. a single __main__ script with inline code, ONE binding allocation,
     and the shared CUDA stream across all frames (steady_state.py)
  3. test_inference.py with helper-function decomposition -- BROKEN
     (returned all-zero output, ~1.5 ms fake latency after the first
     call). We could not isolate the cause, but it appears to be a
     subtle interaction between pycuda's Stream handle passing across
     function boundaries and the engine's internal scratch space on
     JetPack 6 / TensorRT 8.6.2 / pycuda 2024.1.

Because of (3), the in-process ``run_inference`` here uses the proven
inline pattern from (2): a single stream created at script top-level,
plain ``int(np.prod(shape))`` buffer sizing, ``np.copyto`` into the
pagelocked input, ``cuda.memcpy_htod_async``, ``ctx.execute_async_v2``,
``stream.synchronize``, ``cuda.memcpy_dtoh_async``, ``stream.synchronize``.
On 90 alternating-frame iterations this measured 14.66 ms median
forward-pass latency on the Orin Nano.

Usage (Jetson):

    python3 scripts/test_inference.py \\
        --engine models/best.engine \\
        --input-dir evaluation/camera_samples/cubes_2026-06-27_m4b \\
        --output-dir evaluation/m4b_predictions \\
        --conf 0.25 --iou 0.45

Usage (dev PC, same engine, same frames, slower):

    python3 scripts/test_inference.py \\
        --engine models/best.engine \\
        --input-dir evaluation/camera_samples/cubes_2026-06-27_m4b \\
        --output-dir evaluation/m4b_predictions_devpc \\
        --conf 0.25 --iou 0.45
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

CLASS_NAMES = ["blue_cube", "green_cube", "red_cube"]
# Display colors per class: (R, G, B) for the bounding-box outline.
CLASS_COLORS = {
    "blue_cube": (66, 133, 244),
    "green_cube": (52, 168, 83),
    "red_cube": (234, 67, 53),
}


def letterbox(im: np.ndarray, new_shape: int = 640):
    """Resize+pad to a square new_shape, preserving aspect ratio."""
    h0, w0 = im.shape[:2]
    r = min(new_shape / h0, new_shape / w0)
    new_w, new_h = int(round(w0 * r)), int(round(h0 * r))
    pad_w, pad_h = new_shape - new_w, new_shape - new_h
    pad_l, pad_t = pad_w // 2, pad_h // 2
    pad_r, pad_b = pad_w - pad_l, pad_h - pad_t
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


def annotate(pil_img: Image.Image, detections: list, conf_thres: float) -> Image.Image:
    """Draw bounding boxes + labels on a copy of pil_img and return it."""
    out = pil_img.copy()
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14
        )
    except OSError:
        font = ImageFont.load_default()
    for name, conf, box in detections:
        x1, y1, x2, y2 = box
        color = CLASS_COLORS.get(name, (255, 255, 0))
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        label = f"{name} {conf:.2f}"
        tb = draw.textbbox((x1, y1), label, font=font)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        bg_y1 = max(0, y1 - th - 4)
        draw.rectangle([x1, bg_y1, x1 + tw + 6, y1], fill=color)
        text_color = (255, 255, 255) if name != "green_cube" else (0, 0, 0)
        draw.text((x1 + 3, bg_y1 + 2), label, fill=text_color, font=font)
    draw.rectangle([0, 0, out.width, 18], fill=(0, 0, 0))
    draw.text(
        (4, 2),
        f"TensorRT FP16 | conf>={conf_thres:.2f} | dets={len(detections)}",
        fill=(255, 255, 255),
        font=font,
    )
    return out


def gather_images(input_dir: Path) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png"}
    return sorted(p for p in input_dir.iterdir() if p.suffix.lower() in exts)


def decode_yolov5_output(out, conf_thres, iou_thres, orig_wh, ratio, pad):
    """Decode Ultralytics YOLOv5 fused-decode output [1, 7, 8400]."""
    import torch
    from torchvision.ops import nms

    pred = out[0].transpose()
    boxes = pred[:, :4]
    scores = pred[:, 4:]
    cls_conf = scores.max(axis=1)
    cls_id = scores.argmax(axis=1)
    mask = cls_conf >= conf_thres
    boxes, cls_conf, cls_id = boxes[mask], cls_conf[mask], cls_id[mask]
    if boxes.shape[0] == 0:
        return []

    xyxy = np.zeros_like(boxes)
    xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2
    pad_l, pad_t = pad
    xyxy[:, [0, 2]] -= pad_l
    xyxy[:, [1, 3]] -= pad_t
    xyxy /= ratio
    ow, oh = orig_wh
    xyxy[:, [0, 2]] = xyxy[:, [0, 2]].clip(0, ow - 1)
    xyxy[:, [1, 3]] = xyxy[:, [1, 3]].clip(0, oh - 1)

    keep: list[int] = []
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


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--engine", required=True, type=Path)
    p.add_argument("--input-dir", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou", type=float, default=0.45)
    p.add_argument("--no-annotate", action="store_true")
    args = p.parse_args()

    if not args.engine.exists():
        raise SystemExit(f"engine not found: {args.engine}")
    if not args.input_dir.exists():
        raise SystemExit(f"input dir not found: {args.input_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    images = gather_images(args.input_dir)
    if not images:
        raise SystemExit(f"no .jpg/.jpeg/.png files in {args.input_dir}")
    print(f"[m4b] engine: {args.engine}")
    print(f"[m4b] input : {args.input_dir} ({len(images)} images)")
    print(f"[m4b] output: {args.output_dir}")
    print(f"[m4b] conf={args.conf}  iou={args.iou}  imgsz={args.imgsz}")

    # === TensorRT / CUDA setup (inline, no helper-function wrapping) ===
    # The TensorRT 8.6.2 + pycuda 2024.1 combination on JetPack 6 produced
    # all-zero outputs when we wrapped allocation in helpers and passed the
    # Stream across function boundaries. Keeping everything inline here.
    import tensorrt as trt  # Jetson only
    import pycuda.driver as cuda
    import pycuda.autoinit  # noqa: F401

    trt_logger = trt.Logger(trt.Logger.WARNING)
    with open(args.engine, "rb") as f:
        engine_bytes = f.read()
    engine = trt.Runtime(trt_logger).deserialize_cuda_engine(engine_bytes)
    if engine is None:
        raise RuntimeError(f"engine deserialization failed for {args.engine}")
    ctx = engine.create_execution_context()

    # Get binding info via the TensorRT 10.x API path (8.6 also exposes
    # get_tensor_* names on this build).
    in_name = engine.get_tensor_name(0)
    out_name = engine.get_tensor_name(1)
    in_shape = tuple(engine.get_tensor_shape(in_name))
    out_shape = tuple(engine.get_tensor_shape(out_name))
    in_dtype = trt.nptype(engine.get_tensor_dtype(in_name))
    out_dtype = trt.nptype(engine.get_tensor_dtype(out_name))

    in_host = cuda.pagelocked_empty(int(np.prod(in_shape)), in_dtype)
    out_host = cuda.pagelocked_empty(int(np.prod(out_shape)), out_dtype)
    in_dev = cuda.mem_alloc(in_host.nbytes)
    out_dev = cuda.mem_alloc(out_host.nbytes)
    bindings = [int(in_dev), int(out_dev)]
    stream = cuda.Stream()

    print(f"[m4b] input  binding '{in_name}' shape={in_shape}")
    print(f"[m4b] output binding '{out_name}' shape={out_shape}")

    # === Per-frame inference loop ===
    results: list[dict] = []
    class_frame_hits = {c: 0 for c in CLASS_NAMES}
    class_conf_sums = {c: [] for c in CLASS_NAMES}
    all_latencies_ms: list[float] = []

    for idx, img_path in enumerate(images, 1):
        pil = Image.open(img_path).convert("RGB")
        im0 = np.array(pil)
        orig_h, orig_w = im0.shape[:2]
        img, r, (pad_l, pad_t) = letterbox(im0, args.imgsz)
        img = img.astype(np.float32) / 255.0
        img = img.transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        img = img[np.newaxis, ...]

        np.copyto(in_host, img.ravel())
        cuda.memcpy_htod_async(in_dev, in_host, stream)
        t0 = time.perf_counter()
        ctx.execute_async_v2(bindings=bindings, stream_handle=stream.handle)
        stream.synchronize()
        ms = (time.perf_counter() - t0) * 1000.0
        cuda.memcpy_dtoh_async(out_host, out_dev, stream)
        stream.synchronize()
        out = out_host.reshape(out_shape)

        dets = decode_yolov5_output(
            out, args.conf, args.iou, (orig_w, orig_h), r, (pad_l, pad_t)
        )

        all_latencies_ms.append(ms)
        for name, conf, _ in dets:
            class_frame_hits[name] += 1
            class_conf_sums[name].append(conf)

        results.append({
            "filename": img_path.name,
            "width": orig_w,
            "height": orig_h,
            "engine_ms": ms,
            "num_detections": len(dets),
            "detections": [
                {
                    "class": name,
                    "confidence": conf,
                    "bbox_xyxy": [box[0], box[1], box[2], box[3]],
                }
                for name, conf, box in dets
            ],
        })

        print(
            f"[m4b] {idx:3d}/{len(images)}  {img_path.name:18s}  "
            f"dets={len(dets):2d}  ms={ms:6.2f}  "
            + "  ".join(f"{n.split('_')[0]}={c:.2f}" for n, c, _ in dets)
        )

        if not args.no_annotate:
            ann = annotate(pil, dets, args.conf)
            ann.save(args.output_dir / f"{img_path.stem}_pred.png", "PNG")

    # === Summary ===
    n = len(images)
    lat = np.array(all_latencies_ms)
    summary = {
        "engine": str(args.engine),
        "input_dir": str(args.input_dir),
        "output_dir": str(args.output_dir),
        "conf_threshold": args.conf,
        "iou_threshold": args.iou,
        "num_frames": n,
        "latency_ms": {
            "min": float(lat.min()),
            "median": float(np.median(lat)),
            "mean": float(lat.mean()),
            "max": float(lat.max()),
            "p95": float(np.percentile(lat, 95)),
        },
        "fps_estimate_median": 1000.0 / float(np.median(lat)),
        "per_class_frame_hits": class_frame_hits,
        "per_class_detection_rate": {c: class_frame_hits[c] / n for c in CLASS_NAMES},
        "per_class_mean_confidence": {
            c: (float(np.mean(class_conf_sums[c]))
                if class_conf_sums[c] else None)
            for c in CLASS_NAMES
        },
        "per_class_total_detections": {
            c: len(class_conf_sums[c]) for c in CLASS_NAMES
        },
        "frames": results,
    }

    out_json = args.output_dir / "detections.json"
    out_json.write_text(json.dumps(summary, indent=2))
    print(f"[m4b] wrote {out_json}")
    print(f"[m4b] latency  min={lat.min():.2f}  median={np.median(lat):.2f}  "
          f"mean={lat.mean():.2f}  max={lat.max():.2f}  ms")
    print(f"[m4b] fps estimate (median): {1000.0 / float(np.median(lat)):.1f}")
    print(f"[m4b] per-class frame-hit rate:")
    for c in CLASS_NAMES:
        rate = class_frame_hits[c] / n
        mean_c = summary["per_class_mean_confidence"][c]
        mean_s = f"{mean_c:.3f}" if mean_c is not None else "—"
        print(f"        {c:11s}  {class_frame_hits[c]:2d}/{n} ({rate*100:5.1f}%)  "
              f"mean conf={mean_s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())