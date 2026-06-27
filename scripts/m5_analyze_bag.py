#!/usr/bin/env python3
"""M5 bag analysis — extract detection counts + latency from a recorded bag.

Reads ``/cube_detections`` and ``/depth_cam/rgb/image_raw`` from a bag
recorded by ``scripts/m5_capture_bag.py`` and produces:

  - per-second publish rate of ``/cube_detections``
  - per-class kept count (by reading ``results[].hypothesis.class_id``)
  - mean frame-to-frame RGB interval (a proxy for upstream camera Hz)
  - sync delta between paired RGB and depth if a depth topic is present
  - ``summary.json`` sidecar with all of the above

Usage (dev PC):

    source /opt/ros/humble/setup.bash
    python3 scripts/m5_analyze_bag.py \\
        --bag-dir evaluation/m5_live/bag_cubes_2026-XX-XX \\
        --out-json evaluation/m5_live/bag_cubes_2026-XX-XX/summary.json \\
        --label cubes
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

# ROS side
ROS_DIST = "/opt/ros/humble/local/lib/python3.10/dist-packages"
ROS_SITE = "/opt/ros/humble/lib/python3.10/site-packages"
WS_INSTALL = "/home/maher/maher_ws/install"
for p in (ROS_DIST, ROS_SITE, WS_INSTALL):
    if p not in sys.path:
        sys.path.insert(0, p)

# rosbag2_py (a Python binding for the new C++ bag reader). The exact import
# path varies; the supported one on Humble is ``rosbag2_py``.
try:
    from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions  # type: ignore
except Exception as exc:  # pragma: no cover
    SequentialReader = None  # type: ignore
    _IMPORT_ERROR = exc
from rclpy.time import Time
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message  # type: ignore


def _hms_ns(t) -> int:
    return int(t) // 1000  # rclpy time in ns


def _open_bag(bag_dir: Path):
    if SequentialReader is None:
        raise SystemExit(f"rosbag2_py import failed: {_IMPORT_ERROR}\n"
                         "source /opt/ros/humble/setup.bash first.")
    storage_options = StorageOptions(uri=str(bag_dir), storage_id="mcap")
    converter_options = ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )
    reader = SequentialReader()
    reader.open(storage_options, converter_options)
    return reader


def analyze(bag_dir: Path, label: str) -> dict:
    reader = _open_bag(bag_dir)
    topic_types = {t.name: t.type for t in reader.get_all_topics_and_types()}
    print(f"[m5-analyze] bag={bag_dir}  label={label}")
    print(f"[m5-analyze] topics: {sorted(topic_types.keys())}")

    det_topic = "/cube_detections"
    rgb_topic = "/depth_cam/rgb/image_raw"
    if det_topic not in topic_types:
        print(f"[m5-analyze] no {det_topic} in bag — aborting")
        return {"error": "no detections topic"}

    DetMsg = get_message(topic_types[det_topic])  # vision_msgs/Detection2DArray
    ImageMsg = get_message(topic_types[rgb_topic]) if rgb_topic in topic_types else None

    per_class_kept: Counter = Counter()
    det_publish_t_ns: list[int] = []
    rgb_stamp_ns: list[int] = []
    det_message_count = 0
    det_array_count = 0
    det_kept_total = 0
    det_array_with_keeps = 0

    while reader.has_next():
        topic, data, t_ns = reader.read_next()
        if topic == det_topic:
            det_publish_t_ns.append(t_ns)
            msg = deserialize_message(data, DetMsg)
            det_message_count += 1
            if len(msg.detections) > 0:
                det_array_with_keeps += 1
            for d in msg.detections:
                if d.results:
                    cls = d.results[0].hypothesis.class_id
                    per_class_kept[cls] += 1
                    det_kept_total += 1
        elif topic == rgb_topic and ImageMsg is not None:
            msg = deserialize_message(data, ImageMsg)
            try:
                rgb_stamp_ns.append(_hms_ns(msg.header.stamp.sec) * 1_000_000_000
                                    + msg.header.stamp.nanosec)
            except Exception:
                pass

    # Per-second publish rate
    if det_publish_t_ns:
        first = det_publish_t_ns[0]
        last = det_publish_t_ns[-1]
        duration_sec = max(1e-6, (last - first) / 1e9)
        pub_rate_hz = len(det_publish_t_ns) / duration_sec
    else:
        pub_rate_hz = 0.0
        duration_sec = 0.0

    # Mean RGB frame interval (a proxy for upstream camera fps)
    if len(rgb_stamp_ns) >= 2:
        intervals_ns = [b - a for a, b in zip(rgb_stamp_ns, rgb_stamp_ns[1:]) if b > a]
        rgb_mean_hz = 1e9 / statistics.mean(intervals_ns) if intervals_ns else 0.0
    else:
        rgb_mean_hz = 0.0

    summary = {
        "label": label,
        "bag_dir": str(bag_dir),
        "duration_sec": duration_sec,
        "topics_seen": sorted(topic_types.keys()),
        "detections_topic": det_topic,
        "num_detection_messages": det_message_count,
        "num_arrays_with_keeps": det_array_with_keeps,
        "total_kept": det_kept_total,
        "per_class_kept": dict(per_class_kept),
        "publish_rate_hz": pub_rate_hz,
        "rgb_frames_seen": len(rgb_stamp_ns),
        "rgb_mean_hz": rgb_mean_hz,
    }
    print()
    print(f"[m5-analyze] === {label} ===")
    print(f"  duration: {duration_sec:.2f}s")
    print(f"  detection messages: {det_message_count}")
    print(f"  arrays with >=1 keep: {det_array_with_keeps}")
    print(f"  total kept: {det_kept_total}")
    print(f"  per-class kept: {dict(per_class_kept)}")
    print(f"  publish rate: {pub_rate_hz:.2f} Hz")
    print(f"  RGB frames: {len(rgb_stamp_ns)}  ({rgb_mean_hz:.2f} Hz)")
    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bag-dir", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--label", default="run")
    args = p.parse_args()

    summary = analyze(args.bag_dir, args.label)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2))
    print(f"[m5-analyze] wrote {args.out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())