# Scripts index

Index for every tracked script under `scripts/`. Use this to find the
right script for a given task.

Last updated: 2026-07-05 (repo cleanup).

Categories:

- **M0 Model / export** — smoke-test inference on exported artifacts.
- **M3 Smoke tests** — first-pass YOLO sanity checks on dev PC.
- **M4c Geometry filter** — distractor gate, V3/V4 runs, summary.
- **M5 Live eval** — bag capture, analysis, offline replay, latency parsing.
- **Capture** — JetRover-side ROS subscribers that save RGB / depth frames.
- **Training / fine-tune** — Roboflow dataset normalization and hard-neg fine-tune recipes.
- **Dev helpers** — one-off scripts under [`dev_helpers/`](dev_helpers/) (M4c1-era debug).

## M0 Model / export

Export commands (no wrapper scripts — run these directly):

```bash
# best.pt → best.onnx (dev PC, Ultralytics)
yolo export model=models/best.pt format=onnx imgsz=640 opset=13

# best.onnx → best.engine (Jetson)
/usr/src/tensorrt/bin/trtexec \
  --onnx=best.onnx --saveEngine=best.engine --fp16 --workspace=2048
```

Full artifact provenance → [`models/README.md`](../models/README.md).

| Script | One-liner |
|---|---|
| `_download_weights.py` | Roboflow helper: download dataset/weights and record SHA-256. |
| `test_inference.py` | Run the engine on every JPG in a directory and dump per-image detections. |

## M3 Smoke tests (dev PC)

| Script | One-liner |
|---|---|
| `m3_smoke_inference.py` | Decode the raw YOLOv5 ONNX output on a saved image — verify `(1, 7, 8400)` shape. |
| `m4a_trt_smoke_inference.py` | Same idea on the TensorRT engine — compare against the ONNX result. |

## M4c Geometry filter (distractor gate)

| Script | One-liner |
|---|---|
| `m4c_geometry_filter.py` | Apply the depth/geometry post-filter to saved detections (dev-PC reference for the ROS 2 node). |
| `m4c_yolo_inference.py` | Run YOLO alone on M4c capture frames to produce distractor candidates. |
| `m4c_v3v4_run.sh` | SSH-to-Jetson orchestration: for each distractor, capture 30 sync RGB+depth frames and run the filter. |
| `m4c_v3v4_summary.py` | Read `evaluation/m4c_geometry_filter/filter_results_*.json` and print a KEEP/REJECT markdown table. |

## M5 Live evaluation

| Script | One-liner |
|---|---|
| `m5_capture_bag.py` | Jetson-side orchestrator: starts the M5 node + `ros2 bag record` for 30 s captures. |
| `m5_analyze_bag.py` | Dev-PC bag analyzer: per-class kept counts, publish rate, RGB Hz, latency. |
| `m5_offline_replay.py` | Replay the M5 pipeline on saved sync RGB+depth (no ROS) — parity check before live runs. |
| `m5_parse_latency.py` | Parse the per-100-frame latency lines from `node.log` into structured JSON. |

## Capture (JetRover side)

| Script | One-liner |
|---|---|
| `capture_frames.py` | rclpy subscriber that saves up to N JPG frames from `/depth_cam/rgb/image_raw`. |
| `capture_rgb_depth_sync.py` | Synchronised RGB + depth capture (used for M4c1). |
| `verify_camera_samples.py` | Sidecar SHA-256 + count checker for captured samples. |

## Training / fine-tune (dev PC, optional)

| Script | One-liner |
|---|---|
| `normalize_dataset.py` | Convert Roboflow segmentation export → YOLOv5 detection format. |
| `build_hardneg_dataset.py` | Build the M3c hard-negative dataset (Roboflow + JetRover-room frames). |
| `finetune_hardneg.py` | Continue-train `models/best.pt` on the hard-negative dataset. |
| `validate_hardneg.py` | Before/after FP comparison between original and fine-tuned model on M4b frames. |
| `check_empty_scene.py` | Pre-V4 helper: prints how much clutter is on the floor before a capture. |

## Dev helpers (`dev_helpers/`)

One-shot scripts from the M4c1 distractor analysis. Not part of any routine pipeline.

| Script | One-liner |
|---|---|
| `dev_helpers/_cleanup_inspect.py` | Clean up `_*` inspection files under `data/hardneg`. |
| `dev_helpers/_inspect_tall_cyl_schema.py` | Dump the JSON schema of the M4c1 tall_cyl outputs. |
| `dev_helpers/_peek_bboxes_once.py` | One-shot live RGB peek with bbox overlay + per-frame JSON dump. |
| `dev_helpers/_summarize_carton.py` | Summarize carton YOLO + filter results (superseded by `m4c_v3v4_summary.py`). |
| `dev_helpers/_summarize_cup.py` | Same, for the cup distractor. |
| `dev_helpers/_summarize_tall_cyl.py` | Same, for the tall cylinder distractor. |
