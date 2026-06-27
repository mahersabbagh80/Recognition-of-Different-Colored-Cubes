#!/usr/bin/env python3
"""Capture synchronised RGB + depth frames from the JetRover depth camera.

Subscribes to:
  - /depth_cam/rgb/image_raw       (sensor_msgs/Image, rgb8, 640x360)
  - /depth_cam/depth/image_raw     (sensor_msgs/Image, 16UC1, 640x360)

Output:
  <out-dir>/<prefix>_NNNN_rgb.jpg   (q=92)
  <out-dir>/<prefix>_NNNN_depth.png (uint16 mm; cv2 IMWRITE_PNG with 0)
  <out-dir>/<prefix>_metadata.json  (per-pair sha256 + ROS stamps)

Use message_filters ApproximateTimeSynchronizer with slop=0.05 s to align
RGB and depth. Only pairs whose stamp delta is <= 0.05 s are saved. Any
orphaned message (e.g. depth without recent RGB) is dropped.

Designed to be run on the Jetson with the vendor bringup active.

Usage (Jetson):
  source /opt/ros/humble/setup.bash
  source /home/ubuntu/jetson_ws/install/setup.bash
  python3 scripts/capture_rgb_depth_sync.py \\
      --rgb-topic /depth_cam/rgb/image_raw \\
      --depth-topic /depth_cam/depth/image_raw \\
      --out-dir /home/ubuntu/cube_camera_samples/cubes_depth_2026-06-27 \\
      --max-frames 30 --interval-s 1.0 --prefix cubes
"""
# pyright: reportMissingImports=false, reportUndefinedVariable=false
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import cv2
import message_filters
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class SyncSaver(Node):
    def __init__(
        self,
        rgb_topic: str,
        depth_topic: str,
        out_dir: Path,
        max_frames: int,
        interval_s: float,
        prefix: str,
        slop_s: float,
    ) -> None:
        super().__init__("rgb_depth_sync_saver")
        self.bridge = CvBridge()
        self.out_dir = out_dir
        self.max_frames = max_frames
        self.interval_s = interval_s
        self.prefix = prefix
        self.slop_s = slop_s
        self.saved = 0
        self.last_save_t = 0.0
        self.metadata: list[dict] = []

        rgb_sub = message_filters.Subscriber(self, Image, rgb_topic)
        depth_sub = message_filters.Subscriber(self, Image, depth_topic)
        self.ts = message_filters.ApproximateTimeSynchronizer(
            [rgb_sub, depth_sub],
            queue_size=10,
            slop=slop_s,
        )
        self.ts.registerCallback(self._cb)

    def _cb(self, rgb_msg: Image, depth_msg: Image) -> None:
        now = time.monotonic()
        if now - self.last_save_t < self.interval_s:
            return
        rgb_stamp = rgb_msg.header.stamp.sec + rgb_msg.header.stamp.nanosec * 1e-9
        depth_stamp = depth_msg.header.stamp.sec + depth_msg.header.stamp.nanosec * 1e-9
        if abs(rgb_stamp - depth_stamp) > self.slop_s:
            self.get_logger().warn(
                f"sync slop exceeded: rgb={rgb_stamp} depth={depth_stamp}"
            )
            return
        try:
            rgb = self.bridge.imgmsg_to_cv2(rgb_msg, desired_encoding="bgr8")
            depth = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding="passthrough")
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"cv_bridge conversion failed: {exc!r}")
            return

        if depth.dtype != np.uint16:
            self.get_logger().warn(
                f"depth dtype unexpected: {depth.dtype}; will still save raw"
            )
        idx = self.saved + 1
        rgb_name = f"{self.prefix}_{idx:04d}_rgb.jpg"
        depth_name = f"{self.prefix}_{idx:04d}_depth.png"
        rgb_path = self.out_dir / rgb_name
        depth_path = self.out_dir / depth_name
        if not cv2.imwrite(str(rgb_path), rgb, [cv2.IMWRITE_JPEG_QUALITY, 92]):
            self.get_logger().error(f"cv2.imwrite failed for {rgb_path}")
            return
        if not cv2.imwrite(str(depth_path), depth):
            self.get_logger().error(f"cv2.imwrite failed for {depth_path}")
            return

        rgb_sha = hashlib.sha256(rgb_path.read_bytes()).hexdigest()
        depth_sha = hashlib.sha256(depth_path.read_bytes()).hexdigest()

        meta = {
            "index": idx,
            "rgb_filename": rgb_name,
            "depth_filename": depth_name,
            "rgb_frame_id": rgb_msg.header.frame_id or "",
            "depth_frame_id": depth_msg.header.frame_id or "",
            "rgb_stamp_sec": rgb_msg.header.stamp.sec,
            "rgb_stamp_nanosec": rgb_msg.header.stamp.nanosec,
            "depth_stamp_sec": depth_msg.header.stamp.sec,
            "depth_stamp_nanosec": depth_msg.header.stamp.nanosec,
            "stamp_delta_s": abs(rgb_stamp - depth_stamp),
            "rgb_width": int(rgb_msg.width),
            "rgb_height": int(rgb_msg.height),
            "rgb_encoding": rgb_msg.encoding,
            "depth_width": int(depth_msg.width),
            "depth_height": int(depth_msg.height),
            "depth_encoding": depth_msg.encoding,
            "rgb_sha256": rgb_sha,
            "depth_sha256": depth_sha,
            "rgb_bytes_on_disk": rgb_path.stat().st_size,
            "depth_bytes_on_disk": depth_path.stat().st_size,
        }
        self.metadata.append(meta)
        self.saved += 1
        self.last_save_t = now
        self.get_logger().info(
            f"saved pair {idx}/{self.max_frames}  rgb={rgb_name}  "
            f"depth={depth_name}  dt={abs(rgb_stamp - depth_stamp)*1000:.1f} ms"
        )

    def write_sidecar(self) -> None:
        sidecar = self.out_dir / f"{self.prefix}_metadata.json"
        sidecar.write_text(json.dumps(self.metadata, indent=2))
        self.get_logger().info(f"wrote sidecar: {sidecar}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--rgb-topic", default="/depth_cam/rgb/image_raw")
    p.add_argument("--depth-topic", default="/depth_cam/depth/image_raw")
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--max-frames", type=int, default=30)
    p.add_argument("--interval-s", type=float, default=1.0)
    p.add_argument("--prefix", required=True)
    p.add_argument("--slop-s", type=float, default=0.05)
    p.add_argument("--timeout-s", type=float, default=60.0)
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rclpy.init()
    node = SyncSaver(
        rgb_topic=args.rgb_topic,
        depth_topic=args.depth_topic,
        out_dir=args.out_dir,
        max_frames=args.max_frames,
        interval_s=args.interval_s,
        prefix=args.prefix,
        slop_s=args.slop_s,
    )
    try:
        start = time.monotonic()
        while rclpy.ok() and node.saved < args.max_frames:
            rclpy.spin_once(node, timeout_sec=0.5)
            if time.monotonic() - start > args.timeout_s:
                node.get_logger().warn(
                    f"timeout after {node.saved}/{args.max_frames} frames"
                )
                break
    finally:
        node.write_sidecar()
        node.destroy_node()
        rclpy.shutdown()
    print(f"[m4c-capture] saved {node.saved} pairs in {args.out_dir}")
    return 0 if node.saved > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
