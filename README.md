# Recognition of Different Colored Cubes

Detect and classify red, green, and blue cubes in real time using the JetRover onboard camera, YOLOv5, TensorRT, and ROS 2.

---

## What it does

This project runs real-time cube detection on a live camera feed from a HiWonder JetRover. A YOLOv5s model finds cube-shaped objects and classifies them as `red_cube`, `green_cube`, or `blue_cube` — not just any colored region in the scene. Inference runs on the Jetson GPU via TensorRT; results are published as ROS 2 `vision_msgs/Detection2DArray` plus an annotated debug image for visualization. A geometry post-filter (raised-fraction + aspect + planar-top stddev) sits on top of the YOLO output at confidence ≥ 0.50 so flat-colored distractors and tall non-cube objects in the JetRover room are suppressed before any detection is published.

Pretrained Roboflow weights are used by default; optional local fine-tuning on a dev PC (NVIDIA RTX 4070 Ti) applies only if accuracy on the robot camera needs improvement. Target operating distance: **20–80 cm** from the camera.

Built on a HiWonder JetRover with NVIDIA Jetson Orin Nano.

---

## What I built

- Real-time object detection on edge hardware (Jetson Orin Nano)
- ML deployment pipeline: PyTorch weights → ONNX → TensorRT FP16
- ROS 2 perception node (`cube_detection_node`) subscribing to the vendor RGB + depth streams, publishing standard `vision_msgs/Detection2DArray` and vendor `interfaces/ObjectsInfo` plus an annotated debug image
- M4c1 geometry post-filter (raised-fraction + aspect + planar-top stddev) layered on top of the YOLO output at `confidence_threshold = 0.50` — the M5 pre-ship gate for flat-color and tall-non-cube distractors in the JetRover room (5/5 testable distractors + empty scene → 622 input detections / 0 kept)
- Documented optional fine-tune path if the pretrained model underperforms on the robot camera

---

## Architecture

![Inference pipeline](assets/concept2_inference_pipeline.png)

Full pipeline details, ROS 2 topics, and training/export path → [`docs/architecture.md`](docs/architecture.md)

---

## Results

> **TODO:** Fill this section after running the pipeline on hardware and completing the 50-frame evaluation.

### Summary

<!-- One short paragraph: did it work, what accuracy/fps achieved, any fine-tuning needed -->

_TBD — add after project completion._

### Metrics

| Metric | Target | Result |
|--------|--------|--------|
| Classification accuracy | ≥ 80% (50-frame test) | TBD |
| Inference rate | ≥ 5 fps on Jetson | TBD |
| Operating distance | 20–80 cm | TBD |

### Demo

<!-- Optional TODO: add assets/results/detection_screenshot.png and uncomment the line below -->

<!-- ![Live detection with bounding boxes](assets/results/detection_screenshot.png) -->

_Screenshot or clip of live detections — add here after Milestone 5/6._

_Evaluation protocol and per-class breakdown: [`docs/evaluation.md`](docs/evaluation.md)_

---

## Requirements

| | Jetson (robot) | Dev machine |
|--|----------------|-------------|
| **Role** | Runs detection | Edit code, optional fine-tune, visualize (RViz2) |
| **OS / ROS / Python** | 22.04 / Humble / 3.10 | 22.04 / Humble / 3.10 |
| **Hardware** | JetRover, Orbbec depth camera | NVIDIA RTX 4070 Ti (CUDA training) |
| **Key software** | TensorRT, YOLOv5, OpenCV, cv_bridge | PyTorch + CUDA, RViz2 (optional) |

Full dependencies and model artifacts → [`docs/technical-stack.md`](docs/technical-stack.md)

---

## Quick Start

> **Note:** Inference is not live yet. Below: how to build the package today, and the intended workflow on the Jetson once the model and node are implemented.

### Build the package (dev machine — works now)

```zsh
cd ~/maher_ws
colcon build --packages-select recognition_of_different_colored_cubes
source install/setup.bash
ros2 run recognition_of_different_colored_cubes cube_detection_node
```

Expected: node logs a scaffold initialization message. Exits cleanly on Ctrl+C.

### Run on the Jetson (after model + node are implemented)

```zsh
ssh ubuntu@192.168.2.138   # DHCP — update if changed

sudo systemctl stop start_app_node.service

cd ~/jetson_ws/src
git clone <repo-url> Recognition-of-Different-Colored-Cubes

cd ~/jetson_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select recognition_of_different_colored_cubes --symlink-install
source install/setup.bash

# 1. Start the vendor camera bringup (depth camera + RGB + color-registered depth)
export need_compile=True
export MACHINE_TYPE=JetRover_Mecanum
export LIDAR_TYPE=LD19
export HOST=/
export MASTER=
export DEPTH_CAMERA_TYPE=Dabai
ros2 launch peripherals depth_camera.launch.py &

# 2. Verify the two upstream topics before starting the detector
ros2 topic hz /depth_cam/rgb/image_raw
ros2 topic hz /depth_cam/depth/image_raw
ros2 topic info /depth_cam/rgb/camera_info -v

# 3. Start the cube detector (loads models/best.engine + M4c1 geometry filter)
ros2 launch recognition_of_different_colored_cubes detection.launch.py
```

