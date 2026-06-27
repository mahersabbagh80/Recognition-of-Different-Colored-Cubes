"""M5 geometry filter — pure-Python helper module embedded into the ROS package.

This is a clean copy of the two functions used by the M4c1 evidence gate
(``scripts/m4c_geometry_filter.py``): ``compute_geometry`` and ``decide``.
Keeping them as a proper package module (rather than sys.path-injecting the
scripts/ directory) makes the dependency explicit and survives both
symlink-install and full-copy colcon layouts.

The M5 ROS node imports these as:

    from recognition_of_different_colored_cubes.geometry_filter import (
        compute_geometry, decide,
    )

Tested with v2-only M4c1 params (raised_mm=30, min_raised_frac=0.20,
max_planar_top_stddev_mm=30, max_ratio=1.2, inset_px=1, annulus_outer_px=15)
on 622 input detections / 0 kept across 5 testable distractors + 2 conf
levels on the empty scene. See ``evaluation/m4c_geometry_filter/report.md``
for the full validation table.
"""
from __future__ import annotations

from typing import Any

import numpy as np


def compute_geometry(
    depth_mm: np.ndarray, x1: int, y1: int, x2: int, y2: int, params: dict
) -> dict[str, Any]:
    """Return per-detection geometry statistics. Pure numpy, no external deps.

    depth_mm is a (H, W) uint16 array in millimeters; 0 means invalid.
    All coordinates are pixel coordinates into depth_mm.

    Geometry tests (the M4c1 raised-object test — supersedes the §3
    addendum's "height above floor" test, which fails on a tilted-down
    camera because YOLO bboxes cover slightly more than the cube top,
    dragging the in-box median to floor depth):

      1. Floor depth: median of annulus pixels. Floor pixels are tightly
         clustered (~5 mm stddev on a real wood floor).
      2. In-box depth statistics: median / stddev / range / raised
         fraction (count of in-box pixels > RAISED_MM above floor).
      3. 3D extent of the RAISED SUBSET (not the whole bbox). For a
         50 mm cube this gives ~50x50x50 mm and ratio ~1.0; for a tall
         bag this gives ~200x250x400 mm and ratio > 1.2.
      4. Planar top: stddev of depth in the raised subset. Cubes have
         low stddev (flat top), bags have high stddev.

    Edge / center statistics are also computed for diagnostic logging but
    are not part of the KEEP / REJECT decision.
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

    in_median = float(np.median(in_valid_arr))
    in_std = float(np.std(in_valid_arr))
    in_min = float(in_valid_arr.min())
    in_max = float(in_valid_arr.max())
    in_range = in_max - in_min

    raised_mm = float(params.get("raised_mm", 30.0))
    raised_mask = in_valid_arr > (floor_mm + raised_mm)
    n_raised = int(raised_mask.sum())
    raised_frac = n_raised / max(n_valid, 1)

    # For the raised subset, compute the 3D extent in world mm.
    raised_pts_arr = np.empty((0, 3), dtype=np.float32)
    if n_raised > 5:
        ys, xs = np.where((in_box > (floor_mm + raised_mm)) & (in_box > 0))
        actual_xs = xs + x1i
        actual_ys = ys + y1i
        actual_zs = in_box[ys, xs].astype(np.float32)
        raised_pts_arr = np.stack([
            actual_xs.astype(np.float32),
            actual_ys.astype(np.float32),
            actual_zs,
        ], axis=1)

    fx = float(params.get("fx", 360.3266))
    fy = float(params.get("fy", 360.3266))
    z_ref = float(np.median(raised_pts_arr[:, 2])) if n_raised > 5 else in_median
    if n_raised > 5 and z_ref > 0:
        u_range_px = float(raised_pts_arr[:, 0].max() - raised_pts_arr[:, 0].min())
        v_range_px = float(raised_pts_arr[:, 1].max() - raised_pts_arr[:, 1].min())
        z_range_mm = float(raised_pts_arr[:, 2].max() - raised_pts_arr[:, 2].min())
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

    planar_top_stddev = float("nan")
    planar_top_frac = 0.0
    if n_raised > 5:
        z_std = float(np.std(raised_pts_arr[:, 2]))
        planar_top_stddev = z_std
        planar_top_frac = float(np.sum(np.abs(raised_pts_arr[:, 2] - z_ref) < 20.0) / n_raised)

    edge_depths = []
    bx1, by1, bx2, by2 = x1i, y1i, x2i, y2i
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
        "extent_mm": {"u": widths_mm[0], "v": widths_mm[1], "z": widths_mm[2]},
        "ratio_long_over_short": ratio,
        "planar_top_stddev_mm": planar_top_stddev,
        "planar_top_frac": planar_top_frac,
        "edge_median_mm": edge_median,
        "edge_std_mm": edge_std,
        "center_median_mm": center_median,
        "edge_to_center_mm": edge_to_center,
    }


def decide(stats: dict, params: dict) -> tuple[str, str]:
    """Return (verdict, reason).

    KEEP if every test passes (raised-frac, aspect, planar-top stddev).
    KEEP-with-low-depth-quality when the depth image has insufficient
    coverage in this bbox (do not silently filter under data sparsity).
    REJECT otherwise, with a reason string identifying the failing test.
    """
    if not stats.get("valid"):
        return ("KEEP", f"no_depth_stats:{stats.get('reason','unknown')}")
    if stats["n_valid"] < params["n_min"]:
        return ("KEEP", f"low_depth_quality:n_valid={stats['n_valid']}<{params['n_min']}")

    raised_frac = stats["raised_frac"]
    min_raised_frac = float(params.get("min_raised_frac", 0.10))
    if raised_frac < min_raised_frac:
        return ("REJECT", f"flat:raised_frac={raised_frac:.3f}<{min_raised_frac}")

    r = stats["ratio_long_over_short"]
    max_ratio = float(params["max_ratio"])
    if not np.isnan(r) and r > max_ratio:
        return ("REJECT", f"aspect:r={r:.2f}>{max_ratio}")

    pstd = stats["planar_top_stddev_mm"]
    max_planar_std = float(params.get("max_planar_top_stddev_mm", 30.0))
    if not np.isnan(pstd) and pstd > max_planar_std:
        return ("REJECT", f"no_planar_top:stddev={pstd:.1f}mm>{max_planar_std}mm")

    return ("KEEP", "all_tests_passed")