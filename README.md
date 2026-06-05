# Recognition of Different Colored Cubes

Detect and classify red, green, and blue cubes in real time using the JetRover onboard camera, YOLOv5, TensorRT, and ROS 2.

---

## Project Overview

A custom YOLOv5s model detects and classifies colored cubes (`red_cube`, `green_cube`, `blue_cube`) from the Orbbec depth camera feed. The model distinguishes cubes from non-cube objects in the scene — not just any colored blob. Results are published as ROS 2 messages for visualization and future robot integration.

This is **Project 2** in a progressive JetRover series. Duration: 1–2 weeks. Purpose: learning robotics software engineering and building portfolio evidence for GitHub.

> **Status:** Package scaffolding complete. Inference logic is not implemented yet. Next step: Milestone 1 — verify camera topic on hardware.

---

## Problem Statement

Given a live RGB image stream from the robot's onboard camera, the system must:

1. Detect cube-shaped objects in the scene
2. Classify each detection as `red_cube`, `green_cube`, or `blue_cube`
3. Publish bounding boxes and class labels as `vision_msgs/Detection2DArray`
4. Publish an annotated debug image for live visualization

Operating distance: **20–80 cm** from the camera.

---

## Hardware

| Component | Details |
|-----------|---------|
| Robot | HiWonder JetRover (Orin Nano version), Mecanum chassis |
| Compute | NVIDIA Jetson Orin Nano |
| Camera | Orbbec depth camera (onboard) |
| OS | Ubuntu 22.04 LTS |
| SDK | NVIDIA JetPack |

---

## Software

| Machine | Ubuntu | ROS 2 | Python |
|---------|--------|-------|--------|
| Jetson Orin Nano | 22.04 LTS | Humble | 3.10 |
| Host (dev machine) | 22.04 LTS | Humble | 3.10 |

**On-robot runtime:** OpenCV, cv_bridge, vision_msgs, TensorRT  
**Off-robot training:** Google Colab, PyTorch, YOLOv5, ONNX, Roboflow

See [`docs/technical-stack.md`](docs/technical-stack.md) for the full stack and export chain.

---

## Architecture

![Pipeline](assets/pipeline_diagram.png)

```
Camera hardware (Orbbec)
    ↓
/depth_cam/rgb/image_raw  [sensor_msgs/Image]
    ↓
cube_detection_node  (Python / ROS 2 Humble)
    ├── cv_bridge        → converts ROS 2 image to OpenCV frame
    ├── YOLOv5 + TensorRT → runs inference, outputs bounding boxes + class labels
    └── Confidence filter → discards detections below threshold
    ↓                          ↓
/cube_detections           /cube_detections/debug_image
[vision_msgs/              [sensor_msgs/Image]
 Detection2DArray]
    ↓                          ↓
Robot systems              RViz2 / rqt_image_view
(future integration)       (live visualization)
```

See [`docs/architecture.md`](docs/architecture.md) for detailed pipeline documentation.

### Topics

| Topic | Message Type | Direction |
|-------|-------------|-----------|
| `/depth_cam/rgb/image_raw` | `sensor_msgs/Image` | Input |
| `/cube_detections` | `vision_msgs/Detection2DArray` | Output |
| `/cube_detections/debug_image` | `sensor_msgs/Image` | Output |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Color classification accuracy | ≥ 80% on a structured 50-frame test |
| Detection frame rate | ≥ 5 fps on Jetson (inference rate) |
| Operating distance | 20–80 cm from camera |

---

## Directory Structure

```
Recognition-of-Different-Colored-Cubes/
├── README.md
├── package.xml
├── setup.py
├── setup.cfg
├── .gitignore
├── LICENSE
├── docs/
│   ├── architecture.md
│   ├── Concept-and-Approach.md
│   ├── LOGBOOK.md
│   ├── ROADMAP.md
│   ├── project-definition.md
│   ├── technical-stack.md
│   ├── milestones.md
│   └── evaluation.md
├── recognition_of_different_colored_cubes/
│   ├── __init__.py
│   └── cube_detection_node.py
├── launch/
│   └── detection.launch.py
├── config/
│   └── params.yaml
├── training/
│   └── train.ipynb
├── scripts/
│   ├── test_inference.py
│   ├── export_onnx.py
│   └── convert_tensorrt.py
├── evaluation/
│   └── evaluate.py
├── models/                        # model artifacts not committed to git
├── assets/
│   └── pipeline_diagram.png
├── resource/
├── test/
└── vendor/
```

---

## Dependencies

**ROS 2 packages** (declared in `package.xml`, installed via `rosdep`):

- `rclpy`, `sensor_msgs`, `vision_msgs`, `cv_bridge`, `std_msgs`

**System / pip packages** (on Jetson, documented in `docs/technical-stack.md`):

- OpenCV, PyTorch, ONNX, TensorRT, YOLOv5

**Starting dataset:** [Roboflow — Red Green Blue Cube Detection](https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1)

---

## Getting Started

```zsh
# Build the package
cd ~/maher_ws   # or your colcon workspace root
colcon build --packages-select recognition_of_different_colored_cubes
source install/setup.bash

# Verify the scaffold node starts (no camera or model required yet)
ros2 run recognition_of_different_colored_cubes cube_detection_node
```

Expected: node logs a scaffold initialization message. Exits cleanly on Ctrl+C.

**Launch file (after inference is implemented):**

```zsh
ros2 launch recognition_of_different_colored_cubes detection.launch.py
```

### Milestone 1 — Camera verification (on Jetson)

```zsh
sudo systemctl stop start_app_node.service
ros2 topic list                                    # confirm camera topic name
ros2 topic hz /depth_cam/rgb/image_raw             # confirm live publishing
ros2 run rqt_image_view rqt_image_view             # view live feed
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/project-definition.md`](docs/project-definition.md) | Problem definition, classes, constraints |
| [`docs/technical-stack.md`](docs/technical-stack.md) | Runtime and training stack |
| [`docs/milestones.md`](docs/milestones.md) | M1–M7 milestones and implementation steps |
| [`docs/evaluation.md`](docs/evaluation.md) | 50-frame test protocol (placeholder) |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Early bringup roadmap |
| [`docs/LOGBOOK.md`](docs/LOGBOOK.md) | Development session notes |

---

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
