#!/usr/bin/env python3
"""Export human-confirmed robot images and boxes as a YOLO dataset.

The historical defaults reproduce the 9 September input selection. New review
records may provide ``source_file`` and ``split`` per image. Use ``--check-only``
to run every input and conversion check without writing the export.
"""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "evaluation/camera_samples/jetrover_positives_2026-07-08"
DEFAULT_REVIEW = ROOT / "evaluation/robot_dataset_2026-09-09/human_review.json"
DEFAULT_OUTPUT = ROOT / "evaluation/results/robot_training_2026-09-09"
DEFAULT_MANIFEST = ROOT / "evaluation/robot_dataset_2026-09-09/development_split.json"
DEFAULT_VALIDATION_GROUPS = {"dist40cm", "spread_out"}
CLASSES = ["blue_cube", "green_cube", "red_cube"]
SPLIT_NAMES = {"train": "train", "training": "train", "val": "val", "validation": "val"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def project_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=project_path, default=DEFAULT_REVIEW)
    parser.add_argument("--source", type=project_path, default=DEFAULT_SOURCE,
                        help="Legacy source root when review entries have only image_id")
    parser.add_argument("--output", type=project_path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=project_path, default=DEFAULT_MANIFEST)
    parser.add_argument("--base-training-dataset", type=project_path,
                        help="Existing reviewed YOLO dataset whose train pairs are retained")
    parser.add_argument("--base-manifest", type=project_path,
                        help="Manifest proving the base dataset's review and source hashes")
    parser.add_argument("--check-only", action="store_true",
                        help="Validate and stage in memory without writing files")
    return parser.parse_args()


def normalized_split(item: dict, group: str) -> str:
    declared = item.get("split")
    if declared is None:
        return "val" if group in DEFAULT_VALIDATION_GROUPS else "train"
    try:
        return SPLIT_NAMES[declared]
    except KeyError as error:
        raise ValueError(f"Unknown split {declared!r} for {item['image_id']}") from error


def source_path(item: dict, legacy_source: Path) -> Path:
    if "source_file" in item:
        source = project_path(item["source_file"])
        if not source.is_relative_to(ROOT.resolve()):
            raise ValueError(f"Source file is outside the project: {source}")
        return source
    relative = Path(item["image_id"])
    source = (legacy_source / relative).resolve()
    if not source.is_relative_to(legacy_source.resolve()):
        raise ValueError(f"Unexpected source path: {relative}")
    return source


def yolo_label(objects: list, width: int, height: int, image_id: str) -> str:
    lines = []
    for obj in objects:
        try:
            class_id = CLASSES.index(obj["class_name"])
        except ValueError as error:
            raise ValueError(f"Unknown class in {image_id}: {obj['class_name']}") from error
        x1, y1, x2, y2 = obj["bbox_xyxy"]
        if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
            raise ValueError(f"Invalid box: {image_id}")
        values = [(x1 + x2) / (2 * width), (y1 + y2) / (2 * height),
                  (x2 - x1) / width, (y2 - y1) / height]
        line = str(class_id) + " " + " ".join(f"{value:.10f}" for value in values)
        cx, cy, box_width, box_height = map(float, line.split()[1:])
        decoded = [(cx-box_width/2)*width, (cy-box_height/2)*height,
                   (cx+box_width/2)*width, (cy+box_height/2)*height]
        if max(abs(actual-expected) for actual, expected in
               zip(decoded, [x1, y1, x2, y2])) > 0.00001:
            raise ValueError("Label coordinate round-trip failed")
        lines.append(line)
    return "\n".join(lines) + ("\n" if lines else "")


