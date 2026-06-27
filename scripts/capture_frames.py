#!/usr/bin/env python3
"""Capture still JPGs from a ROS 2 image topic.

Default topic and target directory are set for the JetRover
`/depth_cam/rgb/image_raw` topic. Saves up to ``--max-frames`` JPGs
spaced at least ``--interval-s`` seconds apart, plus a JSON sidecar
with per-frame metadata (seq, timestamp, sha256, byte size, encoding,
width, height, frame_id).

Used by kanban card t_1c0e63d1 to produce M4/M6 evaluation data.

Run on the Jetson with the vendor bringup active (it owns the camera):

    source /opt/ros/humble/setup.bash
    source /home/ubuntu/ros2_ws/install/setup.bash
    python3 scripts/capture_frames.py \\
        --topic /depth_cam/rgb/image_raw \\
        --out-dir /home/ubuntu/cube_camera_samples/empty_2026-06-27 \\
        --max-frames 30 \\
        --interval-s 1.0 \\
        --prefix empty
"""
# pyright: reportMissingImports=false, reportUndefinedVariable=false
# This script runs on the Jetson (Orin Nano) only, where rclpy / cv_bridge /
# sensor_msgs are installed as ROS 2 apt packages. The dev PC does not have
# those, and Pyright would otherwise flag every reference.
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import cv2  # OpenCV; provided by ros-humble-opencv on Jetson
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class FrameSaver(Node):
    def __init__(
        self,
        topic: str,
        out_dir: Path,
        max_frames: int,
        interval_s: float,
        prefix: str,
    ) -> None:
        super().__init__("frame_saver")
        self.bridge = CvBridge()
        self.out_dir = out_dir
        self.max_frames = max_frames
        self.interval_s = interval_s
        self.prefix = prefix
        self.saved = 0
        self.last_save_t = 0.0
        self.metadata: list[dict] = []
        self.sub = self.create_subscription(Image, topic, self._cb, 10)

    def _cb(self, msg: Image) -> None:
        now = time.monotonic()
        if now - self.last_save_t < self.interval_s:
            return
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"cv_bridge conversion failed: {exc!r}")
            return
        idx = self.saved + 1
        name = f"{self.prefix}_{idx:04d}.jpg"
        path = self.out_dir / name
        if not cv2.imwrite(str(path), frame, [cv2.IMWRITE_JPEG_QUALITY, 92]):
            self.get_logger().error(f"cv2.imwrite failed for {path}")
            return
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        sec = msg.header.stamp.sec
        nsec = msg.header.stamp.nanosec
        meta = {
            "index": idx,
            "filename": name,
            "topic": msg.header.frame_id or "",
            "stamp_sec": sec,
            "stamp_nanosec": nsec,
            "stamp_iso": (
                time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(sec + nsec * 1e-9))
                + f".{nsec:09d}Z"
            ),
            "width": int(msg.width),
            "height": int(msg.height),
            "encoding": msg.encoding,
            "step": int(msg.step),
            "sha256": sha,
            "bytes_on_disk": path.stat().st_size,
        }
        self.metadata.append(meta)
        self.saved += 1
        self.last_save_t = now
        self.get_logger().info(
            f"saved {name} ({meta['bytes_on_disk']} bytes, sha256={sha[:12]}...)"
        )

    def flush_metadata(self) -> None:
        sidecar = self.out_dir / f"{self.prefix}_metadata.json"
        sidecar.write_text(json.dumps(self.metadata, indent=2))
        self.get_logger().info(f"wrote metadata sidecar: {sidecar}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0] if __doc__ else "")
    p.add_argument("--topic", default="/depth_cam/rgb/image_raw")
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--max-frames", type=int, default=30)
    p.add_argument("--interval-s", type=float, default=1.0)
    p.add_argument("--prefix", default="frame")
    p.add_argument(
        "--timeout-s",
        type=float,
        default=0.0,
        help="If >0, exit after this many seconds even if --max-frames not reached.",
    )
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rclpy.init()
    node = FrameSaver(
        str(args.topic), args.out_dir, args.max_frames, args.interval_s, args.prefix
    )

    deadline = time.monotonic() + args.timeout_s if args.timeout_s > 0 else None
    try:
        while rclpy.ok() and node.saved < node.max_frames:
            rclpy.spin_once(node, timeout_sec=0.1)
            if deadline is not None and time.monotonic() >= deadline:
                node.get_logger().info(
                    f"timeout reached after {node.saved}/{node.max_frames} frames"
                )
                break
    except KeyboardInterrupt:
        node.get_logger().info("interrupted by user")
    finally:
        node.flush_metadata()
        node.destroy_node()
        rclpy.shutdown()
    print(f"saved {node.saved} frame(s) to {args.out_dir}", file=sys.stderr)
    return 0 if node.saved > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())