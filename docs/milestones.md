# Milestones

## Model strategy (one-week timeline)

**Default path:** Follow the M2 source decision in [`model-options.md`](model-options.md): use raw compatible Roboflow weights if Maher's account exposes them; otherwise create a local YOLOv5s `best.pt` from the approved Roboflow dataset → export ONNX → TensorRT → deploy.

**Fallback path:** If standalone inference on robot camera images is below target accuracy, fine-tune with additional robot camera images only after the first local artifact has been tested. Do not collect and annotate a custom robot dataset upfront.

TensorRT export on the Jetson is the highest schedule risk — prioritize steps 2–6 before any training work.

---

## Overview

| # | Milestone | Done when |
|---|-----------|-----------|
| M1 | Environment ready | Camera topic verified live, ROS 2 package scaffolding exists |
| M2 | Model weights ready | `models/best.pt` available locally; source/access decision documented in [`model-options.md`](model-options.md) |
| M3 | ONNX export | `best.pt` → `best.onnx` succeeds (fine-tune first only if needed) |
| M4 | Model on Jetson | TensorRT engine running inference on saved images on Jetson |
| M5 | ROS 2 node live | Node publishing to `/cube_detections`, `/cube_detections/vendor_objects`, and `/cube_detections/debug_image` with live vendor camera feed |
| M6 | Evaluation complete | 50-frame test done, frame rate and distance range measured |
| M7 | Repository complete | README, diagram, results, clean code all committed |

---

## M1 — Environment Ready

- [x] ROS 2 package scaffolding (`recognition_of_different_colored_cubes`)
- [x] `cube_detection_node` scaffold (no inference logic)
- [x] Launch file and config placeholders
- [x] Camera topic verified live on Jetson: `ros2 topic hz /depth_cam/rgb/image_raw` ≈ 30 Hz, ~20.65 MB/s, ~0.69 MB/frame, RELIABLE QoS, `frame_id = depth_cam_color_optical_frame`, publisher `/depth_cam`
- [x] PyTorch / ONNX / TensorRT versions confirmed on Jetson: Python 3.10.12, torch 2.4.0 (CUDA 12.2, device "Orin"), onnxruntime-gpu 1.18.0 (TensorRT+CUDA providers), tensorrt 8.6.2, ultralytics 8.3.97, torchvision 0.19.0a0
- [x] `ros-humble-vision-msgs` installed on Jetson (after refreshing the expired OSRF GPG key) so the scaffold's `vision_msgs.msg` import resolves at runtime
- [x] Build + live smoke test on Jetson: `colcon build` clean in 4.75 s (exit 0); `cube_detection_node` runs for 6 s against the live vendor bringup and advertises `/cube_detections`, `/cube_detections/vendor_objects`, `/cube_detections/debug_image` (inference still a placeholder)

**Done when:** Camera topic is publishing and the package builds cleanly.

> **Details: see LOGBOOK.md entry for 2026-06-23 M1 verification** for the full test table, command transcripts, version probe output, build/runtime numbers, and carryover notes (M3 needs `pip install onnx`; M4 needs the bundled `trtexec`; dev PC needs the same OSRF key refresh + `vision_msgs` install). The raw output transcript lives on kanban card `t_639cf91d` (tester retry-3 comment).

---

## M2 — Model Weights Ready

- [ ] Resolve source path using [`model-options.md`](model-options.md): Roboflow raw weights if accessible, otherwise short YOLOv5s fine-tune from approved Roboflow dataset
- [ ] Save the selected/created artifact to `models/best.pt` on dev machine or Jetson

**Done when:** `best.pt` is available locally and its source/version/license are recorded.

**Custom robot-image trigger (defer until after M4):** Add robot camera images only if standalone inference fails accuracy checks.

---

## M3 — ONNX Export

- [ ] Export `best.pt` → `best.onnx` (local script on dev PC)
- [ ] **If M4 accuracy is poor:** fine-tune locally on dev PC (RTX 4070 Ti) — Roboflow dataset, 20–30 epochs, optional robot camera images — then re-export ONNX

**Done when:** `best.onnx` export succeeds without errors.

---

## M4 — Model on Jetson

- [ ] Convert ONNX to TensorRT FP16 engine on Jetson
- [ ] Run `scripts/test_inference.py` on saved images from the robot camera
- [ ] Confirm detections with bounding boxes and correct class labels
- [ ] If accuracy below target → return to M3 fine-tune path, then repeat M4

**Done when:** Standalone inference detects cubes in robot camera images at acceptable accuracy.

---

## M5 — ROS 2 Node Live

- [ ] Subscribe to vendor camera topic `/depth_cam/rgb/image_raw`
- [ ] Run TensorRT inference per frame
- [ ] Publish `/cube_detections`, `/cube_detections/vendor_objects`, and `/cube_detections/debug_image`
- [ ] Add `interfaces` to `package.xml` when vendor-compatible output is implemented
- [ ] Visualize in RViz2 or `rqt_image_view`

**Done when:** Live detections visible with bounding boxes overlaid on camera feed.

---

## M6 — Evaluation Complete

- [ ] Run structured 50-frame test (see [`evaluation.md`](evaluation.md))
- [ ] Measure classification accuracy, inference fps, operating distance

**Done when:** Results recorded; success criteria met or gaps documented.

---

## M7 — Repository Complete

- [ ] README populated with results
- [ ] Pipeline diagram in `assets/`
- [ ] Clean code, all milestones documented in LOGBOOK

**Done when:** Repository is portfolio-ready on GitHub.

---

## Implementation Steps (ordered)

1. **Verify vendor camera** — with `peripherals/depth_camera.launch.py` running, confirm `ros2 topic hz /depth_cam/rgb/image_raw`
2. **Check versions** — PyTorch, ONNX, TensorRT on Jetson
3. **Obtain weights** — follow `model-options.md`: raw Roboflow weights if available, otherwise create `best.pt` with a short YOLOv5s fine-tune from the approved Roboflow dataset
4. **Export ONNX** — `best.pt` → `best.onnx`
5. **TensorRT conversion** — ONNX → TensorRT FP16 `.engine` on Jetson
6. **Standalone inference test** — `scripts/test_inference.py` on robot camera snapshots; if accuracy poor → fine-tune locally (RTX 4070 Ti, 20–30 epochs) and repeat steps 4–6
7. **Minimal ROS 2 node** — subscribe, infer, print detections to terminal
8. **Add publishers** — `/cube_detections`, `/cube_detections/vendor_objects`, and `/cube_detections/debug_image`
9. **Visualize** — confirm bounding boxes in RViz2 or `rqt_image_view`
10. **Evaluate** — 50-frame structured test, measure fps and distance
