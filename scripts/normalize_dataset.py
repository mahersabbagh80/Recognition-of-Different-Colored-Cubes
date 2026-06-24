"""M2 dataset normalization: convert Roboflow YOLOv5 *segmentation* export
(many of the labels are polygons with >5 fields) to a strict YOLOv5
*object-detection* dataset (5 fields per line: class cx cy w h, normalized).

Reads from:  data/roboflow/red-green-blue-cube-detection-1-yolov5pytorch/
Writes to:   data/roboflow_det/red-green-blue-cube-detection-1-yolov5pytorch/

Also rewrites data.yaml to:
- point at the new split dirs,
- rename classes to project-canonical names: blue_cube, green_cube, red_cube
  (source had 'bluecube', 'green cube', 'red cube').

Polygon -> axis-aligned bbox:
    cx = (min(x) + max(x)) / 2
    cy = (min(y) + max(y)) / 2
    w  = max(x) - min(x)
    h  = max(y) - min(y)
All values clipped to [0, 1].
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "data" / "roboflow" / "red-green-blue-cube-detection-1-yolov5pytorch"
DST = REPO / "data" / "roboflow_det" / "red-green-blue-cube-detection-1-yolov5pytorch"

# Source class order from data.yaml:
#   0: 'bluecube', 1: 'green cube', 2: 'red cube'
# Project-canonical names per .cursorrules + model-options.md:
NAME_MAP = {
    0: "blue_cube",
    1: "green_cube",
    2: "red_cube",
}


def convert_label_line(line: str) -> tuple[str, str] | None:
    """Return (new_line, kind) where kind is 'det' or 'poly' (or None on bad line)."""
    parts = line.strip().split()
    if not parts:
        return None
    try:
        cls = int(parts[0])
    except ValueError:
        return None
    nums = [float(x) for x in parts[1:]]
    if len(nums) < 4:
        return None  # cannot form a bbox
    if len(nums) == 4:
        # already cx, cy, w, h (YOLOv5 detection)
        cx, cy, w, h = nums
        kind = "det"
    elif len(nums) % 2 == 0:
        # polygon: x1, y1, x2, y2, ...
        xs = nums[0::2]
        ys = nums[1::2]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        cx = (minx + maxx) / 2.0
        cy = (miny + maxy) / 2.0
        w = maxx - minx
        h = maxy - miny
        kind = "poly"
    else:
        return None  # odd field count, malformed
    # clip to [0, 1]
    cx = min(1.0, max(0.0, cx))
    cy = min(1.0, max(0.0, cy))
    w = min(1.0, max(0.0, w))
    h = min(1.0, max(0.0, h))
    return f"{cls} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}", kind


def convert_split(split: str, stats: dict) -> None:
    src_lbl = SRC / split / "labels"
    src_img = SRC / split / "images"
    dst_lbl = DST / split / "labels"
    dst_img = DST / split / "images"
    dst_lbl.mkdir(parents=True, exist_ok=True)
    dst_img.mkdir(parents=True, exist_ok=True)
    if not src_lbl.is_dir():
        print(f"[skip] missing {src_lbl}", file=sys.stderr)
        return
    label_files = sorted(src_lbl.glob("*.txt"))
    for lbl in label_files:
        new_lines: list[str] = []
        kinds: list[str] = []
        with lbl.open() as f:
            for line in f:
                out = convert_label_line(line)
                if out is None:
                    continue  # drop malformed line
                new_line, kind = out
                new_lines.append(new_line)
                kinds.append(kind)
        (dst_lbl / lbl.name).write_text(("\n".join(new_lines) + "\n") if new_lines else "")
        kind_for_count: str = kinds[0] if kinds else "none"
        stats["labels"][kind_for_count] = stats["labels"].get(kind_for_count, 0) + 1
        if not kinds:
            stats["empty_labels"] += 1
    # copy images (file copy is fastest; symlinks break portability across filesystems)
    for img in src_img.iterdir():
        target = dst_img / img.name
        if not target.exists():
            shutil.copy2(img, target)
    print(f"  {split}: {len(label_files)} label files -> {dst_lbl}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="overwrite existing destination")
    args = parser.parse_args()
    if not SRC.is_dir():
        print(f"ERROR: source dataset not found at {SRC}", file=sys.stderr)
        return 2
    if DST.exists() and not args.force:
        print(f"ERROR: destination {DST} already exists; pass --force to overwrite", file=sys.stderr)
        return 2
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True)

    stats = {
        "labels": {"det": 0, "poly": 0, "none": 0},
        "empty_labels": 0,
    }
    for split in ("train", "valid", "test"):
        convert_split(split, stats)
    # also carry README files for traceability
    for name in ("README.dataset.txt", "README.roboflow.txt"):
        src = SRC / name
        if src.exists():
            shutil.copy2(src, DST / name)

    # write new data.yaml with normalized class names
    (DST / "data.yaml").write_text(
        "# Normalized M2 dataset (YOLOv5 detection format)\n"
        f"# Source: {SRC}\n"
        f"# Polygons (>{4} fields) converted to axis-aligned bounding boxes.\n"
        f"# Source class names: ['bluecube', 'green cube', 'red cube']\n"
        f"# Project-canonical class names: ['blue_cube', 'green_cube', 'red_cube']\n"
        "train: ../train/images\n"
        "val: ../valid/images\n"
        "test: ../test/images\n"
        "\n"
        f"nc: 3\n"
        f"names: ['{NAME_MAP[0]}', '{NAME_MAP[1]}', '{NAME_MAP[2]}']\n"
    )
    print(f"\nNormalized dataset written to: {DST}")
    print(f"Stats: {stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
