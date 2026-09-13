"""M3c post-fine-tune validation: run models/best_hardneg.pt on saved frames.

Compares predictions to the M4b detections.json (which used the original
models/best.pt) and produces a before/after FP table.

Runs on the dev PC (CPU is fine for PyTorch inference at small batch).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[3]
CLASS_NAMES = ["blue_cube", "green_cube", "red_cube"]
CLASS_COLORS = {
    "blue_cube": (66, 133, 244),
    "green_cube": (52, 168, 83),
    "red_cube": (234, 67, 53),
}


def letterbox(im: np.ndarray, new_shape: int = 640):
    h0, w0 = im.shape[:2]
    r = min(new_shape / h0, new_shape / w0)
    new_w, new_h = int(round(w0 * r)), int(round(h0 * r))
    pad_w, pad_h = new_shape - new_w, new_shape - new_h
    pad_l, pad_t = pad_w // 2, pad_h // 2
    pad_r, pad_b = pad_w - pad_l, pad_h - pad_t
    img = np.array(Image.fromarray(im).resize((new_w, new_h), 1))  # 1 = bilinear
    img = np.pad(img, ((pad_t, pad_b), (pad_l, pad_r), (0, 0)),
                 mode="constant", constant_values=114)
    return img, r, (pad_l, pad_t)


def annotate(pil_img, detections, conf_thres, title=""):
    out = pil_img.copy()
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
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
    draw.text((4, 2), title, fill=(255, 255, 255), font=font)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True, type=Path)
    p.add_argument("--input-dir", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou", type=float, default=0.45)
    p.add_argument("--annotate", action="store_true")
    args = p.parse_args()

    if not args.weights.exists():
        raise SystemExit(f"weights not found: {args.weights}")
    if not args.input_dir.exists():
        raise SystemExit(f"input dir not found: {args.input_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[m3c-val] weights: {args.weights}")
    print(f"[m3c-val] input: {args.input_dir}")
    print(f"[m3c-val] output: {args.output_dir}")
    print(f"[m3c-val] conf={args.conf}  iou={args.iou}")

    from ultralytics import YOLO
    model = YOLO(str(args.weights))

    images = sorted(p for p in args.input_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not images:
        raise SystemExit(f"no images in {args.input_dir}")

    results = []
    class_frame_hits = {c: 0 for c in CLASS_NAMES}
    class_total = {c: 0 for c in CLASS_NAMES}

    for img_path in images:
        results_obj = model.predict(
            str(img_path), imgsz=args.imgsz, conf=args.conf, iou=args.iou,
            verbose=False,
        )[0]

        dets = []
        for b in results_obj.boxes:
            cls_id = int(b.cls.item())
            conf = float(b.conf.item())
            xyxy = [float(v) for v in b.xyxy[0].tolist()]
            name = CLASS_NAMES[cls_id]
            dets.append((name, conf, xyxy))
            class_frame_hits[name] += 1
            class_total[name] += 1

        results.append({
            "filename": img_path.name,
            "num_detections": len(dets),
            "detections": [
                {"class": n, "confidence": c, "bbox_xyxy": b}
                for n, c, b in dets
            ],
        })

        print(f"  {img_path.name:18s}  n={len(dets):2d}  " + "  ".join(
            f"{n.split('_')[0]}:{c:.2f}" for n, c, _ in dets
        ))

        if args.annotate:
            pil = Image.open(img_path).convert("RGB")
            ann = annotate(pil, dets, args.conf,
                           title=f"PyTorch | conf>={args.conf:.2f} | dets={len(dets)}")
            ann.save(args.output_dir / f"{img_path.stem}_pred.png", "PNG")

    summary = {
        "weights": str(args.weights),
        "input_dir": str(args.input_dir),
        "output_dir": str(args.output_dir),
        "conf_threshold": args.conf,
        "iou_threshold": args.iou,
        "num_frames": len(images),
        "per_class_frame_hits": class_frame_hits,
        "per_class_total_detections": class_total,
        "frames": results,
    }
    out_json = args.output_dir / "detections.json"
    out_json.write_text(json.dumps(summary, indent=2))
    print(f"\n[m3c-val] wrote {out_json}")
    print(f"[m3c-val] per-class frame-hit rate:")
    for c in CLASS_NAMES:
        rate = class_total[c] / len(images) * 100
        print(f"        {c:11s}  hits={class_total[c]:3d}  rate={rate:5.1f}%")
    print(f"[m3c-val] total detections: {sum(class_total.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
