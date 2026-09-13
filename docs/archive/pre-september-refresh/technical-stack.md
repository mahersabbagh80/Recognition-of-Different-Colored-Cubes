> Historical snapshot preserved on 13 September 2026. Superseded by the current page under docs/.

# Technical Stack

This stack is revised for the vendor-first JetRover requirement: HiWonder packages under `src/vendor` provide camera bring-up and the vendor compatibility message contract; this project provides the cube-recognition package and must not modify vendor source.

Primary architecture reference: [`architecture.md`](../../architecture.md). Vendor audit: [`vendor-audit.md`](../../vendor-audit.md). M2 model-source research: [`archive/model-options.md`](../model-options.md).

---

## On-Robot Runtime (Jetson Orin Nano)

| Component | Version / Notes | Role |
|---|---|---|
| OS | Ubuntu 22.04 LTS | Jetson / ROS 2 base OS |
| NVIDIA SDK | JetPack, exact version to verify on Jetson | CUDA/cuDNN/TensorRT runtime |
| ROS 2 | Humble | Middleware and launch system |
| Python | 3.10 | `ament_python` node runtime |
| HiWonder `peripherals` | from `src/vendor/peripherals` | Vendor camera bring-up; publishes `/depth_cam/rgb/image_raw` |
| HiWonder `interfaces` | from `src/vendor/interfaces` | Vendor `ObjectsInfo` / `ObjectInfo` output contract |
| OpenCV | Jetson/system package | Frame handling and debug overlay drawing |
| `cv_bridge` | ROS package | `sensor_msgs/Image` ↔ OpenCV conversion |
| `vision_msgs` | ROS package | Standard `Detection2DArray` public output |
| TensorRT | JetPack-provided | FP16 inference engine, primary backend |
| ONNX Runtime | optional fallback | Slower fallback if TensorRT conversion fails |

Environment requirements before launching vendor camera stack:

```bash
cd ~/maher_ws
source install/setup.bash
export need_compile=True
export MACHINE_TYPE=JetRover_Mecanum
export LIDAR_TYPE=LD19
export HOST=/
export MASTER=
export DEPTH_CAMERA_TYPE=Dabai
```

`need_compile=True` and `DEPTH_CAMERA_TYPE=Dabai` are not optional for the vendor camera path in this workspace. Without `need_compile=True`, vendor launch files fall back to `/home/ubuntu/ros2_ws/...` paths.

---

## Vendor packages used directly

| Vendor package | How this project uses it | Why |
|---|---|---|
| `peripherals` | Start the Orbbec/Dabai or USB camera through `peripherals/launch/depth_camera.launch.py`; consume `/depth_cam/rgb/image_raw` | Keeps camera ownership in the HiWonder stack and matches vendor topic conventions |
| `interfaces` | Publish `/cube_detections/vendor_objects` as `interfaces/ObjectsInfo` | Enables JetRover/vendor-style consumers to use cube detections without an adapter |
| `example/yolov5_detect` | Reference only; do not depend on it as runtime package code | Shows vendor-proven YOLOv5 + TensorRT + `ObjectsInfo` pattern |
| `example/color_detect`, `color_track`, `color_sorting` | Reference/baseline/diagnostic only | Useful for camera/lighting checks and future manipulation patterns, not the main cube detector |

Do not modify `src/vendor`. If the implementer needs code from a vendor example, copy/adapt the relevant pattern into this project package rather than editing vendor files.

---

## Model Export Chain

```text
PyTorch YOLOv5s weights (`best.pt`)
    -> ONNX (`best.onnx`)
    -> TensorRT FP16 engine (`best.engine`) on Jetson
```

Verify PyTorch, ONNX, CUDA, and TensorRT versions on the Jetson before export/conversion to avoid version mismatch failures.

Fallback: ONNX Runtime inference if TensorRT conversion fails. This is slower and should be treated as a temporary path to keep development moving, not the target deployment state.

---

## Model Weights (M2 decision gate)

See [`archive/model-options.md`](../model-options.md) for the M2 source decision. The earlier assumption that Roboflow Universe would expose a public YOLOv5 `best.pt` is not safe: the visible pages expose hosted Detection API access and dataset exports, while raw weight download appears account/plan-gated.

| Step | Where | Action |
|---|---|---|
| 1 | Roboflow Universe / Maher's account | Check whether the selected model version exposes a raw compatible weights download (`.pt` preferred) |
| 2 | If raw weights are available | Save the selected artifact locally as `models/best.pt` and record source/version/license |
| 3 | If raw weights are not available | Download the approved YOLOv5-format dataset and fine-tune YOLOv5s locally to create a project-owned `models/best.pt` |
| 4 | Dev PC or Jetson | Export `best.pt` -> `best.onnx` in M3 |
| 5 | Jetson | Convert `best.onnx` -> TensorRT FP16 `.engine` in M4 |

