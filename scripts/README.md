# Scripts index

Index for the current scripts and historical archive under `scripts/`. Use
this to find the right entry point for the current workflow.

Last updated: 2026-09-13 (current workflow and archive pointers).

## Current September workflow

Use [the completed workflow](../docs/training-and-validation-workflow.md) for the selected data and [Sunday's journal](../docs/development-learning-journal/2026-09-13-sunday.md) for the exact dated export and live commands.

| Script | Role |
|---|---|
| [capture_frames.py](capture_frames.py) | Save ROS camera images and metadata |
| [build_annotation_review.py](build_annotation_review.py) | Build the human annotation review gallery |
| [prepare_reviewed_robot_dataset.py](prepare_reviewed_robot_dataset.py) | Export approved image/label splits and manifest |
| [run_robot_training_experiment.py](run_robot_training_experiment.py) | Run the reviewed-data training experiment |
| [run_robot_training_smoke.py](run_robot_training_smoke.py) | Earlier bounded training smoke check |
| [test_inference.py](test_inference.py) | Check an exported engine on saved images |
| [capture_rgb_depth_sync.py](capture_rgb_depth_sync.py) | Capture synchronized evidence for future depth diagnosis |

The commands below describe older milestone recipes; do not substitute their generic best paths for the verified September engine. Model conversion and training are not started by reading this index.

Categories:

- **M0 Model / export** — smoke-test inference on exported artifacts.
- **M3 Smoke tests** — first-pass YOLO sanity checks on dev PC.
- **M4c Geometry filter** — distractor gate, V3/V4 runs, summary.
- **M5 Live eval** — bag capture, analysis, offline replay, latency parsing.
- **Capture** — JetRover-side ROS subscribers that save RGB / depth frames.
- **Historical recipes** — earlier Roboflow and M4c1 utilities in the [archive](archive/README.md); not part of the active workflow.

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
| `check_empty_scene.py` | Pre-V4 helper: prints how much clutter is on the floor before a capture. |

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

## Earlier Roboflow training utilities (archived)

The Roboflow download, dataset-normalization, hard-negative build, fine-tuning,
and validation scripts were moved to [`archive/roboflow/`](archive/roboflow/).
They document earlier experiments and are not part of the current September
workflow above.

## Earlier M4c1 debug helpers (archived)

The one-shot M4c1 distractor-analysis helpers are preserved under
[`archive/dev_helpers/`](archive/dev_helpers/). See the [archive index](archive/README.md)
for their names and historical roles.
