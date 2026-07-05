#!/usr/bin/env python3
"""One-shot live RGB peek with bbox overlay + per-frame JSON dump.

Used during M4c1 follow-up to inspect exactly where YOLO fires in the current
scene before deciding whether to run the orchestration capture. This is a
development helper, not a release script.
"""
from __future__ import annotations

import argparse
import json
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
CLASS_COLOR_BGR = {
    "blue_cube":  (255,   0,   0),
    "green_cube": (  0, 255,   0),
    "red_cube":   (  0,   0, 255),
}


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
    def __init__(self, onnx_path, frames, conf, out_prefix, timeout_s):
        super().__init__("peek_bboxes")
        self.bridge = CvBridge()
        self.sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        self.in_name = self.sess.get_inputs()[0].name
        self.out_name = self.sess.get_outputs()[0].name
        self.frames_target = frames
        self.frames_done = 0
        self.conf = conf
        self.out_prefix = out_prefix
        self.timeout_s = timeout_s
        self.results = []
        self.first_image = None
        self.create_subscription(RosImage, "/depth_cam/rgb/image_raw", self._cb, 1)

    def _cb(self, msg):
        if self.frames_done >= self.frames_target:
            return
        try:
            im = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"cv_bridge: {e!r}")
            return
        if self.first_image is None:
            self.first_image = im.copy()
        h0, w0 = im.shape[:2]
        img, r, (pad_l, pad_t) = letterbox(im, 640)
        img = (img.astype(np.float32) / 255.0).transpose(2, 0, 1)
        img = np.ascontiguousarray(img)[np.newaxis, ...]
        out = self.sess.run([self.out_name], {self.in_name: img})[0]
        dets = decode(out, self.conf, 0.45, (w0, h0), r, (pad_l, pad_t))
        self.results.append({
            "frame": self.frames_done + 1,
            "stamp_sec": float(msg.header.stamp.sec) + float(msg.header.stamp.nanosec) * 1e-9,
            "detections": [
                {"class": c, "conf": round(s, 4),
                 "bbox_xyxy": [round(v, 1) for v in b]}
                for c, s, b in dets
            ],
        })
        self.frames_done += 1


def draw_bboxes(im, results, out_path):
    import cv2
    canvas = im.copy()
    for r in results:
        for d in r["detections"]:
            x1, y1, x2, y2 = [int(round(v)) for v in d["bbox_xyxy"]]
            color = CLASS_COLOR_BGR[d["class"]]
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
            label = f"{d['class']} {d['conf']:.2f}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(canvas, (x1, max(0, y1 - th - 4)), (x1 + tw, y1), color, -1)
            cv2.putText(canvas, label, (x1, max(0, y1 - 2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(out_path, canvas, [cv2.IMWRITE_JPEG_QUALITY, 92])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", required=True)
    ap.add_argument("--frames", type=int, default=10)
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--out-prefix", required=True, help="where to write JPEG+JSON, e.g. /tmp/peek")
    ap.add_argument("--timeout", type=float, default=15.0)
    args = ap.parse_args()

    if not Path(args.onnx).exists():
        print(f"ERROR: ONNX not found: {args.onnx}", file=sys.stderr)
        return 1

    rclpy.init()
    node = Peek(args.onnx, args.frames, args.conf, args.out_prefix, args.timeout)
    deadline = time.monotonic() + args.timeout
    while rclpy.ok() and node.frames_done < node.frames_target and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.2)
    if node.frames_done < args.frames:
        print(f"ERROR: only got {node.frames_done}/{args.frames} frames", file=sys.stderr)
        node.destroy_node(); rclpy.shutdown(); return 1

    jpg_path = f"{args.out_prefix}.jpg"
    json_path = f"{args.out_prefix}.json"
    if node.first_image is not None:
        draw_bboxes(node.first_image, node.results, jpg_path)
    with open(json_path, "w") as f:
        json.dump({
            "frames_analysed": node.frames_done,
            "conf_threshold": args.conf,
            "results": node.results,
        }, f, indent=2)
    total = sum(len(r["detections"]) for r in node.results)
    print(f"frames={node.frames_done} total_dets={total} jpg={jpg_path} json={json_path}")
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())