View detections: `ros2 run rqt_image_view rqt_image_view` → topic `/cube_detections/debug_image`.

#### M5 runtime parameters (tunable at runtime)

All of these are declared via `rclpy` and can be inspected or changed with `ros2 param get / cube_detection_node <name>` / `ros2 param set /cube_detection_node <name> <value>`. Defaults live in [`config/params.yaml`](config/params.yaml).

| Parameter | Default | Purpose |
|---|---|---|
| `image_topic` | `/depth_cam/rgb/image_raw` | Vendor RGB input |
| `depth_topic` | `/depth_cam/depth/image_raw` | Vendor color-registered depth (uint16 mm) |
| `rgb_camera_info_topic` | `/depth_cam/rgb/camera_info` | Source of `fx/fy/cx/cy` (overridden at startup) |
| `detections_topic` | `/cube_detections` | `vision_msgs/Detection2DArray` |
| `vendor_objects_topic` | `/cube_detections/vendor_objects` | `interfaces/ObjectsInfo` |
| `debug_image_topic` | `/cube_detections/debug_image` | Annotated overlay |
| `model_path` | `""` (auto → `<pkg>/models/best.engine`) | TensorRT FP16 engine |
| `confidence_threshold` | `0.50` | M4c1 deployment target; below this is dropped before geometry |
| `iou_threshold` | `0.45` | NMS IoU |
| `imgsz` | `640` | Letterbox square |
| `sync_slop_sec` | `0.05` | RGB+depth sync tolerance (50 ms median target) |
| `filter_enabled` | `true` | Master switch for the M4c1 geometry filter |
| `filter_raised_mm` | `30` | How many mm above the annulus floor counts as "raised" |
| `filter_min_raised_frac` | `0.20` | Minimum fraction of raised in-box pixels |
| `filter_max_ratio` | `1.2` | Max 3D extent long/short ratio |
| `filter_max_planar_top_stddev_mm` | `30` | Max stddev of raised subset depth (flat top test) |
| `filter_inset_px` | `1` | Pixels inset from the YOLO bbox before sampling |
| `filter_annulus_outer_px` | `15` | Annulus outer extent (floor reference) |
| `latency_log_every` | `100` | Frames between p50/p95 latency log lines |

Full reasoning behind every default and the V2/V3/V4 evidence gate → [`docs/milestones.md`](docs/milestones.md) M5 + [`evaluation/m4c_geometry_filter/report.md`](evaluation/m4c_geometry_filter/report.md).

### Verify camera (first hardware step)

```zsh
ros2 topic list
ros2 topic hz /depth_cam/rgb/image_raw
ros2 run rqt_image_view rqt_image_view
```

Full ordered setup steps → [`docs/milestones.md`](docs/milestones.md)

---

## Key Directories

| Path | Purpose |
|------|---------|
| `recognition_of_different_colored_cubes/` | ROS 2 Python package — `cube_detection_node.py` |
| `launch/` | `detection.launch.py` |
| `config/` | Node parameters (`params.yaml`) |
| `scripts/` | ONNX export, TensorRT conversion, standalone inference test |
| `models/` | `best.pt`, `best.onnx`, `.engine` — gitignored, not committed |
| `training/` | Optional local fine-tune notebook (`train.ipynb`) |
| `evaluation/` | 50-frame structured test script |
| `assets/` | Pipeline diagrams; `assets/results/` for evaluation screenshots |
| `docs/` | Architecture, milestones, logbook, evaluation protocol |
| `vendor/` | Reference notes for Hiwonder vendor code (not copied) |

Browse the full tree on GitHub — this table only highlights non-obvious layout.

---

## Documentation

### For visitors

| Document | Description |
|----------|-------------|
| [`docs/architecture.md`](docs/architecture.md) | How the pipeline works — topics, node, diagrams |
| [`docs/Concept-and-Approach.md`](docs/Concept-and-Approach.md) | Why YOLOv5 + TensorRT; model strategy |
| [`docs/evaluation.md`](docs/evaluation.md) | How results are measured |

### Development notes

| Document | Description |
|----------|-------------|
| [`docs/project-definition.md`](docs/project-definition.md) | Problem definition, classes, constraints |
| [`docs/technical-stack.md`](docs/technical-stack.md) | Runtime stack, dependencies, model artifacts |
| [`docs/milestones.md`](docs/milestones.md) | Implementation milestones and ordered steps |
| [`docs/LOGBOOK.md`](docs/LOGBOOK.md) | Session-by-session development log |

---

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
