"""M3c fine-tune: continue from models/best.pt with hard-negative-augmented data.

Recipe (per M3c plan §6 with adaptations for the actual data we have):
- Base: models/best.pt (continue from M2 artifact, not COCO)
- Data: data/hardneg/data.yaml (merged Roboflow + JetRover + hard-neg crops)
- Epochs: 25 (fine-tune, not from scratch)
- Imgsz: 640
- Batch: 16
- LR: 0.0005 (10x lower than M2 to preserve features)
- Optimizer: AdamW (auto)
- Scheduler: cosine, close_mosaic=10
- Patience: 15
- Augmentation: mosaic=1.0, mixup=0.15, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
                degrees=10, translate=0.1, scale=0.5, fliplr=0.5
- Seed: 42
- Project: runs/m3c, name: m3c_25ep
- exist_ok: True

Output: runs/m3c/m3c_25ep/weights/best.pt -> copy to models/best_hardneg.pt
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--epochs", type=int, default=25)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--lr0", type=float, default=0.0005)
    p.add_argument("--device", default="0")
    p.add_argument("--name", default="m3c_25ep")
    p.add_argument("--data", default=str(REPO / "data" / "hardneg" / "data.yaml"))
    p.add_argument("--base", default=str(REPO / "models" / "best.pt"))
    p.add_argument("--out", default=str(REPO / "models" / "best_hardneg.pt"))
    p.add_argument("--patience", type=int, default=15)
    args = p.parse_args()

    print(f"[m3c] base: {args.base}")
    print(f"[m3c] data: {args.data}")
    print(f"[m3c] epochs: {args.epochs}, batch: {args.batch}, imgsz: {args.imgsz}, lr0: {args.lr0}")
    print(f"[m3c] device: {args.device}, name: {args.name}")
    print(f"[m3c] output: {args.out}")

    # Run the Ultralytics training
    from ultralytics import YOLO

    model = YOLO(args.base)
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        lr0=args.lr0,
        optimizer="AdamW",
        cos_lr=True,
        close_mosaic=10,
        patience=args.patience,
        seed=42,
        project=str(REPO / "runs" / "m3c"),
        name=args.name,
        exist_ok=True,
        plots=True,
        save_period=-1,
        cache=False,
        workers=8,
        amp=True,
        # Heavy augmentation per M3c plan §6
        mosaic=1.0,
        mixup=0.15,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10,
        translate=0.1,
        scale=0.5,
        fliplr=0.5,
        verbose=True,
    )
    print(f"[m3c] training done: {results}")

    # Copy best.pt to models/best_hardneg.pt
    src_best = REPO / "runs" / "m3c" / args.name / "weights" / "best.pt"
    if not src_best.exists():
        print(f"ERROR: {src_best} not found", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_best, out)
    size = out.stat().st_size
    import hashlib
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"[m3c] copied to {out}")
    print(f"[m3c] size: {size} bytes ({size / 1024 / 1024:.1f} MB)")
    print(f"[m3c] sha256: {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
