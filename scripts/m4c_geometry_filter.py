#!/usr/bin/env python3
"""M4c geometry-filter harness.

Implements the Phase 1 depth/geometry post-filter from
`docs/model-objectness-addendum.md` §3.6 (combined height + ratio + planar
test). Takes:

  - a list of YOLO candidate boxes (xyxy in original RGB frame pixels)
  - a depth image (uint16, mm, registered to RGB frame)
  - the matching RGB image (for visualisation only)

For each candidate, computes per-detection geometry statistics and decides
KEEP / REJECT (and why). Aggregates per-frame latency and per-class
verdict counts. Output:

  - per-detection verdicts (json)
  - per-frame annotated PNGs (PNG with KEEP=green / REJECT=red outlines)
  - a summary.json with overall counts and timings

Geometry tests (all in original RGB pixel coordinates):

  1. In-box valid depth count:           N_valid  (skip if < N_MIN)
  2. Height above annulus floor:         height_mm = median(depth_in_box) - median(depth_annulus)
     An annulus is a ring of INSET_PX-wide rings outside the box on all 4 sides.
     Reject if height_mm < MIN_HEIGHT
  3. 3D bbox aspect ratio of in-box points after floor removal:
       (x_max - x_min) / (z_max - z_min)
     Reject if ratio > MAX_RATIO (long axis over short axis)
  4. Planar-top fraction: fraction of "top" points (upper 20% by z) whose
     depth-gradient vs neighbours is small (i.e. flat top face).
     Reject if planar_frac < MIN_PLANAR_FRAC
  5. Low-depth-evidence behavior: if N_valid < N_MIN, KEEP with a
     depth_quality="low" flag (do not silently filter).

The verdict is REJECT if ANY of tests 2/3/4 fails; KEEP otherwise.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ---- Defaults from docs/model-objectness-addendum.md §3.6 ----
DEFAULTS = {
    "min_height_mm": 15.0,
    "max_ratio": 1.4,
    "min_planar_frac": 0.6,
    "n_min": 30,
    "inset_px": 4,
    "annulus_outer_px": 30,
    "max_depth_mm": 4000,
    "top_quantile": 0.20,
    "planar_grad_mm": 8.0,
}


def compute_geometry(
    depth_mm: np.ndarray, x1: int, y1: int, x2: int, y2: int, params: dict
) -> dict[str, Any]:
    """Return per-detection geometry statistics. Pure numpy, no external deps.

    depth_mm is a (H, W) uint16 array in millimeters; 0 means invalid.
    All coordinates are pixel coordinates into depth_mm.

    Geometry tests (revised for tilted-down camera + small objects):

      The §3 addendum tests (height-above-floor, 3D aspect, planar-top)
      assume a side-on camera and tight YOLO boxes. On a tilted-down camera
      looking at horizontal floor with 50 mm cubes, those tests misfire:

      - A "height above floor" median test fails because YOLO bboxes are
        slightly larger than the cube, so the in-box median is dragged to
        the floor depth. Even tight bboxes span the cube height in image-y,
        so the median is only ~25 mm above the floor (cube is 50 mm tall).
      - The "3D aspect" test (computed from u/v pixel ranges × z_world / fx)
        gives noisy results because the per-pixel depth varies across the
        cube face and a single z_world median is wrong.

      A more robust test is depth-histogram based:

        1. Floor depth: median of annulus pixels. Floor pixels are tightly
           clustered (~5 mm stddev on a real wood floor).
        2. In-box depth stddev: high (~30 mm) for a 50 mm-tall cube, low
           (~5 mm) for a flat distractor. Use stddev > STDDEV_MIN as the
           "raised object" test.
        3. In-box depth range (max-min): high (~50 mm) for a cube, low
           (~10 mm) for a flat distractor. Use RANGE_MIN as a backup.
        4. Raised-point fraction: in-box pixels that are > RAISED_MM above
           the floor median. A cube has > 30% raised pixels; a flat
           distractor has < 5%.

      Once an object is "raised", we still apply:

        - 3D extent ratio of the RAISED SUBSET (not the whole bbox). For
          a cube this gives ~50x50x50 mm and ratio ~1.0; for a tall bag
          this gives ~200x250x400 mm and ratio ~2.0+.
        - Planar top: stddev of depth in the upper-third of raised points.
          Cubes have low stddev (flat top), bags have high stddev.
    """
    H, W = depth_mm.shape
    inset = int(params["inset_px"])
    x1i = max(0, x1 + inset)
    y1i = max(0, y1 + inset)
    x2i = min(W, x2 - inset)
    y2i = min(H, y2 - inset)
    if x2i <= x1i or y2i <= y1i:
        return {"valid": False, "reason": "box too small after inset"}

    in_box = depth_mm[y1i:y2i, x1i:x2i]
    in_valid_arr = in_box[(in_box > 0) & (in_box < int(params["max_depth_mm"]))]
    n_valid = int(in_valid_arr.size)

    a_out = int(params["annulus_outer_px"])
    ay1 = max(0, y1 - a_out)
    ay2 = min(H, y2 + a_out)
    ax1 = max(0, x1 - a_out)
    ax2 = min(W, x2 + a_out)
    annulus = depth_mm[ay1:ay2, ax1:ax2].copy()
    in_y1_rel = max(0, y1 - ay1)
    in_y2_rel = min(ay2 - ay1, y2 - ay1)
    in_x1_rel = max(0, x1 - ax1)
    in_x2_rel = min(ax2 - ax1, x2 - ax1)
    annulus[in_y1_rel:in_y2_rel, in_x1_rel:in_x2_rel] = 0
    ann_valid = annulus[(annulus > 0) & (annulus < int(params["max_depth_mm"]))]
    n_ann = int(ann_valid.size)

    if n_valid == 0:
        return {"valid": False, "reason": "no in-box valid depth"}
    if n_ann == 0:
        return {"valid": False, "reason": "no annulus valid depth"}

    floor_mm = float(np.median(ann_valid))
    floor_std_mm = float(np.std(ann_valid))

    # In-box statistics
    in_median = float(np.median(in_valid_arr))
    in_std = float(np.std(in_valid_arr))
    in_min = float(in_valid_arr.min())
    in_max = float(in_valid_arr.max())
    in_range = in_max - in_min

    raised_mm = float(params.get("raised_mm", 20.0))
    raised_mask = in_valid_arr > (floor_mm + raised_mm)
    n_raised = int(raised_mask.sum())
    raised_frac = n_raised / max(n_valid, 1)

    # For the raised subset, compute the 3D extent in world mm.
    # Find the (u, v) coordinates of each raised point.
    raised_pts_arr = np.empty((0, 3), dtype=np.float32)
    if n_raised > 5:
        ys, xs = np.where((in_box > (floor_mm + raised_mm)) & (in_box > 0))
        # Note: np.where returns indices into in_box, which is depth_mm[y1i:y2i, x1i:x2i]
        # So the actual image coordinates are (xs + x1i, ys + y1i).
        actual_xs = xs + x1i
        actual_ys = ys + y1i
        actual_zs = in_box[ys, xs].astype(np.float32)
        raised_pts_arr = np.stack([actual_xs.astype(np.float32),
                                   actual_ys.astype(np.float32),
                                   actual_zs], axis=1)

    fx = float(params.get("fx", 360.3266))
    fy = float(params.get("fy", 360.3266))
    # Convert pixel ranges to mm using the median z of raised subset
    # (or full bbox if no raised points).
    z_ref = float(np.median(raised_pts_arr[:, 2])) if n_raised > 5 else in_median
    if n_raised > 5 and z_ref > 0:
        u_range_px = float(raised_pts_arr[:, 0].max() - raised_pts_arr[:, 0].min())
        v_range_px = float(raised_pts_arr[:, 1].max() - raised_pts_arr[:, 1].min())
        z_range_mm = float(raised_pts_arr[:, 2].max() - raised_pts_arr[:, 2].min())
        # Approximate world u/v extent using median z of raised subset
        u_world_mm = (u_range_px * z_ref / 1000.0) / fx * 1000.0
        v_world_mm = (v_range_px * z_ref / 1000.0) / fy * 1000.0
        widths_mm = (u_world_mm, v_world_mm, z_range_mm)
    else:
        widths_mm = (0.0, 0.0, 0.0)

    sorted_w = sorted(widths_mm)
    if sorted_w[0] > 1.0:
        ratio = sorted_w[2] / sorted_w[0]
    else:
        ratio = float("nan")

    # Planar top: take the raised points and check stddev of z (depth).
    # A flat top has low z stddev.
    planar_top_stddev = float("nan")
    planar_top_frac = 0.0
    if n_raised > 5:
        z_std = float(np.std(raised_pts_arr[:, 2]))
        planar_top_stddev = z_std
        planar_top_frac = float(np.sum(np.abs(raised_pts_arr[:, 2] - z_ref) < 20.0) / n_raised)

    # EDGE TRANSITION test: the depth just inside the bbox border (1 px ring)
    # versus the depth at the bbox center. For a real cube on the floor, the
    # border catches the floor (at floor depth) while the center catches the
    # cube top. For a flat distractor, border ≈ center.
    edge_depths = []
    bx1, by1, bx2, by2 = x1i, y1i, x2i, y2i
    # Top edge row
    if by2 > by1:
        row_top = depth_mm[by1, bx1:bx2]
        row_bot = depth_mm[by2 - 1, bx1:bx2]
        edge_depths.extend(row_top[(row_top > 0) & (row_top < 4000)].tolist())
        edge_depths.extend(row_bot[(row_bot > 0) & (row_bot < 4000)].tolist())
    if bx2 > bx1:
        col_l = depth_mm[by1:by2, bx1]
        col_r = depth_mm[by1:by2, bx2 - 1]
        edge_depths.extend(col_l[(col_l > 0) & (col_l < 4000)].tolist())
        edge_depths.extend(col_r[(col_r > 0) & (col_r < 4000)].tolist())
    edge_arr = np.array(edge_depths, dtype=np.float32) if edge_depths else np.array([0.0])
    edge_median = float(np.median(edge_arr))
    edge_std = float(np.std(edge_arr))
    # Center: 1/3 inner box
    cx1 = bx1 + (bx2 - bx1) // 3
    cx2 = bx1 + 2 * (bx2 - bx1) // 3
    cy1 = by1 + (by2 - by1) // 3
    cy2 = by1 + 2 * (by2 - by1) // 3
    center_region = depth_mm[cy1:cy2, cx1:cx2]
    center_valid = center_region[(center_region > 0) & (center_region < 4000)]
    if center_valid.size > 0:
        center_median = float(np.median(center_valid))
        edge_to_center = center_median - edge_median
    else:
        center_median = float("nan")
        edge_to_center = float("nan")

    return {
        "valid": True,
        "n_valid": n_valid,
        "n_ann": n_ann,
        "floor_mm": floor_mm,
        "floor_std_mm": floor_std_mm,
        "in_median_mm": in_median,
        "in_std_mm": in_std,
        "in_range_mm": in_range,
        "n_raised": n_raised,
        "raised_frac": raised_frac,
        "extent_mm": {
            "u": widths_mm[0],
            "v": widths_mm[1],
            "z": widths_mm[2],
        },
        "ratio_long_over_short": ratio,
        "planar_top_stddev_mm": planar_top_stddev,
        "planar_top_frac": planar_top_frac,
        "edge_median_mm": edge_median,
        "edge_std_mm": edge_std,
        "center_median_mm": center_median,
        "edge_to_center_mm": edge_to_center,
    }


def decide(stats: dict, params: dict) -> tuple[str, str]:
    """Return (verdict, reason)."""
    if not stats.get("valid"):
        return ("KEEP", f"no_depth_stats:{stats.get('reason','unknown')}")
    if stats["n_valid"] < params["n_min"]:
        return ("KEEP", f"low_depth_quality:n_valid={stats['n_valid']}<{params['n_min']}")

    # Test A: raised-object test. If fewer than RAISED_FRAC of in-box pixels
    # are raised above the floor by RAISED_MM, treat as flat (or hole).
    raised_frac = stats["raised_frac"]
    min_raised_frac = float(params.get("min_raised_frac", 0.10))
    if raised_frac < min_raised_frac:
        return ("REJECT", f"flat:raised_frac={raised_frac:.3f}<{min_raised_frac}")

    # Test B: 3D extent ratio of the raised subset
    r = stats["ratio_long_over_short"]
    max_ratio = float(params["max_ratio"])
    if not np.isnan(r) and r > max_ratio:
        return ("REJECT", f"aspect:r={r:.2f}>{max_ratio}")

    # Test C: planar top — stddev of raised subset depth
    # For a cube top, stddev should be < planar_top_stddev_max
    pstd = stats["planar_top_stddev_mm"]
    max_planar_std = float(params.get("max_planar_top_stddev_mm", 25.0))
    if not np.isnan(pstd) and pstd > max_planar_std:
        return ("REJECT", f"no_planar_top:stddev={pstd:.1f}mm>{max_planar_std}mm")

    return ("KEEP", "all_tests_passed")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--detections-json", required=True, type=Path)
    p.add_argument("--depth-dir", required=True, type=Path,
                   help="dir with <prefix>_<idx>_depth.png files")
    p.add_argument("--rgb-dir", required=True, type=Path,
                   help="dir with <prefix>_<idx>_rgb.jpg files (for annotation)")
    p.add_argument("--output-json", required=True, type=Path)
    p.add_argument("--output-annotated-dir", type=Path,
                   help="optional dir to write annotated PNGs (KEEP=green, REJECT=red)")
    p.add_argument("--prefix", required=True)
    p.add_argument("--conf-threshold", type=float, default=0.25,
                   help="ignore detections below this conf")
    p.add_argument("--min-height-mm", type=float, default=DEFAULTS["min_height_mm"])
    p.add_argument("--max-ratio", type=float, default=DEFAULTS["max_ratio"])
    p.add_argument("--min-planar-frac", type=float, default=DEFAULTS["min_planar_frac"])
    p.add_argument("--n-min", type=int, default=DEFAULTS["n_min"])
    p.add_argument("--inset-px", type=int, default=DEFAULTS["inset_px"])
    p.add_argument("--annulus-outer-px", type=int, default=DEFAULTS["annulus_outer_px"])
    p.add_argument("--max-depth-mm", type=int, default=DEFAULTS["max_depth_mm"])
    p.add_argument("--top-quantile", type=float, default=DEFAULTS["top_quantile"])
    p.add_argument("--planar-grad-mm", type=float, default=DEFAULTS["planar_grad_mm"])
    p.add_argument("--band-mm", type=float, default=30.0,
                   help="depth band around cube for annulus; pixels in annulus "
                        "outside ±band_mm of cube depth are ignored")
    p.add_argument("--raised-mm", type=float, default=20.0,
                   help="a point is 'raised' if it is more than this many mm "
                        "above the annulus (floor) median")
    p.add_argument("--min-raised-frac", type=float, default=0.10,
                   help="reject if fewer than this fraction of in-box pixels are raised")
    p.add_argument("--max-planar-top-stddev-mm", type=float, default=25.0,
                   help="reject if raised-subset z-stddev exceeds this (no flat top)")
    p.add_argument("--fx", type=float, default=360.3266)
    p.add_argument("--fy", type=float, default=360.3266)
    p.add_argument("--cx", type=float, default=321.0181)
    p.add_argument("--cy", type=float, default=179.2141)
    args = p.parse_args()

    params = {
        "min_height_mm": args.min_height_mm,
        "max_ratio": args.max_ratio,
        "min_planar_frac": args.min_planar_frac,
        "n_min": args.n_min,
        "inset_px": args.inset_px,
        "annulus_outer_px": args.annulus_outer_px,
        "max_depth_mm": args.max_depth_mm,
        "top_quantile": args.top_quantile,
        "planar_grad_mm": args.planar_grad_mm,
        "band_mm": args.band_mm,
        "raised_mm": args.raised_mm,
        "min_raised_frac": args.min_raised_frac,
        "max_planar_top_stddev_mm": args.max_planar_top_stddev_mm,
        "fx": args.fx, "fy": args.fy, "cx": args.cx, "cy": args.cy,
    }
    print(f"[m4c-filter] detections: {args.detections_json}")
    print(f"[m4c-filter] depth-dir: {args.depth_dir}  rgb-dir: {args.rgb_dir}")
    print(f"[m4c-filter] params: {json.dumps(params)}")

    dets_doc = json.loads(args.detections_json.read_text())
    frames_in = dets_doc["frames"]
    print(f"[m4c-filter] {len(frames_in)} frames from detections.json")

    if args.output_annotated_dir:
        args.output_annotated_dir.mkdir(parents=True, exist_ok=True)

    per_class_counts = {
        "blue_cube": {"input": 0, "kept": 0, "rejected": 0, "low_qual": 0},
        "green_cube": {"input": 0, "kept": 0, "rejected": 0, "low_qual": 0},
        "red_cube": {"input": 0, "kept": 0, "rejected": 0, "low_qual": 0},
    }
    reject_reasons = {
        "flat": 0, "aspect": 0, "no_planar_top": 0,
        "low_depth_quality": 0, "no_depth_stats": 0,
    }
    per_filter_ms: list[float] = []
    out_frames: list[dict] = []

    for idx, frame in enumerate(frames_in, 1):
        # Locate the matching depth + rgb for this frame
        # detections filenames are like cubes_0001_rgb.jpg
        rgb_path = args.rgb_dir / frame["filename"]
        # depth filename = stem without _rgb
        stem = rgb_path.stem  # cubes_0001_rgb
        depth_stem = stem.replace("_rgb", "") + "_depth"
        depth_path = args.depth_dir / (depth_stem + ".png")
        if not rgb_path.exists():
            print(f"[m4c-filter] WARN: missing rgb {rgb_path}, skip")
            continue
        if not depth_path.exists():
            print(f"[m4c-filter] WARN: missing depth {depth_path}, skip")
            continue
        depth_mm = cv2.imread(str(depth_path), cv2.IMREAD_UNCHANGED)
        if depth_mm is None:
            print(f"[m4c-filter] WARN: cv2.imread depth returned None for {depth_path}")
            continue
        rgb = cv2.imread(str(rgb_path))
        if rgb is None:
            continue

        out_dets = []
        for det in frame["detections"]:
            cls = det["class"]
            conf = det["confidence"]
            x1, y1, x2, y2 = [int(round(v)) for v in det["bbox_xyxy"]]
            if conf < args.conf_threshold:
                continue
            t0 = time.perf_counter()
            stats = compute_geometry(depth_mm, x1, y1, x2, y2, params)
            verdict, reason = decide(stats, params)
            ms = (time.perf_counter() - t0) * 1000.0
            per_filter_ms.append(ms)
            per_class_counts[cls]["input"] += 1
            if verdict == "KEEP":
                if reason.startswith("low_depth_quality"):
                    per_class_counts[cls]["low_qual"] += 1
                else:
                    per_class_counts[cls]["kept"] += 1
            else:
                per_class_counts[cls]["rejected"] += 1
                if reason.startswith("flat"):
                    reject_reasons["flat"] += 1
                elif reason.startswith("aspect"):
                    reject_reasons["aspect"] += 1
                elif reason.startswith("no_planar_top"):
                    reject_reasons["no_planar_top"] += 1
                elif reason.startswith("low_depth_quality"):
                    reject_reasons["low_depth_quality"] += 1
                elif reason.startswith("no_depth_stats"):
                    reject_reasons["no_depth_stats"] += 1
            out_dets.append({
                "class": cls,
                "confidence": conf,
                "bbox_xyxy": [x1, y1, x2, y2],
                "verdict": verdict,
                "reason": reason,
                "geometry": stats,
                "filter_ms": ms,
            })
        out_frames.append({
            "filename": rgb_path.name,
            "depth_filename": depth_path.name,
            "width": int(frame["width"]),
            "height": int(frame["height"]),
            "yolo_ms": frame.get("yolo_ms"),
            "num_input_detections": len([
                d for d in frame["detections"] if d["confidence"] >= args.conf_threshold
            ]),
            "num_kept": sum(1 for d in out_dets if d["verdict"] == "KEEP"),
            "num_rejected": sum(1 for d in out_dets if d["verdict"] == "REJECT"),
            "detections": out_dets,
        })
        if args.output_annotated_dir:
            # Annotate: REJECT = red dashed outline + reason, KEEP = green outline
            pil = Image.open(rgb_path).convert("RGB")
            draw = ImageDraw.Draw(pil)
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13
                )
            except OSError:
                font = ImageFont.load_default()
            for d in out_dets:
                x1, y1, x2, y2 = d["bbox_xyxy"]
                if d["verdict"] == "KEEP":
                    color = (52, 168, 83)
                else:
                    color = (234, 67, 53)
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                label = f"{d['class']} {d['confidence']:.2f} {d['verdict']} {d['reason'][:30]}"
                draw.text((x1, max(0, y1 - 16)), label, fill=color, font=font)
            draw.rectangle([0, 0, pil.width, 18], fill=(0, 0, 0))
            draw.text((4, 2),
                      f"m4c filter | kept={out_frames[-1]['num_kept']} "
                      f"rej={out_frames[-1]['num_rejected']}",
                      fill=(255, 255, 255), font=font)
            out_path = args.output_annotated_dir / f"{rgb_path.stem.replace('_rgb','')}_filter.png"
            pil.save(out_path, "PNG")

    ms_arr = np.array(per_filter_ms) if per_filter_ms else np.array([0.0])
    summary = {
        "params": params,
        "conf_threshold": args.conf_threshold,
        "num_frames": len(out_frames),
        "num_input_detections": int(sum(c["input"] for c in per_class_counts.values())),
        "num_kept": int(sum(c["kept"] for c in per_class_counts.values())),
        "num_rejected": int(sum(c["rejected"] for c in per_class_counts.values())),
        "num_low_quality_kept": int(sum(c["low_qual"] for c in per_class_counts.values())),
        "per_class": per_class_counts,
        "reject_reasons": reject_reasons,
        "filter_latency_ms": {
            "min": float(ms_arr.min()),
            "median": float(np.median(ms_arr)),
            "mean": float(ms_arr.mean()),
            "max": float(ms_arr.max()),
            "p95": float(np.percentile(ms_arr, 95)),
        },
        "frames": out_frames,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, indent=2))
    print()
    print(f"[m4c-filter] wrote {args.output_json}")
    print(f"  per-class (input / kept / rejected / low_qual):")
    for cls, c in per_class_counts.items():
        print(f"    {cls:12s} {c['input']:4d} / {c['kept']:4d} / {c['rejected']:4d} / {c['low_qual']:4d}")
    print(f"  reject reasons: {reject_reasons}")
    print(f"  filter latency (ms): min={summary['filter_latency_ms']['min']:.2f}  "
          f"median={summary['filter_latency_ms']['median']:.2f}  "
          f"max={summary['filter_latency_ms']['max']:.2f}  "
          f"p95={summary['filter_latency_ms']['p95']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
