# Milestones

## Overview

| # | Milestone | Done when |
|---|-----------|-----------|
| M1 | Environment ready | Camera topic verified live, ROS 2 package scaffolding exists |
| M2 | Dataset ready | Annotated cube images exported from Roboflow in YOLOv5 format |
| M3 | Model trained | YOLOv5s trained on Colab, ONNX export successful |
| M4 | Model on Jetson | TensorRT engine running inference on saved images on Jetson |
| M5 | ROS 2 node live | Node publishing to `/cube_detections` with live camera feed |
| M6 | Evaluation complete | 50-frame test done, frame rate and distance range measured |
| M7 | Repository complete | README, diagram, results, clean code all committed |

---

## M1 — Environment Ready

- [x] ROS 2 package scaffolding (`recognition_of_different_colored_cubes`)
- [x] `cube_detection_node` scaffold (no inference logic)
- [x] Launch file and config placeholders
- [ ] Camera topic verified live on Jetson: `ros2 topic hz /depth_cam/rgb/image_raw`
- [ ] PyTorch / ONNX / TensorRT versions confirmed on Jetson

**Done when:** Camera topic is publishing and the package builds cleanly.

---

## M2 — Dataset Ready

- [ ] Download starter dataset from Roboflow
- [ ] Capture supplementary images from robot camera
- [ ] Annotate and export in YOLOv5 format

**Done when:** YOLOv5-format dataset is ready for Colab training.

---

## M3 — Model Trained

- [ ] Train YOLOv5s on Colab (50–100 epochs)
- [ ] Validate on hold-out set
- [ ] Export to ONNX

**Done when:** `best.onnx` export succeeds without errors.

---

## M4 — Model on Jetson

- [ ] Convert ONNX to TensorRT FP16 engine on Jetson
- [ ] Run `scripts/test_inference.py` on saved test images
- [ ] Confirm detections with bounding boxes and correct class labels

**Done when:** Standalone inference detects cubes in saved images at acceptable accuracy.

---

## M5 — ROS 2 Node Live

- [ ] Subscribe to `/depth_cam/rgb/image_raw`
- [ ] Run TensorRT inference per frame
- [ ] Publish `/cube_detections` and `/cube_detections/debug_image`
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

1. **Verify camera** — `ros2 topic hz /depth_cam/rgb/image_raw`
2. **Check versions** — PyTorch, ONNX, TensorRT on Jetson
3. **Collect and annotate dataset** — robot camera images → Roboflow
4. **Train on Colab** — YOLOv5s, 50–100 epochs, export ONNX
5. **TensorRT conversion** — ONNX → TensorRT FP16 on Jetson
6. **Standalone inference test** — `scripts/test_inference.py`, no ROS 2
7. **Minimal ROS 2 node** — subscribe, infer, print detections to terminal
8. **Add publishers** — `/cube_detections` and `/cube_detections/debug_image`
9. **Visualize** — confirm bounding boxes in RViz2 or `rqt_image_view`
10. **Evaluate** — 50-frame structured test, measure fps and distance
