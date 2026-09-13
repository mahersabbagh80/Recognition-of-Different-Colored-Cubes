#!/usr/bin/env python3
"""One-shot helper to summarize cup YOLO + filter results for the report."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path("/home/maher/maher_ws/src/Recognition-of-Different-Colored-Cubes")
yolo = json.load(open(ROOT / "evaluation/m4c_geometry_filter/yolo_detections_cup.json"))
filt = json.load(open(ROOT / "evaluation/m4c_geometry_filter/filter_results_cup.json"))

print("=== YOLO ===")
print(f"frames: {yolo.get('num_frames')}")
print(f"conf_threshold: {yolo.get('conf_threshold')}")
per_class = Counter()
per_frame = []
for fr in yolo.get("frames", []):
    fc = Counter()
    for det in fr.get("detections", []):
        per_class[det["class"]] += 1
        fc[det["class"]] += 1
    per_frame.append(dict(fc))
print(f"total per class: {dict(per_class)}")
print(f"frames with red_cube: {sum(1 for c in per_frame if 'red_cube' in c)}")
print(f"red_cube total: {sum(c.get('red_cube', 0) for c in per_frame)}")
print()
print("frame 1 dets:")
for det in yolo["frames"][0]["detections"]:
    print(f"  {det['class']} conf={det['confidence']:.3f} bbox={det['bbox_xyxy']}")
print()
print("=== FILTER ===")
print(f"num_input_detections: {filt.get('num_input_detections')}")
print(f"num_kept: {filt.get('num_kept')}")
print(f"num_rejected: {filt.get('num_rejected')}")
print(f"reject_reasons: {filt.get('reject_reasons')}")
print(f"per_class: {json.dumps(filt.get('per_class'), indent=2)}")
print(f"latency_ms: {filt.get('filter_latency_ms')}")
print()
# Per-frame conf breakdown
conf_ranges = {"0.25-0.40": 0, "0.40-0.60": 0, "0.60-0.80": 0, "0.80-1.00": 0}
all_dets = []
for fr in yolo["frames"]:
    for det in fr["detections"]:
        c = det["confidence"]
        all_dets.append((det["class"], c, det["bbox_xyxy"]))
        if c < 0.40:
            conf_ranges["0.25-0.40"] += 1
        elif c < 0.60:
            conf_ranges["0.40-0.60"] += 1
        elif c < 0.80:
            conf_ranges["0.60-0.80"] += 1
        else:
            conf_ranges["0.80-1.00"] += 1
print(f"conf distribution: {conf_ranges}")
print()
# Highest conf det per class
print("highest conf det per class:")
top_per_cls = {}
for cls, c, b in all_dets:
    if cls not in top_per_cls or c > top_per_cls[cls][0]:
        top_per_cls[cls] = (c, b)
for cls, (c, b) in top_per_cls.items():
    print(f"  {cls}: conf={c:.3f} bbox={b}")