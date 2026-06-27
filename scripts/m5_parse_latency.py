#!/usr/bin/env python3
"""Parse cube_detection_node latency lines from a node.log into structured JSON.

The node emits one line every 100 frames:
  latency over last 100 frames  total ms: median=60.2  p95=64.0  yolo ms: median=26.6  p95=26.9  filter ms/frame: median=1.39  sync=100  publishes=100  rejects={'flat': 96, ...}

We parse them all and produce per-bucket p50/p95 statistics.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter
import statistics

# regex pulls out: total_ms_med p95 yolo_ms_med p95 filter_ms_med sync publishes rejects_dict
PATTERN = re.compile(
    r"latency over last (?P<n>\d+) frames\s+"
    r"total ms: median=(?P<tot_med>[\d.]+)\s+p95=(?P<tot_p95>[\d.]+)\s+"
    r"yolo ms: median=(?P<yolo_med>[\d.]+)\s+p95=(?P<yolo_p95>[\d.]+)\s+"
    r"filter ms/frame: median=(?P<filt_med>[\d.]+)\s+"
    r"sync=(?P<sync>\d+)\s+publishes=(?P<pubs>\d+)\s+"
    r"rejects=(?P<rej>\{[^}]*\})"
)


def parse_log(path: Path) -> dict:
    samples = []
    for line in path.read_text().splitlines():
        m = PATTERN.search(line)
        if not m:
            continue
        g = m.groupdict()
        try:
            rej_str = g["rej"].replace("'", '"')
            rej = json.loads(rej_str)
        except Exception:
            rej = {}
        samples.append({
            "n": int(g["n"]),
            "total_ms_median": float(g["tot_med"]),
            "total_ms_p95": float(g["tot_p95"]),
            "yolo_ms_median": float(g["yolo_med"]),
            "yolo_ms_p95": float(g["yolo_p95"]),
            "filter_ms_median": float(g["filt_med"]),
            "sync": int(g["sync"]),
            "publishes": int(g["pubs"]),
            "rejects": rej,
        })

    if not samples:
        return {"error": "no latency lines parsed"}

    totals = [s["total_ms_median"] for s in samples]
    yolos = [s["yolo_ms_median"] for s in samples]
    filts = [s["filter_ms_median"] for s in samples]
    total_pubs = sum(s["publishes"] for s in samples)
    total_sync = sum(s["sync"] for s in samples)
    rej_total = Counter()
    for s in samples:
        for k, v in s["rejects"].items():
            rej_total[k] += int(v)

    return {
        "log_path": str(path),
        "num_summary_lines": len(samples),
        "total_publishes_observed": total_pubs,
        "total_sync_observed": total_sync,
        "totals": {
            "p50_total_ms": round(statistics.median(totals), 3),
            "p95_total_ms": round(sorted(totals)[int(0.95 * len(totals))], 3),
            "max_total_ms": round(max(totals), 3),
        },
        "yolo": {
            "p50_yolo_ms": round(statistics.median(yolos), 3),
            "p95_yolo_ms": round(sorted(yolos)[int(0.95 * len(yolos))], 3),
            "max_yolo_ms": round(max(yolos), 3),
        },
        "filter": {
            "p50_filter_ms_per_frame": round(statistics.median(filts), 3),
            "max_filter_ms_per_frame": round(max(filts), 3),
        },
        "rejects_total": dict(rej_total),
        "samples": samples,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--log", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    parsed = parse_log(args.log)
    args.out.write_text(json.dumps(parsed, indent=2))
    print(f"[latency] wrote {args.out}")
    print(f"[latency] {parsed.get('num_summary_lines', 0)} summary lines, "
          f"{parsed.get('total_publishes_observed', 0)} publishes")
    if "totals" in parsed:
        print(f"  total ms: p50={parsed['totals']['p50_total_ms']} "
              f"p95={parsed['totals']['p95_total_ms']} max={parsed['totals']['max_total_ms']}")
        print(f"  yolo  ms: p50={parsed['yolo']['p50_yolo_ms']} "
              f"p95={parsed['yolo']['p95_yolo_ms']} max={parsed['yolo']['max_yolo_ms']}")
        print(f"  filter ms/frame: p50={parsed['filter']['p50_filter_ms_per_frame']} "
              f"max={parsed['filter']['max_filter_ms_per_frame']}")
        print(f"  rejects: {parsed['rejects_total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