No custom robot-image collection is required upfront. Add robot camera images only if standalone M4 inference fails the accuracy target.

---

## Dev Machine Training (optional fallback)

Use only if standalone inference on robot camera images is below target accuracy.

| Component | Role |
|---|---|
| NVIDIA RTX 4070 Ti | Local CUDA GPU for fine-tuning |
| PyTorch + CUDA | Training framework |
| YOLOv5 (Ultralytics) | Object detection model (YOLOv5s) |
| ONNX | Export intermediate format |
| Roboflow | Pretrained weights and YOLOv5-format dataset |

Fine-tune recipe: Roboflow dataset, 20–30 epochs on dev PC. Add robot camera images only if accuracy is still below 80% after fine-tuning.

Training notebook: [`training/train.ipynb`](../../../training/train.ipynb) (optional fallback).

---

## ROS 2 Package Dependencies

Declared dependencies for `recognition_of_different_colored_cubes` should be:

| Dependency | Current? | Required action | Reason |
|---|---:|---|---|
| `rclpy` | yes | keep | Python ROS 2 node |
| `sensor_msgs` | yes | keep | Image input and debug image output |
| `vision_msgs` | yes | keep | Primary `Detection2DArray` output |
| `cv_bridge` | yes | keep | ROS image to OpenCV conversion |
| `std_msgs` | yes | keep | General ROS std dependency; useful for headers/helpers |
| `interfaces` | no | add as `exec_depend` | Vendor `ObjectsInfo` compatibility output |

Recommended manifest change for the implementer when code publishing `ObjectsInfo` is added:

```xml
<exec_depend>interfaces</exec_depend>
```

The package can remain `ament_python`; adding `interfaces` does not require converting this project to `ament_cmake` because the project consumes vendor-generated messages rather than defining new messages.

---

## Python / system dependencies not represented cleanly in `package.xml`

These are environment-managed rather than normal ROS package dependencies:

| Environment | Dependencies |
|---|---|
| Jetson runtime | OpenCV, TensorRT, CUDA/cuDNN, PyTorch/YOLOv5 runtime pieces needed by the chosen inference wrapper, optional ONNX Runtime |
| Dev PC export/training | PyTorch + CUDA, YOLOv5, ONNX, optional Roboflow tooling |
| Visualization | RViz2, `rqt_image_view` |

Do not commit model artifacts or large generated engines. Store runtime model files in `models/` (gitignored):

| File | Description |
|---|---|
| `best.pt` | PyTorch weights (Roboflow pretrained or fine-tuned) |
| `best.onnx` | ONNX export |
| `best.engine` | TensorRT FP16 engine |

---

## Launch strategy

Recommended default launch:

- `launch/detection.launch.py` starts only `cube_detection_node`.
- It assumes `/depth_cam/rgb/image_raw` is already being published by the vendor camera stack.

Optional convenience launch, after Maher approves the workflow:

- `launch/detection_with_vendor_camera.launch.py` includes `peripherals/launch/depth_camera.launch.py`, then starts `cube_detection_node`.
- It must document the required environment variables and fail clearly if they are missing.

Reason for split: vendor camera launch is robot infrastructure with strict environment requirements; detection should remain independently runnable for testing against live camera, bags, or saved-image adapters.

---

## Output contract stack choice

Publish both outputs:

| Contract | Type | Use |
|---|---|---|
| Standard ROS vision | `vision_msgs/Detection2DArray` | Primary public API, RViz/future ROS tooling |
| Vendor compatibility | `interfaces/ObjectsInfo` | HiWonder/JetRover-style downstream consumers |

This adds the `interfaces` dependency, but it is the cleanest compromise between portability and the project-level vendor-first requirement.

---

## Verification commands for the implementer/tester

Camera stack verification:

```bash
ros2 launch peripherals depth_camera.launch.py
ros2 topic info /depth_cam/rgb/image_raw -v
ros2 topic hz /depth_cam/rgb/image_raw
```

Detection graph verification after implementation:

```bash
ros2 launch recognition_of_different_colored_cubes detection.launch.py
ros2 topic info /cube_detections -v
ros2 topic info /cube_detections/vendor_objects -v
ros2 topic echo /cube_detections/vendor_objects --once
ros2 run rqt_image_view rqt_image_view /cube_detections/debug_image
```

---

## Decisions requiring Maher's review

1. Approve adding `interfaces` to the project manifest when the implementer adds the vendor output publisher.
2. Approve the split launch strategy: default detection-only launch, optional vendor-camera convenience launch.
3. Confirm whether the optional convenience launch should be built now or deferred until after M5 live detection works.
