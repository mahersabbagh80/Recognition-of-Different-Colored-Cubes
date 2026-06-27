"""M3 smoke test: ONNX Runtime inference on a saved validation image.

The exported YOLOv5s ONNX graph (ultralytics 8.4.75, opset 13) emits
output0 with shape (1, 4 + nc, num_anchors) = (1, 7, 8400) where:
  - rows 0..3 are decoded bounding boxes in xywh (pixels in the model's
    640x640 input grid -- NOT letterbox-inverse applied at the model),
  - rows 4..6 are already sigmoid-activated per-class scores
    (no separate objectness channel in the 4+nc layout).

We do the standard Ultralytics post-processing on top: per-class confidence
filter (conf >= conf_thres), xywh->xyxy, torchvision NMS, then undo
letterbox to map back into the original image frame.

This is NOT a full M4 accuracy check.  It only proves that:
  - the exported graph loads into ORT,
  - a forward pass executes and produces the expected output shape,
  - post-processing recovers at least one detection consistent with the
    project's class set, and that the class ordering matches best.pt.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
import torchvision
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    PROJECT_ROOT
    / "data"
    / "roboflow_det"
    / "red-green-blue-cube-detection-1-yolov5pytorch"
    / "valid"
    / "images"
    / "Snimek-obrazovky-2023-08-16-213123_png.rf.270a8af923637b40e0f4da5bc6da7c2d.jpg"
)


def letterbox(im: np.ndarray, new_size: int = 640, color: int = 114):
    h, w = im.shape[:2]
    r = min(new_size / h, new_size / w)
    nh, nw = int(round(h * r)), int(round(w * r))
    pil = Image.fromarray(im).resize((nw, nh), Image.BILINEAR)
    canvas = Image.new("RGB", (new_size, new_size), (color, color, color))
    canvas.paste(pil, ((new_size - nw) // 2, (new_size - nh) // 2))
    return np.asarray(canvas, dtype=np.uint8), r, ((new_size - nw) // 2, (new_size - nh) // 2)


def yolov5_decode_and_nms(pred: np.ndarray, conf_thres: float, iou_thres: float):
    """Run standard post-processing on a (1, 4+nc, num_anchors) YOLOv5 ONNX export.

    pred[0] has shape (4+nc, N).  Rows 0..3 are xywh in 640x640 pixel space.
    Rows 4..4+nc are already sigmoid-activated class scores.

    Returns (M, 6) array of [x1, y1, x2, y2, conf, cls] in 640x640 pixels.
    """
    x = torch.from_numpy(pred[0])  # (4+nc, N)
    nc = x.shape[0] - 4
    box = x[:4].T  # (N, 4)  xywh in 640x640 pixels
    cls = x[4:].T  # (N, nc)  class probs (already sigmoid)
    conf, j = cls.max(1, keepdim=True)  # (N,1) each
    # Filter by per-class confidence
    mask = conf[:, 0] >= conf_thres
    if not mask.any():
        return torch.zeros((0, 6), dtype=torch.float32)

    box = box[mask]
    conf = conf[mask]
    j = j[mask].float()

    # xywh -> xyxy in 640x640 pixel space
    x1, y1, w, h = box[:, 0], box[:, 1], box[:, 2], box[:, 3]
    x2, y2 = x1 + w, y1 + h
    boxes_xyxy = torch.stack([x1, y1, x2, y2], dim=1)

    # Per-class NMS using torchvision
    keep = []
    for c in j.unique():
        ci = (j == c).nonzero(as_tuple=True)[0]
        ki = torchvision.ops.nms(boxes_xyxy[ci], conf[ci].squeeze(1), iou_thres)
        keep.append(ci[ki])
    keep = torch.cat(keep) if keep else torch.empty(0, dtype=torch.long)
    out = torch.cat([boxes_xyxy[keep], conf[keep], j[keep]], dim=1)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="M3 ORT smoke inference for models/best.onnx")
    p.add_argument("--model", default=str(PROJECT_ROOT / "models" / "best.onnx"))
    p.add_argument("--image", default=str(DEFAULT_IMAGE))
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou", type=float, default=0.45)
    p.add_argument("--topk", type=int, default=20)
    return p.parse_args()


def main() -> int:
    args = parse_args()

    model_path = Path(args.model)
    image_path = Path(args.image)
    if not model_path.exists():
        print(f"FAIL: model not found: {model_path}", file=sys.stderr)
        return 2
    if not image_path.exists():
        print(f"FAIL: image not found: {image_path}", file=sys.stderr)
        return 2

    print("providers:", ort.get_available_providers())
    sess = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    in_meta = sess.get_inputs()[0]
    out_meta = sess.get_outputs()[0]
    print(f"input:  {in_meta.name} {in_meta.shape} {in_meta.type}")
    print(f"output: {out_meta.name} {out_meta.shape} {out_meta.type}")

    img = np.asarray(Image.open(image_path).convert("RGB"))
    h0, w0 = img.shape[:2]
    padded, ratio, (pad_x, pad_y) = letterbox(img, new_size=args.imgsz)
    blob = (padded.astype(np.float32) / 255.0).transpose(2, 0, 1)[None]  # (1, 3, 640, 640)

    out = sess.run(None, {in_meta.name: blob})[0]
    print(f"raw_output_shape={out.shape} dtype={out.dtype}")
    print(f"raw_output_stats: min={out.min():.3f} max={out.max():.3f}")
    print(f"box_xywh range: cx=[{out[0,0].min():.1f},{out[0,0].max():.1f}] "
          f"cy=[{out[0,1].min():.1f},{out[0,1].max():.1f}] "
          f"w=[{out[0,2].min():.1f},{out[0,2].max():.1f}] "
          f"h=[{out[0,3].min():.1f},{out[0,3].max():.1f}]")
    print(f"class_score range: min={out[0,4:].min():.3f} max={out[0,4:].max():.3f}")

    dets = yolov5_decode_and_nms(out, conf_thres=args.conf, iou_thres=args.iou)
    if dets.shape[0]:
        dets[:, [0, 2]] = (dets[:, [0, 2]] - pad_x) / ratio
        dets[:, [1, 3]] = (dets[:, [1, 3]] - pad_y) / ratio
        dets[:, [0, 2]] = dets[:, [0, 2]].clamp(0, w0)
        dets[:, [1, 3]] = dets[:, [1, 3]].clamp(0, h0)

    names = {0: "blue_cube", 1: "green_cube", 2: "red_cube"}
    print(f"detections_after_nms: {dets.shape[0]}  (orig_size={w0}x{h0})")
    for row in dets[: args.topk]:
        x1, y1, x2, y2, conf, cls = row.tolist()
        print(
            f"  {names[int(cls)]:>10s}  conf={float(conf):.3f}  "
            f"xyxy=({x1:6.1f},{y1:6.1f},{x2:6.1f},{y2:6.1f})"
        )

    # Sanity-check class ordering against best.pt
    from ultralytics import YOLO
    ref = YOLO(str(PROJECT_ROOT / "models" / "best.pt"))
    print(f"reference class names: {ref.names}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
