> Historical snapshot preserved on 13 September 2026. Superseded by the current page under docs/.

# Project Definition

## Title

Recognition of Different Colored Cubes

## Duration

1 week

## Purpose

Learning robotics software engineering and producing portfolio evidence for GitHub.

---

## Problem

Detect and classify colored cubes (red, green, blue) in real time using the robot's onboard camera. The system must distinguish cubes from non-cube objects in the scene — shape discrimination, not just colored blob detection.

---

## Classes

| Class ID | Label |
|----------|-------|
| 0 | `red_cube` |
| 1 | `green_cube` |
| 2 | `blue_cube` |

---

## Approach

**YOLOv5 + TensorRT**

A YOLOv5s model detects `red_cube`, `green_cube`, and `blue_cube`. Weights come from the [Roboflow Universe project](https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1) by default (pretrained — no custom training upfront). The model is exported to ONNX and converted to a TensorRT FP16 engine on the Jetson Orin Nano.

**Fine-tune only if needed:** If inference on robot camera images falls below target accuracy, fine-tune locally on dev PC (NVIDIA RTX 4070 Ti, 20–30 epochs on the Roboflow dataset). Custom dataset collection is a fallback, not the default plan.

Classical CV methods (HSV/LAB thresholding, contour-based detection) are explicitly out of scope.

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Color classification accuracy | ≥ 80% on a structured 50-frame test |
| Detection frame rate | ≥ 5 fps on Jetson (inference rate, not camera frame rate) |
| Operating distance | 20–80 cm from camera |

---

## System Outputs

| Output | Topic | Message Type |
|--------|-------|-------------|
| Detections | `/cube_detections` | `vision_msgs/Detection2DArray` |
| Debug image | `/cube_detections/debug_image` | `sensor_msgs/Image` |

**Input:** `/depth_cam/rgb/image_raw` (`sensor_msgs/Image`)

**Node:** `cube_detection_node` in package `recognition_of_different_colored_cubes`

---

## Non-Goals (this project)

- Robot navigation or manipulation based on detections
- Classical color segmentation as the primary detector
- Committing trained model weights to git

---

## Known Risks

| Risk | Mitigation |
|------|------------|
| TensorRT export fails (version mismatch) | Verify PyTorch/ONNX/TensorRT compatibility on Day 1 |
| Model accuracy below 80% | Fine-tune on Roboflow dataset (20–30 epochs); add robot images only if still failing |
| Frame rate below 5 fps | Switch to YOLOv5n or reduce input resolution to 320×320 |
| Camera topic name different | Check with `ros2 topic list` on robot before assuming |

**Fallback:** If TensorRT cannot be resolved, run inference via ONNX Runtime (slower but functional).

---

## Vendor Context (on robot — do not modify)

| Resource | Path on Jetson |
|----------|----------------|
| Vendor color detection demo | `/home/ubuntu/ros2_ws/src/example/example/color_detect/color_detect_demo.py` |
| LAB calibration tool | `/home/ubuntu/software/lab_tool/main.py` |
| Vendor YOLOv5 + TensorRT docs | Hiwonder JetRover documentation, Chapter 6 |
