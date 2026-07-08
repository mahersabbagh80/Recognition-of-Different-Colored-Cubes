#!/usr/bin/env python3
"""Capture still JPGs from a ROS 2 image topic.

The target directory for each capture bucket is
``<out-dir>/<date>/<prefix>/``. Saves up to ``--max-frames`` JPGs spaced at
least ``--interval-s`` seconds apart, plus a JSON sidecar with
per-frame metadata (seq, timestamp, sha256, byte size, encoding, width,
height, frame_id).


Run on the Jetson with the vendor bringup active (it owns the camera):

python3 scripts/capture_frames.py \
    --topic /depth_cam/rgb/image_raw \
    --out-dir /home/ubuntu/cube_camera_samples \
    --max-frames 30 \
    --interval-s 1.0 \
    --prefix empty

# Output:
# /home/ubuntu/cube_camera_samples/2026-07-08/empty/empty_0001.jpg
# /home/ubuntu/cube_camera_samples/2026-07-08/empty/empty_metadata.json
"""
from __future__ import annotations

import argparse # For parsing the command line arguments
import hashlib # For hashing the files on disk
import json # For writing the metadata to a JSON file
import sys # For printing to the console
import time # For timing the saves
from pathlib import Path # For the file paths

import cv2  # OpenCV; provided by ros-humble-opencv on Jetson
import rclpy # For the ROS 2 node
from cv_bridge import CvBridge # For converting the ROS 2 image message to an OpenCV image
from rclpy.node import Node # For the ROS 2 node
from sensor_msgs.msg import Image # For the ROS 2 image message


class FrameSaver(Node):
    """ROS 2 node that subscribes to a camera topic and saves JPG snapshots."""

    def __init__(
        # Initialize the FrameSaver node with the given parameters
        self,
        topic: str, # The ROS 2 topic to subscribe to
        out_dir: Path, # The directory to save the JPGs to
        max_frames: int, # The maximum number of frames to save
        interval_s: float, # The minimum wall-clock gap between saves
        prefix: str, # The prefix to use for the JPGs
    ) -> None:
        super().__init__("frame_saver") 
        # Initialize the bridge to convert the ROS 2 image message to an OpenCV image
        self.bridge = CvBridge()  # converts sensor_msgs/Image → OpenCV ndarray
        self.out_dir = out_dir 
        self.max_frames = max_frames
        self.interval_s = interval_s
        self.prefix = prefix  # e.g. "empty" → empty_0001.jpg, empty_0002.jpg, …
        self.saved = 0 # The number of frames saved
        self.last_save_t = 0.0  # The time of the last save
        self.metadata: list[dict] = []  # The metadata for the frames
        # Queue depth 10: camera publishes faster than we save; drop oldest if full.
        self.sub = self.create_subscription(Image, topic, self._cb, 10)

    def _cb(self, msg: Image) -> None:
        """Handle one incoming frame: rate-limit, convert, write JPG, record metadata."""
        # Use monotonic time (not msg.header.stamp) so --interval-s is real elapsed time.
        now = time.monotonic()
        if now - self.last_save_t < self.interval_s:
            return

        # Most JetRover RGB topics arrive as rgb8 or bgr8; cv_bridge normalises to BGR
        # for OpenCV, which expects BGR channel order for imwrite/display.
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"cv_bridge conversion failed: {exc!r}")
            return

        idx = self.saved + 1
        name = f"{self.prefix}_{idx:04d}.jpg"
        path = self.out_dir / name
        # Quality 92: good visual fidelity without bloating evaluation datasets.
        if not cv2.imwrite(str(path), frame, [cv2.IMWRITE_JPEG_QUALITY, 92]):
            self.get_logger().error(f"cv2.imwrite failed for {path}")
            return

        # Hash the file on disk so verify_camera_samples.py can detect corruption later.
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        sec = msg.header.stamp.sec
        nsec = msg.header.stamp.nanosec
        meta = {
            "index": idx,
            "filename": name,
            "topic": msg.header.frame_id or "",  # optical frame, not the ROS topic name
            "stamp_sec": sec,
            "stamp_nanosec": nsec,
            "stamp_iso": (
                time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(sec + nsec * 1e-9))
                + f".{nsec:09d}Z"
            ),
            "width": int(msg.width),
            "height": int(msg.height),
            "encoding": msg.encoding,
            "step": int(msg.step),  # row stride in bytes (may exceed width * channels)
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
        """Write {prefix}_metadata.json next to the JPGs (even if capture was interrupted)."""
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

    prefix_path = Path(args.prefix)
    if (
        not args.prefix
        or prefix_path.name != args.prefix
        or args.prefix in {".", ".."}
    ):
        p.error("--prefix must be a non-empty folder name, not a path")

    date_dir = time.strftime("%Y-%m-%d")
    bucket_dir = args.out_dir / date_dir / args.prefix
    bucket_dir.mkdir(parents=True, exist_ok=True)
    rclpy.init()
    node = FrameSaver(
        str(args.topic), bucket_dir, args.max_frames, args.interval_s, args.prefix
    )

    deadline = time.monotonic() + args.timeout_s if args.timeout_s > 0 else None
    try:
        # spin_once in a loop (not spin()): lets us check saved count and timeout each tick.
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
        # Always write metadata — partial captures are still useful for debugging.
        node.flush_metadata()
        node.destroy_node()
        rclpy.shutdown()
    print(f"saved {node.saved} frame(s) to {bucket_dir}", file=sys.stderr)
    return 0 if node.saved > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
