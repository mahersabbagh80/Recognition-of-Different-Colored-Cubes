#!/usr/bin/env python3
"""Jetson-side helper: peek at the current RGB frame and report YOLO detections.

Maher runs this BEFORE the V4 capture to verify the floor is empty
(no cubes, no bags, no clutter in FOV). If the script prints zero
detections at conf 0.25 the scene is clear; otherwise Maher should
remove whatever YOLO is seeing and re-run.

Usage (Jetson):
  source /opt/ros/humble/setup.bash
  source ~/jetson_ws/install/setup.bash
  python3 scripts/check_empty_scene.py            # 1 frame, default conf 0.25
  python3 scripts/check_empty_scene.py --frames 5 # average over 5 frames
  python3 scripts/check_empty_scene.py --save     # also save the peek JPG

The script needs onnxruntime (Jetson arm64 wheel is in requirements.txt)
and PyTorch for torchvision NMS — same deps as scripts/m4c_yolo_inference.py.
"""
from __future__ import annotations
# pyright: reportMissingImports=false, reportUndefinedVariable=false

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import rclpy
import onnxruntime as ort
from cv_bridge import CvBridge
from PIL import Image
from rclpy.node import Node
from sensor_msgs.msg import Image as RosImage


CLASS_NAMES = ["blue_cube", "green_cube", "red_cube"]


def letterbox(im, new_shape=640):
    h0, w0 = im.shape[:2]
    r = min(new_shape / h0, new_shape / w0)
    new_w, new_h = int(round(w0 * r)), int(round(h0 * r))
    pad_w, pad_h = new_shape - new_w, new_shape - new_h
    pad_l, pad_t = pad_w // 2, pad_h // 2
    pad_r, pad_b = pad_w - pad_l, pad_h - pad_t
    img = np.array(Image.fromarray(im).resize((new_w, new_h), 1))
    img = np.pad(img, ((pad_t, pad_b), (pad_l, pad_r), (0, 0)),
                 mode="constant", constant_values=114)
    return img, r, (pad_l, pad_t)


def decode(out, conf_thres, iou_thres, orig_wh, ratio, pad):
    import torch
    from torchvision.ops import nms
    pred = out[0].transpose()
    boxes, scores = pred[:, :4], pred[:, 4:]
    cls_conf = scores.max(axis=1)
    cls_id = scores.argmax(axis=1)
    mask = cls_conf >= conf_thres
    boxes, cls_conf, cls_id = boxes[mask], cls_conf[mask], cls_id[mask]
    if boxes.shape[0] == 0:
        return []
    xyxy = np.zeros_like(boxes)
    xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2
    pad_l, pad_t = pad
    xyxy[:, [0, 2]] -= pad_l
    xyxy[:, [1, 3]] -= pad_t
    xyxy /= ratio
    ow, oh = orig_wh
    xyxy[:, [0, 2]] = xyxy[:, [0, 2]].clip(0, ow - 1)
    xyxy[:, [1, 3]] = xyxy[:, [1, 3]].clip(0, oh - 1)
    keep = []
    for c in np.unique(cls_id):
        idx = np.where(cls_id == c)[0]
        if idx.size == 0:
            continue
        b_c = torch.from_numpy(xyxy[idx]).float()
        s_c = torch.from_numpy(cls_conf[idx]).float()
        k = nms(b_c, s_c, iou_thres).numpy().tolist()
        keep.extend(idx[k])
    return [(CLASS_NAMES[int(cls_id[i])], float(cls_conf[i]),
             tuple(float(v) for v in xyxy[i])) for i in sorted(keep)]


class Peek(Node):
    def __init__(self, onnx_path: str, frames: int, conf: float, save: bool):
        super().__init__("check_empty_scene")
        self.bridge = CvBridge()
        self.sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        self.in_name = self.sess.get_inputs()[0].name
        self.out_name = self.sess.get_outputs()[0].name
        self.frames_target = frames
        self.frames_done = 0
        self.conf = conf
        self.save = save
        self.det_counts: list[int] = []
        self.det_breakdown: dict[str, int] = {c: 0 for c in CLASS_NAMES}
        self.last_image: np.ndarray | None = None
        self.create_subscription(RosImage, "/depth_cam/rgb/image_raw", self._cb, 1)

    def _cb(self, msg: RosImage) -> None:
        if self.frames_done >= self.frames_target:
            return
        try:
            im = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:  # noqa: BLE001
            self.get_logger().error(f"cv_bridge: {e!r}")
            return
        if self.save and self.last_image is None:
            self.last_image = im.copy()
        h0, w0 = im.shape[:2]
        img, r, (pad_l, pad_t) = letterbox(im, 640)
        img = (img.astype(np.float32) / 255.0).transpose(2, 0, 1)
        img = np.ascontiguousarray(img)[np.newaxis, ...]
        out = self.sess.run([self.out_name], {self.in_name: img})[0]
        dets = decode(out, self.conf, 0.45, (w0, h0), r, (pad_l, pad_t))
        self.det_counts.append(len(dets))
        for n, _, _ in dets:
            self.det_breakdown[n] += 1
        self.frames_done += 1
        if self.frames_done >= self.frames_target:
            self._report()

    def _report(self) -> None:
        total = sum(self.det_counts)
        print("\n=== check_empty_scene report ===")
        print(f"frames analysed: {self.frames_done}")
        print(f"total detections (conf>={self.conf}): {total}")
        for c in CLASS_NAMES:
            print(f"  {c}: {self.det_breakdown[c]}")
        if total == 0:
            print("VERDICT: scene appears CLEAR — proceed with V4 capture.")
        else:
            print("VERDICT: scene is NOT clear — remove objects YOLO is seeing.")
        if self.save and self.last_image is not None:
            import cv2
            out = "/tmp/check_empty_scene.jpg"
            cv2.imwrite(out, self.last_image, [cv2.IMWRITE_JPEG_QUALITY, 92])
            print(f"saved peek frame: {out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", default="/home/maher/maher_ws/src/Recognition-of-Different-Colored-Cubes/models/best.onnx")
    ap.add_argument("--frames", type=int, default=1)
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--timeout", type=float, default=10.0)
    args = ap.parse_args()

    if not Path(args.onnx).exists():
        print(f"ERROR: ONNX not found: {args.onnx}", file=sys.stderr)
        return 1

    rclpy.init()
    node = Peek(args.onnx, args.frames, args.conf, args.save)
    deadline = time.monotonic() + args.timeout
    while rclpy.ok() and node.frames_done < node.frames_target \
            and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.2)
    if node.frames_done < node.frames_target:
        print(f"ERROR: only got {node.frames_done}/{node.frames_target} frames in {args.timeout}s",
              file=sys.stderr)
        node.destroy_node()
        rclpy.shutdown()
        return 1
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())