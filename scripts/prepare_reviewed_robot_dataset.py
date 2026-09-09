#!/usr/bin/env python3
"""Export the human-confirmed robot subset with a fixed scene-group split.

This is a small, same-session development experiment, not an independent test.
Original images and human-review records remain unchanged.
"""

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evaluation/camera_samples/jetrover_positives_2026-07-08"
REVIEW = ROOT / "evaluation/robot_dataset_2026-09-09/human_review.json"
OUTPUT = ROOT / "evaluation/results/robot_training_2026-09-09"
MANIFEST = ROOT / "evaluation/robot_dataset_2026-09-09/development_split.json"
CLASSES = ["blue_cube", "green_cube", "red_cube"]
# Entire arrangements, including all unselected sibling frames, are reserved.
VALIDATION_GROUPS = {"dist40cm", "spread_out"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    review_bytes = REVIEW.read_bytes()
    reviewed = json.loads(review_bytes)["reviews"]
    if not reviewed:
        raise ValueError("No human-reviewed images")
    if OUTPUT.exists() or MANIFEST.exists():
        raise FileExistsError("Export already exists; review it before replacing it")
    seen_ids, seen_hashes = set(), set()
    records, staged = [], []
    counts = {split: Counter() for split in ("train", "val")}
    for item in sorted(reviewed, key=lambda r: r["image_id"]):
        if item["status"] != "confirmed" or item["reviewer"] != "Maher":
            raise ValueError("Every included image requires human confirmation")
        relative = Path(item["image_id"])
        source = (SOURCE / relative).resolve()
        if not source.is_relative_to(SOURCE.resolve()) or len(relative.parts) != 2:
            raise ValueError("Unexpected source path")
        raw = source.read_bytes()
        sha = digest(raw)
        if sha != item["sha256"]:
            raise ValueError(f"Source hash changed: {relative}")
        if str(relative) in seen_ids or sha in seen_hashes:
            raise ValueError("Duplicate image ID or exact image content")
        seen_ids.add(str(relative))
        seen_hashes.add(sha)
        with Image.open(source) as image:
            width, height = image.size
        group = relative.parts[0]
        split = "val" if group in VALIDATION_GROUPS else "train"
        lines = []
        for obj in item["objects"]:
            class_id = CLASSES.index(obj["class_name"])
            x1, y1, x2, y2 = obj["bbox_xyxy"]
            if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
                raise ValueError(f"Invalid box: {relative}")
            values = [(x1 + x2) / (2 * width), (y1 + y2) / (2 * height),
                      (x2 - x1) / width, (y2 - y1) / height]
            line = str(class_id) + " " + " ".join(f"{v:.10f}" for v in values)
            # Verify the written normalized representation reconstructs the box.
            cx, cy, w, h = map(float, line.split()[1:])
            decoded = [(cx-w/2)*width, (cy-h/2)*height,
                       (cx+w/2)*width, (cy+h/2)*height]
            if max(abs(a-b) for a, b in zip(decoded, [x1, y1, x2, y2])) > 0.00001:
                raise ValueError("Label coordinate round-trip failed")
            lines.append(line)
            counts[split][obj["class_name"]] += 1
        name = group + "__" + relative.name
        label = "\n".join(lines) + ("\n" if lines else "")
        record = {"image_id": str(relative), "group": group, "split": split,
                  "sha256": sha, "width": width, "height": height,
                  "image": f"images/{split}/{name}",
                  "label": f"labels/{split}/{Path(name).stem}.txt",
                  "objects": item["objects"], "reviewer": item["reviewer"]}
        records.append(record)
        staged.append((record, raw, label))
        counts[split]["images"] += 1
        counts[split]["background_images"] += not lines
    groups = {s: {r["group"] for r in records if r["split"] == s}
              for s in ("train", "val")}
    if groups["train"] & groups["val"] or groups["val"] != VALIDATION_GROUPS:
        raise ValueError("Invalid group allocation")
    if any(counts[s][c] == 0 for s in counts for c in CLASSES):
        raise ValueError("Both splits must contain all three classes")
    for record, raw, label in staged:
        image_path, label_path = OUTPUT / record["image"], OUTPUT / record["label"]
        image_path.parent.mkdir(parents=True, exist_ok=True)
        label_path.parent.mkdir(parents=True, exist_ok=True)
        image_path.write_bytes(raw)
        label_path.write_text(label)
        if digest(image_path.read_bytes()) != record["sha256"]:
            raise ValueError("Image copy verification failed")
    yaml = f"path: {json.dumps(str(OUTPUT))}\ntrain: images/train\nval: images/val\n"
    yaml += "names:\n" + "".join(f"  {i}: {name}\n" for i, name in enumerate(CLASSES))
    (OUTPUT / "data.yaml").write_text(yaml)
    manifest = {"purpose": "same-session development experiment; no independent test",
                "source_root": str(SOURCE), "output_root": str(OUTPUT),
                "review_sha256": digest(review_bytes), "classes": CLASSES,
                "validation_groups": sorted(VALIDATION_GROUPS),
                "group_rule": "All sibling frames of validation groups remain excluded from training, including unselected frames.",
                "limitations": ["Only two validation arrangements with two similar frames each",
                                "Shared room and capture session across splits",
                                "Validation has no background-only images",
                                "Not evidence for the final 80-percent completion target"],
                "counts": counts, "frames": records}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"counts": counts, "groups": {s: sorted(v) for s, v in groups.items()},
                      "output": str(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
