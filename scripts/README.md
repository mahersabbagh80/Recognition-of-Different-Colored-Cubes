# Scripts index

Index for every tracked script under `scripts/`. Use this to find the
right script for a given task without scrolling through 28 filenames.

Last updated: 2026-07-05 (M7a repo hygiene pass).

Categories:

- **M0 Model / export** — convert PyTorch → ONNX → TensorRT, smoke-test inference.
- **M3 Smoke tests** — first-pass YOLO sanity checks on dev PC.
- **M4c Geometry filter** — distractor gate, V3/V4 runs, summary.
- **M5 Live eval** — bag capture, analysis, offline replay, latency parsing.
- **Capture** — JetRover-side ROS subscribers that save RGB / depth frames.
- **Training / fine-tune** — Roboflow dataset normalization and hard-neg fine-tune recipes.
- **Dev / debug helpers** — one-off scripts, kept for reproducibility of past analyses.

## M0 Model / export

| Script | One-liner |
|---|---|
| `_download_weights.py` | Helper that prints the Roboflow dataset ID and source URL for `best.pt`. |
| `export_onnx.py` | Export `models/best.pt` → `models/best.onnx` (opset 13). |
| `convert_tensorrt.py` | Convert ONNX → TensorRT FP16 `.engine` for Jetson. |
| `test_inference.py` | Run the engine on every JPG in a directory and dump per-image detections. |

## M3 Smoke tests (dev PC)

| Script | One-liner |
|---|---|
| `m3_smoke_inference.py` | Decode the raw YOLOv5 ONNX output on a saved image — used to verify the model loads and emits the expected `(1, 7, 8400)` shape. |
| `m4a_trt_smoke_inference.py` | Same idea but on the TensorRT engine — run on the same image and compare against the ONNX result. |

## M4c Geometry filter (distractor gate)

| Script | One-liner |
|---|---|
| `m4c_geometry_filter.py` | Apply the depth/geometry post-filter to a saved set of detections — the dev-PC reference implementation that the ROS 2 node copies. |
| `m4c_yolo_inference.py` | Run YOLO alone on M4c capture frames (without the filter) to produce the M4c distractor candidates. |
| `m4c_v3v4_run.sh` | SSH-to-Jetson orchestration: for each distractor, capture 30 sync RGB+depth frames and run the filter. |
| `m4c_v3v4_summary.py` | Read `evaluation/m4c_geometry_filter/filter_results_*.json` and print a KEEP/REJECT markdown table per class. |

## M5 Live evaluation

| Script | One-liner |
|---|---|
| `m5_capture_bag.py` | Jetson-side orchestrator: starts the M5 node + `ros2 bag record` for 30 s captures. |
| `m5_analyze_bag.py` | Dev-PC bag analyzer: per-class kept counts, publish rate, RGB Hz, latency. |
| `m5_offline_replay.py` | Replay the M5 node pipeline end-to-end on saved sync RGB+depth (no ROS, no live camera) — parity check before live runs. |
| `m5_parse_latency.py` | Parse the per-100-frame latency lines from `node.log` into structured JSON. |

## Capture (JetRover side)

| Script | One-liner |
|---|---|
| `capture_frames.py` | rclpy subscriber that saves up to N JPG frames from `/depth_cam/rgb/image_raw`. |
| `capture_rgb_depth_sync.py` | Synchronised RGB + depth capture from `/depth_cam/rgb/image_raw` + `/depth_cam/depth/image_raw` (used for M4c1). |
| `verify_camera_samples.py` | Sidecar SHA-256 + count checker for captured samples. |

## Training / fine-tune (dev PC, optional)

| Script | One-liner |
|---|---|
| `normalize_dataset.py` | Convert the Roboflow dataset to YOLOv5 PyTorch format (5-field normalized lines). |
| `build_hardneg_dataset.py` | Build the M3c hard-negative dataset by merging Roboflow + JetRower-room frames. |
| `finetune_hardneg.py` | Continue-train `models/best.pt` on the hard-negative dataset. |
| `validate_hardneg.py` | Before/after FP comparison between original `best.pt` and the fine-tuned model on M4b frames. |
| `check_empty_scene.py` | Pre-V4 helper that prints how much clutter is on the floor; Maher runs this before a V4 capture. |

## Dev / debug helpers (underscore-prefixed)

These are one-shot scripts written for specific analyses. They are kept
for reproducibility but are not part of any routine pipeline. Move them
to `scripts/dev_helpers/` in a follow-up cleanup pass (see
[`docs/README.md`](../docs/README.md) — Recommended later cleanup).

| Script | One-liner |
|---|---|
| `_cleanup_inspect.py` | Clean up `_*` inspection files under `data/hardneg`. |
| `_inspect_tall_cyl_schema.py` | Dump the JSON schema of the M4c1 tall_cyl outputs. |
| `_peek_bboxes_once.py` | One-shot live RGB peek with bbox overlay + per-frame JSON dump. |
| `_summarize_carton.py` | Summarize carton YOLO + filter results for the M4c1 report. |
| `_summarize_cup.py` | Same, for the cup distractor. |
| `_summarize_tall_cyl.py` | Same, for the tall cylinder distractor. |