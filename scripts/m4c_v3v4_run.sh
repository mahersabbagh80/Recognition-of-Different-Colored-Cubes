#!/usr/bin/env bash
# M4c1 follow-up: V3 + V4 orchestration.
#
# For each distractor (or empty scene), do:
#   1. SSH to jetrover, run the sync RGB+depth capture (30 frames at 1 fps)
#   2. SCP the capture back to the dev PC
#   3. Run YOLOv5 ONNX inference on the RGBs (writes yolo_detections_*.json)
#   4. Run the geometry filter (writes filter_results_*.json + per-set summary)
#
# Maher's role: physically set up the scene BEFORE each call. This script
# does the rest unattended.
#
# Usage (dev PC):
#   ./scripts/m4c_v3v4_run.sh bottle 2026-06-27   # V3 bottle distractor
#   ./scripts/m4c_v3v4_run.sh empty 2026-06-27   # V4 empty-scene (no cubes)
#   ./scripts/m4c_v3v4_run.sh all 2026-06-27     # run V3 (×6) + V4 sequentially
#
# The Jetson-side capture script lives at /tmp/m4c_capture.py on jetrover
# (installed during M4c1, file sha256 matches scripts/capture_rgb_depth_sync.py
# on the dev PC). If the sha no longer matches, this script will refuse to
# proceed — re-copy with `scp scripts/capture_rgb_depth_sync.py jetrover:/tmp/m4c_capture.py`.

set -euo pipefail

DIST="${1:-}"
DATE_TAG="${2:-$(date +%Y-%m-%d)}"
if [ -z "$DIST" ]; then
  echo "usage: $0 <distractor|empty|all> [YYYY-MM-DD]" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# ---------------------------------------------------------------------------
# Per-distractor metadata.
#
# - "label":   short filename prefix used for capture / outputs
# - "v3kind":  "v3" (distractor), "v4" (empty-scene reference), or "v3pos" (positive
#              control, already captured as cubes_depth_2026-06-27; not re-run here)
# - "display": human-readable name for the report
# - "hint":    one-line description of how Maher sets up the scene
# ---------------------------------------------------------------------------
declare -A DISTRACTORS
DISTRACTORS[bottle]="v3|Bottle (cylinder ~60x60x150 mm, any color on JetRover floor in FOV)|Place ONE bottle on the JetRover floor inside the camera FOV. No cubes, no other clutter."
DISTRACTORS[ball]="v3|Ball (sphere ~80 mm diameter, any color)|Place ONE ball on the JetRover floor inside the camera FOV."
DISTRACTORS[cup]="v3|Cup (cylinder ~80x80x100 mm, any color)|Place ONE cup on the JetRover floor inside the camera FOV."
DISTRACTORS[carton]="v3|Rectangular carton (~60x40x120 mm, any color)|Place ONE carton on the JetRover floor inside the camera FOV."
DISTRACTORS[tall_cyl]="v3|Tall cylinder (~50x50x200 mm, any color)|Place ONE tall cylinder on the JetRover floor inside the camera FOV."
DISTRACTORS[cube_toy]="v3|Cube-shaped non-rgb toy (~50 mm, yellow/orange/white)|Place ONE cube-shaped toy of a non-rgb color in the FOV."
DISTRACTORS[empty]="v4|Empty scene (JetRover floor, no cubes, no clutter)|Remove ALL cubes, bags, packages, and clutter from the JetRover floor. Camera FOV should be empty wood floor + background."

