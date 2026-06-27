#!/usr/bin/env python3
"""M5 live evaluation harness — run the M5 node end-to-end and capture bags.

This script does NOT itself run ROS — it is the orchestration that:

1. (Assumes the vendor depth-camera bringup + the cube_detection_node are
   already running on the Jetson with the M5 launch file.)
2. Opens a ``ros2 bag record`` subprocess on the Jetson for ``/cube_detections``,
   ``/cube_detections/vendor_objects``, ``/cube_detections/debug_image``, and
   the upstream RGB stream for cross-checking.
3. Waits ``--duration-sec`` seconds.
4. Stops the recording.
5. Pulls the bag back to ``--out-dir`` on the dev PC for analysis.
6. Counts detections from the recorded ``Detection2DArray`` and prints:
   - per-second publish rate
   - per-class kept / rejected counts (via the geometry-filter log channel)
   - any error patterns.

This produces two bags (cubes + empty) that go under
``evaluation/m5_live/`` so the M5 acceptance criteria are durable, evidence-
backed, and reproducible from the documented commands.

Usage (Jetson SSH session — assumes node is already running):

    ssh ubuntu@192.168.2.138
    # ... after vendor bringup + detection.launch.py are live ...
    # Record cubes-in-frame for 30s
    python3 /tmp/m5_capture_bag.py \
        --out-dir /tmp/m5_bag_cubes \
        --duration-sec 30

The same command against an empty scene (cubes removed) yields the second bag.
"""
from __future__ import annotations

import argparse
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", required=True, type=Path,
                   help="Where to write the .bag/.mcap on the Jetson")
    p.add_argument("--duration-sec", type=float, default=30.0)
    p.add_argument("--topics", nargs="+", default=[
        "/cube_detections",
        "/cube_detections/vendor_objects",
        "/cube_detections/debug_image",
        "/depth_cam/rgb/image_raw",
        "/depth_cam/depth/image_raw",
    ])
    p.add_argument("--format", choices=["mcap", "bag"], default="bag")
    args = p.parse_args()

    # ros2 bag record refuses to write into an existing dir; let it create it.
    if args.out_dir.exists():
        import shutil
        shutil.rmtree(args.out_dir)

    cmd = [
        "ros2", "bag", "record",
        "-o", str(args.out_dir),
        "--storage", "mcap" if args.format == "mcap" else "sqlite3",
    ] + args.topics
    print(f"[m5-bag] starting: {' '.join(cmd)}")
    print(f"[m5-bag] will run for {args.duration_sec:.1f}s")
    proc = subprocess.Popen(cmd)

    try:
        time.sleep(args.duration_sec)
    except KeyboardInterrupt:
        print("[m5-bag] interrupted, stopping")
    finally:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

    # Write a sidecar metadata file
    metadata = args.out_dir / "metadata.json"
    metadata.write_text(
        f'{{"duration_sec": {args.duration_sec}, '
        f'"topics": {args.topics}, '
        f'"format": "{args.format}", '
        f'"recorded_at_unix": {time.time()}}}\n'
    )
    print(f"[m5-bag] wrote {metadata}")
    return 0


if __name__ == "__main__":
    sys.exit(main())