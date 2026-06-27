"""Build the hard-negative fine-tune dataset.

Approach (work-around for missing cube-removed distractor-only frames):
- Use cubes_2026-06-27_m4b (30 frames, cubes + distractors) AS POSITIVES
- Use empty_2026-06-27 (30 frames, also has cubes + distractors - dir mislabeled) AS POSITIVES
- Use Roboflow normalized (90 train + 9 valid) AS POSITIVES for domain retention
- Hard-negatives: CROPPED distractor regions from cubes-set frames
  (right portion with green bag + blue cardboard, top-left blue box,
   bottom-right blue decal) - the crop contains the saturated color
   but no actual cube.

Real cube bboxes (from visual inspection + M4b detections):
  red_cube:   (262, 193, 289, 231)  center (275, 212)  ~27x38
  green_cube: (288, 200, 320, 235)  center (304, 217)  ~32x35
  blue_cube:  (264, 228, 305, 270)  center (284, 249)  ~41x42

These positions are extremely stable across all 30 cubes-set frames
(camera doesn't move, cubes don't move). The same scene is captured
in empty_2026-06-27/.

Note: this approach uses 60 JetRover frames all showing the same scene.
A more diverse set would require new captures at different cube
arrangements. Documented as a known limitation.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROBOFLOW_DET = REPO / "data" / "roboflow_det" / "red-green-blue-cube-detection-1-yolov5pytorch"
CUBES_DIR = REPO / "evaluation" / "camera_samples" / "cubes_2026-06-27_m4b"
EMPTY_DIR = REPO / "evaluation" / "camera_samples" / "empty_2026-06-27"
OUT = REPO / "data" / "hardneg"

# Class indices for YOLO labels
CLASSES = {"blue_cube": 0, "green_cube": 1, "red_cube": 2}

# Cube bboxes (xyxy in 640x360 source) from visual inspection of m4b_0001.jpg
# and other frames. The 3 cubes are clustered at the center of the frame;
# positions are extremely stable across the 30 captures (camera stationary).
CUBE_BBOXES = {
    "red_cube":   (262, 195, 290, 232),  # back-left, 28x37 (confirmed by M4b det)
    "green_cube": (288, 202, 320, 238),  # back-right, 32x36 (estimated)
    "blue_cube":  (267, 232, 304, 268),  # front-center, 37x36 (estimated)
}

# Hard-negative crop regions (xyxy in 640x360 source) — these contain
# the saturated distractor objects but NO actual cube. They become
# background-only training images after cropping.
HARDNEG_CROPS = {
    "greenbag_only":     (380, 30, 580, 360),    # green soil bag only
    "cardboard_pkg":     (500, 30, 640, 230),    # blue cardboard package at top-right
    "topleft_box":       (0, 0, 110, 110),       # blue cardboard box at top-left
    "topright_corner":   (470, 0, 640, 90),      # empty floor at top-right
    "red_camera_mount":  (0, 130, 50, 270),      # camera mount (falsely detected as red)
}


def bbox_to_yolo(bbox: tuple[int, int, int, int], img_w: int, img_h: int) -> tuple[float, float, float, float]:
    """Convert xyxy to normalized cx, cy, w, h."""
    x1, y1, x2, y2 = bbox
    cx = ((x1 + x2) / 2) / img_w
    cy = ((y1 + y2) / 2) / img_h
    w = (x2 - x1) / img_w
    h = (y2 - y1) / img_h
    return cx, cy, w, h


def build_jetrover_positives(src_dir: Path, prefix: str, dst_img_dir: Path, dst_lbl_dir: Path) -> int:
    """Label the 3 cube bboxes in each JetRover frame."""
    count = 0
    for img_path in sorted(src_dir.glob("*.jpg")):
        dst_img = dst_img_dir / f"{prefix}_{img_path.stem}.jpg"
        shutil.copy2(img_path, dst_img)

        # Write labels for all 3 cubes
        lines = []
        for cls_name, bbox in CUBE_BBOXES.items():
            cx, cy, w, h = bbox_to_yolo(bbox, 640, 360)
            lines.append(f"{CLASSES[cls_name]} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
        dst_lbl = dst_lbl_dir / f"{prefix}_{img_path.stem}.txt"
        dst_lbl.write_text("\n".join(lines) + "\n")
        count += 1
    return count


def build_jetrover_hardneg_crops(src_dir: Path, dst_img_dir: Path, dst_lbl_dir: Path) -> int:
    """Crop distractor regions from JetRover frames; produce empty .txt labels."""
    from PIL import Image
    count = 0
    for img_path in sorted(src_dir.glob("*.jpg"))[:20]:  # use 20 source frames -> 20*4 crops = 80 hardneg images
        img = Image.open(img_path)
        for crop_name, bbox in HARDNEG_CROPS.items():
            x1, y1, x2, y2 = bbox
            crop = img.crop((x1, y1, x2, y2))
            stem = f"crop_{img_path.stem}_{crop_name}"
            dst_img = dst_img_dir / f"{stem}.jpg"
            crop.save(dst_img, "JPEG", quality=92)
            # Empty label = background-only training signal
            (dst_lbl_dir / f"{stem}.txt").write_text("")
            count += 1
    return count


def build_roboflow(src_split: str, src_dir: Path, dst_img_dir: Path, dst_lbl_dir: Path) -> int:
    """Copy Roboflow split (train or valid) into the merged dataset."""
    src_img_dir = src_dir / src_split / "images"
    src_lbl_dir = src_dir / src_split / "labels"
    count = 0
    for img_path in sorted(src_img_dir.glob("*.jpg")):
        dst_img = dst_img_dir / f"rf_{img_path.name}"
        shutil.copy2(img_path, dst_img)
        # Copy matching label file if it exists
        lbl = src_lbl_dir / f"{img_path.stem}.txt"
        dst_lbl = dst_lbl_dir / f"rf_{img_path.stem}.txt"
        if lbl.exists():
            shutil.copy2(lbl, dst_lbl)
        else:
            dst_lbl.write_text("")
        count += 1
    return count


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    if OUT.exists():
        if not args.force:
            print(f"ERROR: {OUT} exists; pass --force to overwrite", file=sys.stderr)
            return 2
        shutil.rmtree(OUT)

    img_train = OUT / "images" / "train"
    lbl_train = OUT / "labels" / "train"
    img_val = OUT / "images" / "val"
    lbl_val = OUT / "labels" / "val"
    for d in (img_train, lbl_train, img_val, lbl_val):
        d.mkdir(parents=True, exist_ok=True)

    print("=== Building hard-negative dataset ===")
    print(f"Output: {OUT}")
    print()

    # 1) Roboflow positives (train) + valid for held-out sanity
    n_rf_train = build_roboflow("train", ROBOFLOW_DET, img_train, lbl_train)
    n_rf_valid = build_roboflow("valid", ROBOFLOW_DET, img_val, lbl_val)
    print(f"Roboflow train: {n_rf_train} images -> train/")
    print(f"Roboflow valid: {n_rf_valid} images -> val/")

    # 2) JetRover positives (cubes + distractors together)
    n_cubes = build_jetrover_positives(CUBES_DIR, "cubes", img_train, lbl_train)
    n_empty = build_jetrover_positives(EMPTY_DIR, "empty", img_train, lbl_train)
    print(f"JetRover cube frames: {n_cubes} -> train/")
    print(f"JetRover 'empty' frames: {n_empty} -> train/")

    # 3) JetRover hard-negatives (cropped distractor regions, empty labels)
    n_hardneg = build_jetrover_hardneg_crops(CUBES_DIR, img_train, lbl_train)
    print(f"JetRover hard-neg crops: {n_hardneg} -> train/ (empty labels)")

    # 4) data.yaml
    data_yaml = OUT / "data.yaml"
    data_yaml.write_text(
        "# M3c hard-negative fine-tune dataset (work-around)\n"
        "# Source frames: evaluation/camera_samples/cubes_2026-06-27_m4b/\n"
        "#                evaluation/camera_samples/empty_2026-06-27/\n"
        "#                data/roboflow_det/red-green-blue-cube-detection-1-yolov5pytorch/\n"
        "# Composition:\n"
        f"#   Roboflow train positives: {n_rf_train}\n"
        f"#   Roboflow valid: {n_rf_valid}\n"
        f"#   JetRover cube frames (cubes + distractors, cubes labeled): {n_cubes}\n"
        f"#   JetRover 'empty' frames (mislabeled - also has cubes, cubes labeled): {n_empty}\n"
        f"#   JetRover hard-neg crops (distractor only, empty labels): {n_hardneg}\n"
        "# Caveat: all 60 JetRover frames show the SAME physical scene (stationary\n"
        "# camera, stationary cubes, stationary distractors). Real diversity requires\n"
        "# a fresh capture session.\n"
        "train: ../images/train\n"
        "val: ../images/val\n"
        "test: ../images/val\n"
        "\n"
        "nc: 3\n"
        "names: ['blue_cube', 'green_cube', 'red_cube']\n"
    )
    print(f"\ndata.yaml: {data_yaml}")

    total_train = n_rf_train + n_cubes + n_empty + n_hardneg
    total_val = n_rf_valid
    print(f"\nTotals: train={total_train}, val={total_val}")
    print(f"  positives: {n_rf_train + n_rf_valid + n_cubes + n_empty} (with cube bboxes)")
    print(f"  hardneg (empty labels): {n_hardneg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