def main() -> None:
    args = parse_args()
    if bool(args.base_training_dataset) != bool(args.base_manifest):
        raise ValueError("--base-training-dataset and --base-manifest must be used together")
    review_bytes = args.review.read_bytes()
    review_payload = json.loads(review_bytes)
    reviewed = review_payload.get("images", review_payload.get("reviews"))
    if not reviewed:
        raise ValueError("No human-reviewed images")
    if not args.check_only and (args.output.exists() or args.manifest.exists()):
        raise FileExistsError("Export already exists; review it before replacing it")

    default_reviewer = review_payload.get("reviewer")
    seen_ids, seen_hashes = set(), set()
    records, staged = [], []
    counts = {split: Counter() for split in ("train", "val")}

    base_manifest_bytes = b""
    if args.base_training_dataset:
        base_manifest_bytes = args.base_manifest.read_bytes()
        base_payload = json.loads(base_manifest_bytes)
        manifest_by_name = {}
        for frame in base_payload["frames"]:
            name = Path(frame["image"]).name
            if name in manifest_by_name:
                raise ValueError(f"Duplicate output name in base manifest: {name}")
            manifest_by_name[name] = frame
        base_images = sorted((args.base_training_dataset / "images/train").glob("*.jpg"))
        base_labels = sorted((args.base_training_dataset / "labels/train").glob("*.txt"))
        if not base_images or {path.stem for path in base_images} != {path.stem for path in base_labels}:
            raise ValueError("Base training image and label files are missing or unmatched")
        for image_path in base_images:
            try:
                frame = manifest_by_name[image_path.name]
            except KeyError as error:
                raise ValueError(f"Base image lacks a manifest record: {image_path.name}") from error
            raw = image_path.read_bytes()
            sha = digest(raw)
            if sha != frame["sha256"]:
                raise ValueError(f"Base image hash changed: {image_path.name}")
            if frame["image_id"] in seen_ids or sha in seen_hashes:
                raise ValueError("Duplicate image ID or exact image content")
            seen_ids.add(frame["image_id"])
            seen_hashes.add(sha)
            with Image.open(image_path) as image:
                width, height = image.size
            expected_label = yolo_label(frame["objects"], width, height, frame["image_id"])
            label_path = args.base_training_dataset / "labels/train" / f"{image_path.stem}.txt"
            if label_path.read_text() != expected_label:
                raise ValueError(f"Base label differs from approved boxes: {label_path.name}")
            group = frame["group"]
            record = {
                "image_id": frame["image_id"], "group": group, "split": "train",
                "source_file": str(image_path.resolve()), "sha256": sha,
                "width": width, "height": height,
                "image": f"images/train/{image_path.name}",
                "label": f"labels/train/{label_path.name}",
                "objects": frame["objects"], "reviewer": frame["reviewer"],
                "origin": "retained_base_training_dataset",
            }
            records.append(record)
            staged.append((record, raw, expected_label))
            counts["train"]["images"] += 1
            counts["train"]["background_images"] += not frame["objects"]
            for obj in frame["objects"]:
                counts["train"][obj["class_name"]] += 1

    for item in sorted(reviewed, key=lambda record: record["image_id"]):
        reviewer = item.get("reviewer", default_reviewer)
        if item["status"] != "confirmed" or reviewer != "Maher":
            raise ValueError("Every included image requires Maher's confirmation")

        source = source_path(item, args.source)
        raw = source.read_bytes()
        sha = digest(raw)
        if sha != item["sha256"]:
            raise ValueError(f"Source hash changed: {item['image_id']}")
        if item["image_id"] in seen_ids or sha in seen_hashes:
            raise ValueError("Duplicate image ID or exact image content")
        seen_ids.add(item["image_id"])
        seen_hashes.add(sha)

        with Image.open(source) as image:
            width, height = image.size
        if "width" in item and (item["width"], item["height"]) != (width, height):
            raise ValueError(f"Recorded dimensions changed: {item['image_id']}")

        group = item.get("group", item["image_id"].split("/", 1)[0])
        split = normalized_split(item, group)
        label = yolo_label(item["objects"], width, height, item["image_id"])
        for obj in item["objects"]:
            counts[split][obj["class_name"]] += 1

        output_name = group + "__" + source.name
        record = {
            "image_id": item["image_id"], "group": group, "split": split,
            "source_file": str(source), "sha256": sha, "width": width, "height": height,
            "image": f"images/{split}/{output_name}",
            "label": f"labels/{split}/{Path(output_name).stem}.txt",
            "objects": item["objects"], "reviewer": reviewer,
        }
        records.append(record)
        staged.append((record, raw, label))
        counts[split]["images"] += 1
        counts[split]["background_images"] += not item["objects"]

    groups = {split: {record["group"] for record in records if record["split"] == split}
              for split in ("train", "val")}
    if groups["train"] & groups["val"]:
        raise ValueError("A group cannot appear in both training and validation")
    if any(counts[split][class_name] == 0 for split in counts for class_name in CLASSES):
        raise ValueError("Both splits must contain all three classes")

    summary = {
        "mode": "check-only" if args.check_only else "export",
        "review": str(args.review), "output": str(args.output),
        "manifest": str(args.manifest), "counts": counts,
        "base_training_dataset": (str(args.base_training_dataset)
                                  if args.base_training_dataset else None),
        "groups": {split: sorted(values) for split, values in groups.items()},
    }
    if args.check_only:
        print(json.dumps(summary, indent=2))
        return

    for record, raw, label in staged:
        image_path = args.output / record["image"]
        label_path = args.output / record["label"]
        image_path.parent.mkdir(parents=True, exist_ok=True)
        label_path.parent.mkdir(parents=True, exist_ok=True)
        image_path.write_bytes(raw)
        label_path.write_text(label)
        if digest(image_path.read_bytes()) != record["sha256"]:
            raise ValueError("Image copy verification failed")

    yaml = f"path: {json.dumps(str(args.output))}\ntrain: images/train\nval: images/val\n"
    yaml += "names:\n" + "".join(f"  {index}: {name}\n"
                                   for index, name in enumerate(CLASSES))
    (args.output / "data.yaml").write_text(yaml)
    manifest = {
        "purpose": review_payload.get("purpose", "human-confirmed YOLO dataset export"),
        "review": str(args.review), "output_root": str(args.output),
        "review_sha256": digest(review_bytes), "classes": CLASSES,
        "base_training_dataset": (str(args.base_training_dataset)
                                  if args.base_training_dataset else None),
        "base_manifest": str(args.base_manifest) if args.base_manifest else None,
        "base_manifest_sha256": digest(base_manifest_bytes) if base_manifest_bytes else None,
        "split_rule": "Use each review entry's declared split; legacy records use fixed validation groups.",
        "counts": counts, "frames": records,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
