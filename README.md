# Recognition of Different Colored Cubes

Detect and classify red, green, and blue cubes in real time using the JetRover onboard camera, YOLOv5, TensorRT, and ROS 2.

---

## Current state — 13 September 2026

A general pretrained YOLOv5u-small model was fine-tuned on **23 reviewed robot-camera images**, with **8 separate validation images**, and converted to TensorRT FP16 for NVIDIA Jetson hardware.

- Saved validation views: 17 of 18 cubes visibly detected, one red cube missed, no additional visible boxes.
- Live diagnostic with geometry filter disabled: all three colors detected together; an empty scene produced no detection.
- With geometry filtering enabled, the tested candidates—including real cubes—were rejected as flat. The rejection stage is known; its root cause is not yet diagnosed.
- Broad reliability, full 20–80 cm coverage, and reliable depth-based localization remain unverified.

These are development results and brief live observations. The full filtered perception pipeline is **not complete**. The new engine was selected explicitly for a temporary test; the older default engine was not replaced.

## What the project implements

The ROS 2 node consumes vendor RGB, depth and camera information, runs TensorRT detection, optionally applies geometry checks, and publishes standard and vendor-compatible detections plus a debug image. Maher captured and reviewed data, ran the training/deployment steps, and interpreted outputs; Codex assisted with code, checks and documentation. Vendor camera software and ML libraries are reused.

## Architecture and workflow

[System architecture](docs/architecture.md) · [Training and validation workflow](docs/training-and-validation-workflow.md) · [Technical stack and model identity](docs/technical-stack.md)

## Results and evidence

| Evidence | Location |
|---|---|
| Completed training and exact settings | [Saturday walkthrough](docs/development-learning-journal/2026-09-12-saturday.md) |
| Reviewed validation predictions | [Eight-image comparison](docs/validation-prediction-review-2026-09-13.md) |
| Conversion, engine checks, live observations and filter limitation | [Sunday walkthrough](docs/development-learning-journal/2026-09-13-sunday.md) |
| Current evaluation summary and remaining tests | [Evaluation](docs/evaluation.md) |
| English slides, notes and tutor questions | [Presentation package v8](artifacts/presentation/README.md) |
| Earlier June live tests | [Historical M5 report](evaluation/m5_live/report.md) |

The historical June model and filter tests must not be substituted for the September model's results.

---

## Requirements

| | Jetson (robot) | Dev machine |
|--|----------------|-------------|
| **Role** | Runs detection | Edit code, fine-tune and export, inspect results |
| **OS / ROS / Python** | 22.04 / Humble / 3.10 | 22.04 / Humble / 3.10 |
| **Hardware** | JetRover, Orbbec depth camera | NVIDIA RTX 4070 Ti (CUDA training) |
| **Key software** | TensorRT, YOLOv5, OpenCV, cv_bridge | PyTorch + CUDA, RViz2 (optional) |

Full dependencies and model artifacts → [`docs/technical-stack.md`](docs/technical-stack.md)

---

## Quick Start

The following is the September diagnostic configuration. It assumes the JetRover's vendor camera is already running, the workspace is built, and the dated engine has been transferred and verified. A Git pull does not transfer model weights.

### Build when source code changes

Run inside the intended machine's workspace (not during an active detector session):

```zsh
cd ~/maher_ws
colcon build --packages-select recognition_of_different_colored_cubes --symlink-install
source install/setup.zsh
```

### Start the tested configuration on the JetRover

In an SSH session on the robot:

```zsh
source /opt/ros/humble/setup.zsh
source /home/ubuntu/maher_ws/install/setup.zsh
ros2 run recognition_of_different_colored_cubes cube_detection_node \
  --ros-args \
  --params-file /home/ubuntu/maher_ws/src/Recognition-of-Different-Colored-Cubes/config/params.yaml \
  -p model_path:=/home/ubuntu/maher_ws/best_2026-09-12.engine \
  -p confidence_threshold:=0.25 \
  -p filter_enabled:=false
```

Open the existing web-video service at
[the debug view](http://192.168.2.138:8080/stream_viewer?topic=/cube_detections/debug_image).
The address is LAN-specific and may change with DHCP. The vendor camera and web-video service must be running. Desktop rqt topic discovery was not fully repaired; the browser was the working preview route.

Stop the foreground node with Ctrl+C before restarting it. To compare the geometry filter, restart the same command with `filter_enabled:=true`; the September test then rejected the real cubes. This is a diagnostic comparison, not an accepted production configuration.

### Parameters

Defaults live in [config/params.yaml](config/params.yaml). They still use confidence 0.50, filter enabled, and an automatic default model path. The explicit command above overrides them without changing the defaults.

The current node reads these settings during initialization. Use a restart to apply changes: `ros2 param set` alone is not a verified way to update the running detector's cached settings. Model files are local artifacts; see [model inventory](models/README.md).

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

Historical geometry-filter parameter rationale and the V2/V3/V4 evidence gate → [`docs/milestones.md`](docs/milestones.md) and [`evaluation/m4c_geometry_filter/report.md`](evaluation/m4c_geometry_filter/report.md).

### Verify camera (first hardware step)

```zsh
ros2 topic list
ros2 topic hz /depth_cam/rgb/image_raw
ros2 run rqt_image_view rqt_image_view
```

Current milestone status → [`docs/milestones.md`](docs/milestones.md)

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
| `evaluation/` | Dataset manifests, reviews and evaluation reports |
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
| [Historical fine-tune proposal](docs/archive/completed-2026-09-13/m3d-revived-plan.md) | Historical fine-tune proposal; see the current training workflow |
| [Historical logbook](docs/archive/completed-2026-09-13/LOGBOOK.md) | Session-by-session development log |

### Script index

| Index | What it covers |
|-------|----------------|
| [`scripts/README.md`](scripts/README.md) | Table of every tracked script with category + one-line role. |

---

## License

Apache-2.0 — see [`LICENSE`](LICENSE).

---

## References

- [ROS + Machine Learning Course — JetRover (Orin Nano) docs](https://docs.hiwonder.com/projects/JetRover/en/jetson-orin-nano/docs/6.ROS%2BMachine_Learning_Course.html) — official HiWonder ML + ROS tutorial; supervised-learning fundamentals and the vendor reference pattern for target detection on the JetRover.
