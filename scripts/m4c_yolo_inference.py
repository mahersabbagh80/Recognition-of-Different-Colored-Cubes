"""Run YOLOv5 ONNX inference on a directory of RGB JPGs (no _rgb suffix)."""
import argparse
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image

CLASS_NAMES = ["blue_cube", "green_cube", "red_cube"]


def letterbox(im: np.ndarray, new_shape: int = 640):
    h0, w0 = im.shape[:2]
    r = min(new_shape / h0, new_shape / w0)
    new_w, new_h = int(round(w0 * r)), int(round(h0 * r))
    pad_w, pad_h = new_shape - new_w, new_shape - new_h
    pad_l, pad_t = pad_w // 2, pad_h // 2
    pad_r, pad_b = pad_w - pad_l, pad_h - pad_t
    img = np.array(Image.fromarray(im).resize((new_w, new_h), 1))
    img = np.pad(
        img, ((pad_t, pad_b), (pad_l, pad_r), (0, 0)),
        mode="constant", constant_values=114,
    )
    return img, r, (pad_l, pad_t)


def decode(out, conf_thres, iou_thres, orig_wh, ratio, pad):
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


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--onnx", required=True, type=Path)
    p.add_argument("--rgb-dir", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--glob", default="*.jpg",
                   help="glob pattern for input images (default: *.jpg)")
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou", type=float, default=0.45)
    p.add_argument("--imgsz", type=int, default=640)
    args = p.parse_args()

    import onnxruntime as ort
    sess = ort.InferenceSession(
        str(args.onnx), providers=["CPUExecutionProvider"]
    )
    in_name = sess.get_inputs()[0].name
    out_name = sess.get_outputs()[0].name
    print(f"[m4c-yolo] onnx: {args.onnx}")
    print(f"[m4c-yolo] rgb-dir: {args.rgb_dir}  glob={args.glob}")

    images = sorted(args.rgb_dir.glob(args.glob))
    print(f"[m4c-yolo] {len(images)} images")
    if not images:
        return 1

    frames = []
    all_lat = []
    for idx, img_path in enumerate(images, 1):
        pil = Image.open(img_path).convert("RGB")
        im0 = np.array(pil)
        orig_h, orig_w = im0.shape[:2]
        img, r, (pad_l, pad_t) = letterbox(im0, args.imgsz)
        img = img.astype(np.float32) / 255.0
        img = img.transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        img = img[np.newaxis, ...]
        t0 = time.perf_counter()
        out = sess.run([out_name], {in_name: img})[0]
        ms = (time.perf_counter() - t0) * 1000.0
        all_lat.append(ms)
        dets = decode(out, args.conf, args.iou, (orig_w, orig_h), r, (pad_l, pad_t))
        frames.append({
            "filename": img_path.name,
            "width": orig_w,
            "height": orig_h,
            "yolo_ms": ms,
            "num_detections": len(dets),
            "detections": [
                {"class": n, "confidence": c, "bbox_xyxy": [b[0], b[1], b[2], b[3]]}
                for n, c, b in dets
            ],
        })

    lat = np.array(all_lat)
    summary = {
        "onnx": str(args.onnx),
        "rgb_dir": str(args.rgb_dir),
        "glob": args.glob,
        "conf_threshold": args.conf,
        "iou_threshold": args.iou,
        "num_frames": len(images),
        "yolo_latency_ms": {
            "min": float(lat.min()),
            "median": float(np.median(lat)),
            "mean": float(lat.mean()),
            "max": float(lat.max()),
        },
        "frames": frames,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2))
    total_dets = sum(len(f["detections"]) for f in frames)
    print(f"[m4c-yolo] wrote {args.output}  ({len(images)} frames, "
          f"{total_dets} total dets, median yolo ms={summary['yolo_latency_ms']['median']:.1f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
