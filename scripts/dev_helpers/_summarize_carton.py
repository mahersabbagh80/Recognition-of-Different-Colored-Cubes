#!/usr/bin/env python3
"""One-shot helper to summarize carton YOLO + filter results for the report."""
import json
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path("/home/maher/maher_ws/src/Recognition-of-Different-Colored-Cubes")
yolo = json.load(open(ROOT / "evaluation/m4c_geometry_filter/yolo_detections_carton.json"))
filt = json.load(open(ROOT / "evaluation/m4c_geometry_filter/filter_results_carton.json"))

total_dets = sum(len(f.get("detections", [])) for f in yolo["frames"])
print(f"YOLO: {yolo['num_frames']} frames, conf={yolo['conf_threshold']}, total_dets={total_dets}")
print(f"FILTER: kept={filt['num_kept']} rejected={filt['num_rejected']} reasons={filt['reject_reasons']}")
print(f"per_class: {json.dumps(filt['per_class'], indent=2)}")
print(f"filter latency ms: {filt.get('filter_latency_ms')}")

per_class = Counter()
conf = {"blue": [], "green": [], "red": []}
for fr in yolo["frames"]:
    for d in fr["detections"]:
        per_class[d["class"]] += 1
        conf[d["class"].replace("_cube", "")].append(d["confidence"])

print(f"yolo counts: {dict(per_class)}")
for k, v in conf.items():
    if v:
        print(f"  {k}_cube conf: min={min(v):.3f} med={statistics.median(v):.3f} max={max(v):.3f} n={len(v)}")

print("\nFrame 1 dets (xyxy):")
for d in yolo["frames"][0]["detections"]:
    print(f"  {d['class']} conf={d['confidence']:.3f} bbox={d['bbox_xyxy']}")

print("\nHighest conf per class:")
top_per_cls = {}
for fr in yolo["frames"]:
    for d in fr["detections"]:
        c = d["class"]
        if c not in top_per_cls or d["confidence"] > top_per_cls[c][0]:
            top_per_cls[c] = (d["confidence"], d["bbox_xyxy"])
for cls, (c, b) in top_per_cls.items():
    print(f"  {cls}: conf={c:.3f} bbox={b}")