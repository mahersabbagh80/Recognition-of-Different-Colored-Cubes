# Milestones

## Model strategy (one-week timeline)

**Default path:** Use pretrained YOLOv5 weights from the [Roboflow Universe project](https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1) → export ONNX → TensorRT → deploy.

**Fallback path:** If standalone inference on robot camera images is below target accuracy, fine-tune locally on dev PC (RTX 4070 Ti, 20–30 epochs on the Roboflow dataset; add robot images only if still failing). Do not collect and annotate a custom dataset upfront.

TensorRT export on the Jetson is the highest schedule risk — prioritize steps 2–6 before any training work.

---

## Overview

| # | Milestone | Done when |
|---|-----------|-----------|
| M1 | Environment ready | Camera topic verified live, ROS 2 package scaffolding exists |
| M2 | Model weights ready | `best.pt` obtained (Roboflow pretrained — no custom training required) |
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
- [ ] Camera topic verified live on Jetson: `ros2 topic hz /depth_cam/rgb/image_raw`
- [ ] PyTorch / ONNX / TensorRT versions confirmed on Jetson

**Done when:** Camera topic is publishing and the package builds cleanly.

---

## M2 — Model Weights Ready

- [ ] Download pretrained YOLOv5 weights from Roboflow Universe (`best.pt`)
- [ ] Save to `models/best.pt` on dev machine or Jetson

**Done when:** `best.pt` is available locally. No local training or custom dataset required for this milestone.

**Fine-tune trigger (defer to M3):** Only if standalone inference (M4) fails accuracy checks.

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
3. **Obtain weights** — download Roboflow pretrained `best.pt` (no custom training yet)
4. **Export ONNX** — `best.pt` → `best.onnx`
5. **TensorRT conversion** — ONNX → TensorRT FP16 `.engine` on Jetson
6. **Standalone inference test** — `scripts/test_inference.py` on robot camera snapshots; if accuracy poor → fine-tune locally (RTX 4070 Ti, 20–30 epochs) and repeat steps 4–6
7. **Minimal ROS 2 node** — subscribe, infer, print detections to terminal
8. **Add publishers** — `/cube_detections`, `/cube_detections/vendor_objects`, and `/cube_detections/debug_image`
9. **Visualize** — confirm bounding boxes in RViz2 or `rqt_image_view`
10. **Evaluate** — 50-frame structured test, measure fps and distance