run_one() {
  local label="$1"
  local meta="${DISTRACTORS[$label]:-}"
  if [ -z "$meta" ]; then
    echo "ERROR: unknown distractor '$label'. Known: ${!DISTRACTORS[*]}" >&2
    return 2
  fi
  IFS='|' read -r kind display hint <<< "$meta"

  local out_dir="evaluation/camera_samples/${label}_depth_${DATE_TAG}"
  local yolo_json="evaluation/m4c_geometry_filter/yolo_detections_${label}.json"
  local filter_json="evaluation/m4c_geometry_filter/filter_results_${label}.json"
  local ann_dir="evaluation/m4c_geometry_filter/annotated_${label}"
  local remote_out="/home/ubuntu/cube_camera_samples/${label}_depth_${DATE_TAG}"

  echo
  echo "==================================================================="
  echo "[$kind] $display"
  echo "  hint: $hint"
  echo "  out:  $out_dir"
  echo "  yolo: $yolo_json"
  echo "  filt: $filter_json"
  echo "==================================================================="

  mkdir -p "$out_dir" "$ann_dir"

  # ---- 1. Pre-flight: capture script md5 matches dev PC ----
  local dev_md5 jet_md5
  dev_md5="$(md5sum scripts/capture_rgb_depth_sync.py | awk '{print $1}')"
  jet_md5="$(ssh jetrover "md5sum /tmp/m4c_capture.py 2>/dev/null | awk '{print \$1}'")"
  if [ "$dev_md5" != "$jet_md5" ]; then
    echo "ERROR: /tmp/m4c_capture.py on jetrover md5 ($jet_md5) != dev PC ($dev_md5)" >&2
    echo "  fix with:  scp scripts/capture_rgb_depth_sync.py jetrover:/tmp/m4c_capture.py" >&2
    return 1
  fi

  # ---- 2. Verify topic liveness (don't capture if bringup isn't running) ----
  if ! ssh jetrover "bash /tmp/jetrover_probe.sh 2>/dev/null | grep -q 'rgb/image_raw'"; then
    echo "ERROR: /depth_cam/rgb/image_raw not live on jetrover — vendor bringup missing?" >&2
    return 1
  fi

  # ---- 3. Run the sync capture on the Jetson ----
  # The Jetson's user .bashrc returns early for non-interactive shells, so
  # `bash -lc` does NOT source any overlay by itself. We must source the
  # overlay explicitly inside the command. See scripts/capture_rgb_depth_sync.py
  # header for the required stack:
  #   source /opt/ros/humble/setup.bash
  #   source ~/jetson_ws/install/setup.bash    # brings message_filters + cv_bridge
  # NOTE: /opt/ros/humble/local_setup.bash (pulled in transitively) tries to
  # source /home/ubuntu/setup.sh which does not exist on this install; that's
  # a known HiWonder legacy leftover per docs/LOGBOOK.md 2026-06-23 and is
  # harmless (the line is `.: not found`, capture still proceeds).
  echo "[1/4] running sync capture on jetrover -> $remote_out"
  ssh jetrover bash --noprofile --norc <<EOF
set -e
source /opt/ros/humble/setup.bash
source ~/jetson_ws/install/setup.bash
cd /tmp
python3 /tmp/m4c_capture.py --out-dir $remote_out --max-frames 30 --interval-s 1.0 --prefix $label --timeout-s 45
EOF

  # ---- 4. Pull the capture ----
  echo "[2/4] pulling $remote_out -> $out_dir"
  rm -rf "$out_dir"
  mkdir -p "$out_dir"
  scp -r "jetrover:$remote_out"/* "$out_dir"/

  # SHA-256 verify against the sidecar JSON
  python3 scripts/verify_camera_samples.py "$out_dir" --prefix "$label" || {
    echo "ERROR: capture SHA-256 verification failed" >&2
    return 1
  }

  # ---- 5. YOLOv5 ONNX inference on the RGBs ----
  echo "[3/4] running YOLO inference -> $yolo_json"
  if ! python3 scripts/m4c_yolo_inference.py \
      --onnx models/best.onnx \
      --rgb-dir "$out_dir" \
      --output "$yolo_json" \
      --glob "*_rgb.jpg" --conf 0.25; then
    echo "ERROR: YOLO inference failed. Is torch+torchvision installed?" >&2
    echo "  fix with: pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu" >&2
    return 1
  fi

  # ---- 6. Geometry filter (v2-only parameter set, M4c1 recommended) ----
  # NOTE: the M4c1 "v2-only" sweep used inset_px=1, annulus_outer_px=15.
  # We pass them explicitly here so V3+V4 results are directly comparable
  # to M4c1's filter_results_cubes.json / sweep_v2-only.json. Without
  # these flags the script defaults (4 and 30) apply, which behave
  # differently on gray-cloth annulus floor depth.
  echo "[4/4] running geometry filter -> $filter_json"
  python3 scripts/m4c_geometry_filter.py \
    --detections-json "$yolo_json" \
    --depth-dir "$out_dir" \
    --rgb-dir "$out_dir" \
    --output-json "$filter_json" \
    --output-annotated-dir "$ann_dir" \
    --prefix "$label" --conf-threshold 0.25 \
    --raised-mm 30 --min-raised-frac 0.20 \
    --max-planar-top-stddev-mm 30 --max-ratio 1.2 \
    --inset-px 1 --annulus-outer-px 15
}

# ---------------------------------------------------------------------------
# Main: dispatch on argument
# ---------------------------------------------------------------------------
case "$DIST" in
  all)
    for d in bottle ball cup carton tall_cyl cube_toy empty; do
      run_one "$d" || { echo "FAILED on $d"; exit 1; }
    done
    ;;
  *)
    run_one "$DIST"
    ;;
esac

echo
echo "==================================================================="
echo "Done. Run scripts/m4c_v3v4_summary.py to produce the unified table."
echo "==================================================================="