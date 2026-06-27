#!/usr/bin/env python3
"""M5 offline replay harness — runs the M5 node's pipeline end-to-end on a
saved synchronised RGB+depth dataset (no ROS, no live camera).

Re-uses the same pure-Python building blocks the M5 node uses:

  - _letterbox + _decode_yolov5_output from cube_detection_node.py
  - compute_geometry + decide from m4c_geometry_filter.py

Inference uses ONNX Runtime (CPU) instead of TensorRT — the same exported
model produces equivalent outputs on both engines, and ONNX lets us run
this script on the dev PC for unit-level verification before the Jetson
live test. Per-frame latency on the dev PC is NOT representative of the
Jetson; this script only verifies detection correctness + filter verdict
parity, not timing.

Usage:

    python3 scripts/m5_offline_replay.py \\
        --rgb-dir evaluation/camera_samples/cubes_depth_2026-06-27 \\
        --onnx models/best.onnx \\
        --out-json evaluation/m5_live/replay_cubes_summary.json \\
        --label cubes
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

# Add project scripts/ to sys.path so we can import the canonical m4c filter.
sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "scripts")
)

from m4c_geometry_filter import compute_geometry, decide  # noqa: E402

# Reuse the letterbox + decode helpers from the node
from cube_detection_node import _letterbox, _decode_yolov5_output, CLASS_NAMES  # noqa: E402


def _load_rgb_depth(rgb_dir: Path, idx: int):
    rgb_path = rgb_dir / f"cubes_{idx:04d}_rgb.jpg"
    depth_path = rgb_dir / f"cubes_{idx:04d}_depth.png"
    if not rgb_path.exists() or not depth_path.exists():
        return None, None
    rgb = cv2.imread(str(rgb_path), cv2.IMREAD_COLOR)
    depth = cv2.imread(str(depth_path), cv2.IMREAD_UNCHANGED)
    return rgb, depth


def replay(rgb_dir: Path, onnx_path: Path, label: str,
           conf: float, iou: float, imgsz: int,
           filter_params: dict, max_frames: int = 0) -> dict:
    import onnxruntime as ort

    sess = ort.InferenceSession(
        str(onnx_path), providers=["CPUExecutionProvider"]
    )
    in_name = sess.get_inputs()[0].name
    out_name = sess.get_outputs()[0].name
    print(f"[m5-replay] onnx={onnx_path}  rgb-dir={rgb_dir}  "
          f"conf={conf}  iou={iou}  imgsz={imgsz}")

    per_class: dict[str, dict[str, int]] = {
        c: {"input": 0, "kept": 0, "rejected": 0} for c in CLASS_NAMES
    }
    reject_reasons: Counter = Counter()
    yolo_ms_list: list[float] = []
    filter_ms_list: list[float] = []
    frame_keeps: list[int] = []
    frames_analyzed = 0

    idx = 1
    while True:
        if max_frames and frames_analyzed >= max_frames:
            break
        rgb, depth_mm = _load_rgb_depth(rgb_dir, idx)
        if rgb is None or depth_mm is None:
            break
        idx += 1
        frames_analyzed += 1

        h0, w0 = rgb.shape[:2]
        img, r, (pad_l, pad_t) = _letterbox(rgb[:, :, ::-1], imgsz)
        img = (img.astype(np.float32) / 255.0).transpose(2, 0, 1)
        img = np.ascontiguousarray(img)[np.newaxis, ...]

        t0 = time.perf_counter()
        out = sess.run([out_name], {in_name: img})[0]
        yolo_ms = (time.perf_counter() - t0) * 1000.0
        yolo_ms_list.append(yolo_ms)

        dets = _decode_yolov5_output(out, conf, iou, (w0, h0), r, (pad_l, pad_t))
        frame_keeps_this = 0
        for class_name, conf_i, box in dets:
            per_class[class_name]["input"] += 1
            x1, y1, x2, y2 = [int(round(v)) for v in box]
            t_f0 = time.perf_counter()
            stats = compute_geometry(depth_mm, x1, y1, x2, y2, filter_params)
            verdict, reason = decide(stats, filter_params)
            filter_ms = (time.perf_counter() - t_f0) * 1000.0
            filter_ms_list.append(filter_ms)
            if verdict == "KEEP":
                per_class[class_name]["kept"] += 1
                frame_keeps_this += 1
            else:
                per_class[class_name]["rejected"] += 1
                tag = reason.split(":")[0]
                reject_reasons[tag] += 1
        frame_keeps.append(frame_keeps_this)

    yolo_arr = np.array(yolo_ms_list) if yolo_ms_list else np.array([0.0])
    filter_arr = np.array(filter_ms_list) if filter_ms_list else np.array([0.0])

    summary = {
        "label": label,
        "rgb_dir": str(rgb_dir),
        "onnx": str(onnx_path),
        "conf_threshold": conf,
        "iou_threshold": iou,
        "imgsz": imgsz,
        "filter_params": filter_params,
        "num_frames": frames_analyzed,
        "per_class": per_class,
        "reject_reasons": dict(reject_reasons),
        "frame_keeps_total": sum(frame_keeps),
        "frames_with_keep": sum(1 for k in frame_keeps if k > 0),
        "yolo_ms": {
            "median": float(np.median(yolo_arr)),
            "p95": float(np.percentile(yolo_arr, 95)),
            "max": float(np.max(yolo_arr)),
        },
        "filter_ms_per_box": {
            "median": float(np.median(filter_arr)),
            "p95": float(np.percentile(filter_arr, 95)),
            "max": float(np.max(filter_arr)),
        },
    }
    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--rgb-dir", required=True, type=Path)
    p.add_argument("--onnx", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--label", default="run")
    p.add_argument("--conf", type=float, default=0.50)
    p.add_argument("--iou", type=float, default=0.45)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--max-frames", type=int, default=0)
    # M4c1 v2-only filter params (must match what the live node uses)
    p.add_argument("--raised-mm", type=float, default=30.0)
    p.add_argument("--min-raised-frac", type=float, default=0.20)
    p.add_argument("--max-planar-top-stddev-mm", type=float, default=30.0)
    p.add_argument("--max-ratio", type=float, default=1.2)
    p.add_argument("--inset-px", type=int, default=1)
    p.add_argument("--annulus-outer-px", type=int, default=15)
    p.add_argument("--n-min", type=int, default=30)
    p.add_argument("--max-depth-mm", type=int, default=4000)
    p.add_argument("--fx", type=float, default=360.3266)
    p.add_argument("--fy", type=float, default=360.3266)
    p.add_argument("--cx", type=float, default=321.0181)
    p.add_argument("--cy", type=float, default=179.2141)
    args = p.parse_args()

    filter_params = {
        "raised_mm": args.raised_mm,
        "min_raised_frac": args.min_raised_frac,
        "max_planar_top_stddev_mm": args.max_planar_top_stddev_mm,
        "max_ratio": args.max_ratio,
        "inset_px": args.inset_px,
        "annulus_outer_px": args.annulus_outer_px,
        "n_min": args.n_min,
        "max_depth_mm": args.max_depth_mm,
        "fx": args.fx, "fy": args.fy, "cx": args.cx, "cy": args.cy,
    }
    summary = replay(args.rgb_dir, args.onnx, args.label,
                     args.conf, args.iou, args.imgsz,
                     filter_params, args.max_frames)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2))
    print(f"\n[m5-replay] wrote {args.out_json}")
    print(f"  frames={summary['num_frames']}  "
          f"per-class={summary['per_class']}  "
          f"frame_keeps_total={summary['frame_keeps_total']}  "
          f"frames_with_keep={summary['frames_with_keep']}")
    print(f"  yolo ms (dev PC, ORT CPU): median={summary['yolo_ms']['median']:.1f}  "
          f"p95={summary['yolo_ms']['p95']:.1f}  max={summary['yolo_ms']['max']:.1f}")
    print(f"  filter ms/box: median={summary['filter_ms_per_box']['median']:.2f}  "
          f"p95={summary['filter_ms_per_box']['p95']:.2f}  "
          f"max={summary['filter_ms_per_box']['max']:.2f}")
    print(f"  reject reasons: {summary['reject_reasons']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())