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
- M4c1 geometry post-filter (raised-fraction + aspect + planar-top stddev) layered on top of the YOLO output at `confidence_threshold = 0.50` — gates flat-color and tall-non-cube distractors in the JetRover room (5/5 testable distractors + empty scene → 622 input detections / 0 kept, replicated live 2026-06-28)
- Documented fine-tune path: the active next step is M3d-revived (positive fine-tune on real JetRover-room cubes) — see [`docs/m3d-revived-plan.md`](docs/m3d-revived-plan.md) and "Current status" under [Results](#results) below

---

## Architecture

![Inference pipeline](assets/concept2_inference_pipeline.png)

Full pipeline details, ROS 2 topics, and training/export path → [`docs/architecture.md`](docs/architecture.md)

---

## Results

### Current status — M5 PARTIAL

The M5 ROS 2 node and the M4c1 geometry filter are **implemented and live on
the Jetson**: 29 runtime parameters, TensorRT FP16 engine loads, sync
p50 within `sync_slop_sec = 0.05`. The geometry filter cleanly
suppresses flat-color and tall-non-cube distractors in the JetRover room
(empty scene: KEEP=0/439 at conf=0.50, no false positives).

The blocker is **model accuracy on real JetRover-room cubes** — at conf=0.50
the model fires only on floor texture, not on the actual cubes (M5c:
KEEP=0/414 with sticker on; M5c2: KEEP=0/460 with sticker removed). At
conf=0.25 the model partially responds (green_cube only, 2/439). The
geometry filter cannot fix this — it is a model-accuracy issue, not a
filter issue.

**M5 acceptance is PARTIAL. Next step:** fine-tune `models/best.pt` on
real JetRover-room positives per [`docs/m3d-revived-plan.md`](docs/m3d-revived-plan.md),
then re-run the M5c2 bag and re-check the M5 acceptance bar. Full
evidence: [`evaluation/m5_live/report.md`](evaluation/m5_live/report.md).

### Live numbers (M5, 2026-06-28)

| Bag | KEEP at conf=0.50 | YOLO p50 | Filter p50 | Publish rate |
|---|---|---|---|---|
| Empty scene | 0/439 ✅ PASS | 26.6 ms | 1.53 ms | 15.78 Hz |
| Cubes in frame (sticker on) | 0/414 ❌ FAIL | 26.6 ms | 2.57 ms | 15.52 Hz |
| Cubes in frame (sticker off) | 0/460 ❌ FAIL | 26.6 ms | 1.27 ms | 15.86 Hz |
| Cubes (sticker off, conf=0.25) | 2/439 (green only) ❌ FAIL | 26.6 ms | 4.83 ms | 15.21 Hz |

50-frame per-class evaluation is pending the M3d-revived fine-tune.

### Demo

Annotated debug overlays from the 2026-06-28 live bags live at
[`evaluation/m5_live/empty_2026-06-28/preview/debug_overlay.png`](evaluation/m5_live/empty_2026-06-28/preview/debug_overlay.png)
(empty scene, HUD `keep=0` — no false positives on the bare JetRover floor)
and [`evaluation/m5_live/cubes_2026-06-28/peek_debug_live.png`](evaluation/m5_live/cubes_2026-06-28/peek_debug_live.png)
(three cubes visible in the RGB frame, HUD `keep=0` at conf=0.50 — the
filter is correctly rejecting; the model is the bottleneck, see above).

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

The detection node runs live on the Jetson. The M4c1 geometry filter is
on by default; flip `filter_enabled` to `false` to bypass it for
debugging. **Heads-up: M5 acceptance is PARTIAL — the model does not
yet fire on real cubes in the JetRover room at conf≥0.50.** See the
"Current status" subsection under [Results](#results) below for the
2026-06-28 live-bag numbers and the next step (M3d-revived fine-tune).

### Build the package (dev machine — works now)

```zsh
cd ~/maher_ws
colcon build --packages-select recognition_of_different_colored_cubes --symlink-install
source install/setup.bash
```

### Run on the Jetson (live)

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

All of these are declared via `rclpy` and can be inspected or changed at runtime:

```zsh
ros2 param get /cube_detection_node confidence_threshold
ros2 param set /cube_detection_node confidence_threshold 0.25   # takes effect on the next frame
ros2 param set /cube_detection_node filter_enabled false       # bypass geometry filter entirely
```

Defaults live in [`config/params.yaml`](config/params.yaml).

**Topics**

| Parameter | Default | Purpose |
|---|---|---|
| `image_topic` | `/depth_cam/rgb/image_raw` | Vendor RGB input the node YOLO-infers on |
| `depth_topic` | `/depth_cam/depth/image_raw` | Vendor color-registered depth (uint16 mm) the geometry filter samples |
| `rgb_camera_info_topic` | `/depth_cam/rgb/camera_info` | Source of `fx/fy/cx/cy` (overridden at startup from the live message) |
| `detections_topic` | `/cube_detections` | Published `vision_msgs/Detection2DArray` — kept detections only |
| `vendor_objects_topic` | `/cube_detections/vendor_objects` | Published `interfaces/ObjectsInfo` — vendor-compatible output |
| `debug_image_topic` | `/cube_detections/debug_image` | Published `sensor_msgs/Image` (bgr8) — annotated overlay for `rqt_image_view` |

**Model + inference**

| Parameter | Default | Purpose |
|---|---|---|
| `model_path` | `""` (auto → `<pkg>/models/best.engine`) | TensorRT FP16 engine. Empty means use the bundled engine from the package's `models/` directory. |
| `confidence_threshold` | `0.50` | **M4c1 deployment target.** YOLO candidates below this are dropped before geometry is even applied. |
| `iou_threshold` | `0.45` | NMS IoU threshold for duplicate suppression on the raw YOLO output. |
| `imgsz` | `640` | Square letterbox size the engine expects. |

**RGB + depth sync**

| Parameter | Default | Purpose |
|---|---|---|
| `sync_slop_sec` | `0.05` | Maximum timestamp gap between an RGB and depth message for the `ApproximateTimeSynchronizer` to pair them (50 ms — the M5 median target). |
| `sync_queue_size` | `10` | Pairwise queue depth for the synchronizer. |

**Geometry post-filter (M4c1 v2-only)**

The filter is a pure-numpy helper ([`recognition_of_different_colored_cubes/geometry_filter.py`](recognition_of_different_colored_cubes/geometry_filter.py)) that decides KEEP / REJECT per YOLO candidate using the synchronised depth image. It was validated against 622 input detections across 5 testable distractors + the empty scene with **0 kept** (M4c1 V2 PASS replicated live on the Jetson 2026-06-28, see [`evaluation/m4c_geometry_filter/report.md`](evaluation/m4c_geometry_filter/report.md)).

| Parameter | Default | Plain-language meaning |
|---|---|---|
| `filter_enabled` | `true` | Master switch. Set to `false` to publish every YOLO candidate ≥ `confidence_threshold` with no geometry check. |
| `filter_n_min` | `30` | Minimum number of valid depth pixels inside the YOLO bbox before the filter will even try to decide — below this, the detection is kept with a `low_depth_quality` reason rather than silently rejected. |
| `filter_max_depth_mm` | `4000` | Anything farther than 4 m is treated as invalid depth (kinect noise / dropouts) and excluded from the stats. |
| `filter_inset_px` | `1` | Number of pixels to shrink the YOLO bbox inward before sampling depth. Prevents the annulus from leaking in and the in-box stats from picking up edge pixels of the cube's slanted sides. |
| `filter_annulus_outer_px` | `15` | Width (in pixels) of the rectangular ring around the YOLO bbox that the filter uses as the **floor reference** (median depth of this ring becomes "ground level" for the raised test). Wider → more robust against local floor texture, narrower → tighter floor. |
| `filter_raised_mm` | `30` | "Raised" = an in-box pixel that is at least this many mm above the annulus-floor median. A cube on the floor has most of its top pixels raised; floor texture has none. |
| `filter_min_raised_frac` | `0.20` | Minimum fraction of in-box depth pixels that must be raised for the detection to even be considered a 3D object. Below this, REJECT with reason `flat` (this is what catches blue cardboard, decals, wood-grain false positives). |
| `filter_max_ratio` | `1.2` | Maximum allowed ratio of the longest to the shortest side of the raised subset's 3D bounding box. A cube gives ≈1.0; a tall bottle / bag gives >1.5. Above this, REJECT with reason `aspect`. |
| `filter_max_planar_top_stddev_mm` | `30` | Maximum allowed standard deviation of the depth values inside the raised subset (the "top" of the object). A flat cube top has ~5 mm stddev; a ball or curved package has >>30 mm. Above this, REJECT with reason `no_planar_top`. |

**Diagnostics**

| Parameter | Default | Purpose |
|---|---|---|
| `latency_log_every` | `100` | Frames between p50/p95 latency log lines (total + yolo + filter). |
| `publish_vendor_objects` | `true` | Toggle the vendor-compatible output. |
| `publish_debug_image` | `true` | Toggle the annotated debug overlay. |

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
| `recognition_of_different_colored_cubes/` | ROS 2 Python package — `cube_detection_node.py` (live node) + `geometry_filter.py` (M4c1 KEEP/REJECT helper) |
| `launch/` | `detection.launch.py` |
| `config/` | Node parameters (`params.yaml`) |
| `scripts/` | Capture, inference smoke tests, M4c/M5 eval harnesses — see [`scripts/README.md`](scripts/README.md) |
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
| [`docs/README.md`](docs/README.md) | **Start here** — documentation index (start-here / current / research / evaluation, plus current status and recommended later cleanup). |
| [`docs/architecture.md`](docs/architecture.md) | How the pipeline works — topics, node, diagrams |
| [`docs/Concept-and-Approach.md`](docs/Concept-and-Approach.md) | Why YOLOv5 + TensorRT; model strategy |
| [`docs/evaluation.md`](docs/evaluation.md) | How results are measured |

### Development notes

| Document | Description |
|----------|-------------|
| [`docs/project-definition.md`](docs/project-definition.md) | Problem definition, classes, constraints |
| [`docs/technical-stack.md`](docs/technical-stack.md) | Runtime stack, dependencies, model artifacts |
| [`docs/milestones.md`](docs/milestones.md) | Implementation milestones and ordered steps |
| [`docs/m3d-revived-plan.md`](docs/m3d-revived-plan.md) | Active fine-tune plan (M3d-revived, positive-detection scope) |
| [`docs/LOGBOOK.md`](docs/LOGBOOK.md) | Session-by-session development log |

### Script index

| Index | What it covers |
|-------|----------------|
| [`scripts/README.md`](scripts/README.md) | Table of every tracked script with category + one-line role. |

---

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
