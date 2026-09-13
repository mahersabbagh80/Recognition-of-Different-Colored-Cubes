#!/usr/bin/env python3
"""Dev helper: dump the JSON schema of the M4c1 tall_cyl outputs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for name in ("yolo_detections_tall_cyl.json", "filter_results_tall_cyl.json"):
    p = ROOT / "evaluation/m4c_geometry_filter" / name
    j = json.load(p.open())
    print(f"=== {name} ===")
    print("top keys:", list(j.keys()))
    if "frames" in j:
        fr = j["frames"][0]
        print("frame keys:", list(fr.keys()))
        if fr.get("detections"):
            d = fr["detections"][0]
            print("det sample:", d)
    print()
