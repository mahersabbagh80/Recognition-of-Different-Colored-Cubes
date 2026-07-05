#!/usr/bin/env python3
"""Dev helper: summarise M4c1 tall_cyl YOLO + geometry-filter output.

Run from repo root:
    python3 scripts/dev_helpers/_summarize_tall_cyl.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YOLO = ROOT / "evaluation/m4c_geometry_filter/yolo_detections_tall_cyl.json"
FILT = ROOT / "evaluation/m4c_geometry_filter/filter_results_tall_cyl.json"


def main() -> None:
    y = json.load(YOLO.open())
    f = json.load(FILT.open())

    det_frames = y["frames"]
    filt_frames = f["frames"]
    print(f"=== {len(det_frames)} frames, conf_threshold={y['conf_threshold']} ===")
    print(f"YOLO latency (ms): min/med/max from y['yolo_latency_ms'] = {y['yolo_latency_ms']}")
    print(f"Filter latency (ms): {f['filter_latency_ms']}")

    all_dets = [d for fr in det_frames for d in fr["detections"]]
    all_filt = [d for fr in filt_frames for d in fr["detections"]]
    kept = [d for d in all_filt if d.get("verdict") == "KEEP"]
    print(f"\nyolo total dets: {len(all_dets)}")
    print(f"filter total: {len(all_filt)}  kept: {len(kept)}")
    if kept:
        print("KEPT samples (first 5):")
        for d in kept[:5]:
            print(f"  {d}")

    # per-class confidence distribution
    by_cls: dict[str, list[float]] = {}
    for d in all_dets:
        c = d.get("class", "?")
        by_cls.setdefault(c, []).append(d.get("confidence", 0.0))
    print("\n--- per-class YOLO conf distribution (all dets) ---")
    for c, lst in sorted(by_cls.items()):
        lst.sort()
        med = lst[len(lst) // 2]
        print(f"  {c:10s}  n={len(lst):3d}  min={lst[0]:.3f}  med={med:.3f}  max={lst[-1]:.3f}")

    # per-class kept
    kept_by_cls: Counter = Counter(d.get("class", "?") for d in kept)
    print(f"\n--- kept by class: {dict(kept_by_cls) if kept_by_cls else 'NONE (PASS)'}")

    # reject reasons (from per_class totals + per-frame counts)
    print(f"\n--- per_class (filter): {f['per_class']}")
    print(f"--- reject_reasons (filter): {f['reject_reasons']}")

    # bbox x-center histogram — separates cylinder (center) from cloth pile (right)
    print("\n--- bbox x-center histogram (all YOLO dets, image width=640) ---")
    buckets: Counter = Counter()
    for d in all_dets:
        bb = d["bbox_xyxy"]
        cx = (bb[0] + bb[2]) / 2.0
        buckets[int(cx // 80) * 80] += 1
    for k in sorted(buckets):
        print(f"  x in [{k:3d},{k + 80:3d}): {buckets[k]:3d}")

    # max conf on bbox-center falling on the deodorant (cx in [240, 400])
    print("\n--- max conf per class WITHIN cylinder x-range [240, 400] ---")
    on_cyl: dict[str, list[float]] = {}
    for d in all_dets:
        bb = d["bbox_xyxy"]
        cx = (bb[0] + bb[2]) / 2.0
        if 240 <= cx <= 400:
            on_cyl.setdefault(d["class"], []).append(d["confidence"])
    for c, lst in sorted(on_cyl.items()):
        lst.sort()
        med = lst[len(lst) // 2]
        print(f"  {c:10s}  n={len(lst):3d}  min={lst[0]:.3f}  med={med:.3f}  max={lst[-1]:.3f}")

    # per-frame detection counts
    print("\n--- per-frame YOLO det count distribution ---")
    counts = Counter(len(fr["detections"]) for fr in det_frames)
    for k in sorted(counts):
        print(f"  {k} dets/frame: {counts[k]} frames")


if __name__ == "__main__":
    main()
