# Vendor-first audit: colored-cube recognition

Task: Stage 2 audit of the HiWonder/JetRover vendor stack before continuing implementation of `Recognition-of-Different-Colored-Cubes`.

Constraint: use HiWonder vendor packages under `src/vendor` as the foundation whenever practical, but do not modify `src/vendor`.

## Sources audited

Local vendor/project sources:

- `AGENTS.md`
- `src/vendor/README.md`
- `src/vendor/peripherals/README.md`
- `src/vendor/peripherals/launch/depth_camera.launch.py`
- `src/vendor/peripherals/launch/usb_cam.launch.py`
- `src/vendor/peripherals/launch/include/dabai_dcw.launch.py`
- `src/vendor/peripherals/config/usb_cam_param.yaml`
- `src/vendor/peripherals/config/camera_info.yaml`
- `src/vendor/interfaces/README.md`
- `src/vendor/interfaces/msg/ObjectInfo.msg`
- `src/vendor/interfaces/msg/ObjectsInfo.msg`
- `src/vendor/interfaces/msg/ColorInfo.msg`
- `src/vendor/interfaces/msg/ColorsInfo.msg`
- `src/vendor/interfaces/msg/ColorDetect.msg`
- `src/vendor/interfaces/msg/ROI.msg`
- `src/vendor/interfaces/srv/SetColorDetectParam.srv`
- `src/vendor/interfaces/srv/SetCircleROI.srv`
- `src/vendor/interfaces/srv/SetLineROI.srv`
- `src/vendor/example/README.md`
- `src/vendor/example/example/color_detect/`
- `src/vendor/example/example/color_track/`
- `src/vendor/example/example/color_sorting/`
- `src/vendor/example/example/yolov5_detect/yolov5_node.py`
- Current project docs under `src/Recognition-of-Different-Colored-Cubes/docs/`

External source already cited in the project docs:

- Roboflow cube dataset / pretrained model source: https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1

## 1. Correct vendor package(s) for RGB image input

Use the vendor `peripherals` package for camera bring-up.

Relevant launch files:

- `src/vendor/peripherals/launch/depth_camera.launch.py`
  - Top-level camera launch for the JetRover camera path.
  - Requires `need_compile` and `DEPTH_CAMERA_TYPE` in the environment.
  - If `DEPTH_CAMERA_TYPE == 'Dabai'`, includes `launch/include/dabai_dcw.launch.py` for the Orbbec/Dabai depth camera.
  - Otherwise falls back to `usb_cam.launch.py` and publishes a static transform from `depth_cam_link` to `depth_cam_color_frame`.

- `src/vendor/peripherals/launch/include/dabai_dcw.launch.py`
  - Starts `orbbec_camera::OBCameraNodeDriver` in a composable node container.
  - Default `camera_name` is `depth_cam`.
  - Remaps Orbbec color topics to the vendor RGB namespace:
    - `/<camera_name>/color/image_raw` -> `/<camera_name>/rgb/image_raw`
    - `/<camera_name>/color/camera_info` -> `/<camera_name>/rgb/camera_info`
    - `/<camera_name>/color/image_raw/compressed` -> `/<camera_name>/rgb/image_raw/compressed`
    - `/<camera_name>/depth/color/points` -> `/<camera_name>/depth_registered/points`

- `src/vendor/peripherals/launch/usb_cam.launch.py`
  - Starts `usb_cam` with `config/usb_cam_param.yaml`.
  - Remaps `image_raw` to `/depth_cam/rgb/image_raw` and `camera_info` to `/depth_cam/rgb/camera_info`.
  - Even for a USB camera fallback, the project can keep subscribing to the same RGB topic.

Required environment before vendor launches in this workspace:

```bash
cd ~/maher_ws
source install/setup.bash
export need_compile=True
export MACHINE_TYPE=JetRover_Mecanum
export LIDAR_TYPE=LD19
export HOST=/
export MASTER=
export DEPTH_CAMERA_TYPE=Dabai   # for the JetRover Orbbec/Dabai depth camera path
```

Notes:

- `AGENTS.md` and `src/vendor/README.md` both warn that `need_compile=True` is mandatory in `maher_ws`; otherwise vendor launches fall back to `/home/ubuntu/ros2_ws/...` paths.
- `DEPTH_CAMERA_TYPE` has no default in `depth_camera.launch.py`; failing to set it will raise an environment lookup error.
- The current project docs already assume an Orbbec depth camera and `/depth_cam/rgb/image_raw`, which matches the vendor remaps.

## 2. Likely live RGB topics and hardware verification

Likely RGB topics:

- Primary raw RGB image: `/depth_cam/rgb/image_raw`
- Camera calibration: `/depth_cam/rgb/camera_info`
- Compressed RGB image, Orbbec path: `/depth_cam/rgb/image_raw/compressed`
- Compressed RGB image, USB fallback path: `/depth_cam/rgb/image_compressed`
- Registered point cloud, Orbbec path: `/depth_cam/depth_registered/points`

The project should treat `/depth_cam/rgb/image_raw` as the expected input, but verify it on hardware before implementation work continues.

Recommended hardware verification sequence on the Jetson:

```bash
sudo systemctl stop start_app_node.service
cd ~/jetson_ws
source install/setup.bash
export need_compile=True
export MACHINE_TYPE=JetRover_Mecanum
export LIDAR_TYPE=LD19
export HOST=/
export MASTER=
export DEPTH_CAMERA_TYPE=Dabai

ros2 launch peripherals depth_camera.launch.py
```

In another terminal:

```bash
cd ~/jetson_ws
source install/setup.bash
ros2 topic list | sort
ros2 topic info /depth_cam/rgb/image_raw -v
ros2 topic hz /depth_cam/rgb/image_raw
ros2 topic echo /depth_cam/rgb/camera_info --once
ros2 run rqt_image_view rqt_image_view
```

What to confirm:

- `/depth_cam/rgb/image_raw` exists and publishes `sensor_msgs/msg/Image`.
- QoS is compatible with a perception subscriber. For image subscribers, prefer `rclpy.qos.qos_profile_sensor_data` or an equivalent best-effort sensor QoS unless the topic info shows reliable-only behavior.
- Frame size/fps are plausible. The Dabai launch defaults color to `640x360 @ 30 fps`; the USB fallback config is `640x480 @ 30 fps`.
- `rqt_image_view` can display the RGB stream.

## 3. Vendor color detect / track / sorting behavior

### `color_detect`

Files:

- `src/vendor/example/example/color_detect/color_detect_node.launch.py`
- `src/vendor/example/example/color_detect/color_detect_node.py`
- `src/vendor/example/example/color_detect/color_detect_demo.py`

Launch behavior:

- `color_detect_node.launch.py` includes `peripherals/launch/depth_camera.launch.py` and then starts executable `example/color_detect` as node name `color_detect`.
- It loads `example/config/roi.yaml` and launch parameters `enable_display` and `enable_roi_display`.

Node behavior:

- Subscribes to `/depth_cam/rgb/image_raw`.
- Converts ROS images to OpenCV BGR via `cv_bridge`.
- Uses a bounded queue of size 2 and drops the oldest frame when full. This is a useful real-time pattern to reuse.
- Reads LAB thresholds from `/home/ubuntu/software/lab_tool/lab_config.yaml`.
- Chooses `camera_type = 'Stereo'` when `DEPTH_CAMERA_TYPE == 'Dabai'`, otherwise `Mono`.
- Segments configured colors in LAB, applies Gaussian blur, erosion, dilation, contour extraction, and largest-contour selection.
- Supports detect types: `line`, `rect`, and circle/default behavior.
- Publishes:
  - `~/color_info` -> with node name `color_detect`, this resolves to `/color_detect/color_info`, type `interfaces/ColorsInfo`.
  - `~/image_result` -> `/color_detect/image_result`, type `sensor_msgs/Image`.
- Services:
  - `~/start` and `~/stop`, type `std_srvs/Trigger`.
  - `~/set_param`, type `interfaces/SetColorDetectParam`.
  - `~/set_line_roi`, type `interfaces/SetLineROI`.
  - `~/set_circle_roi`, type `interfaces/SetCircleROI`.
  - `~/set_rect_roi`, implemented with `SetCircleROI` shape despite the name.

Reusable ideas:

- Vendor-confirmed camera topic and `cv_bridge` conversion path.
- Bounded frame queue that drops stale frames.
- Debug image publisher pattern.
- Runtime services for start/stop and ROI/target updates.
- LAB calibration is useful as a baseline check for lighting/camera health, but it does not detect cube shape.

### `color_track`

Files:

- `src/vendor/example/example/color_track/color_track_node.launch.py`
- `src/vendor/example/example/color_track/color_track_node.py`

Launch behavior:

- Starts controller (`driver/controller/launch/controller.launch.py`), kinematics (`driver/kinematics/launch/kinematics_node.launch.py`), color detection, then `example/color_track`.

Node behavior:

- Subscribes to `/color_detect/color_info` (`interfaces/ColorsInfo`).
- Calls `/color_detect/set_param` to request one target color as `ColorDetect(color_name=<color>, detect_type='circle')`.
- Uses PID control on detected blob center (`ColorInfo.x`, `ColorInfo.y`) to move the arm/pan joint and maintain target alignment.
- Publishes chassis zero commands to `/controller/cmd_vel` and servo commands through `servo_controller_msgs/ServosPosition`.
- Services:
  - `~/start`, `~/stop`, `~/set_color`.

Reusable ideas:

- Shows how downstream nodes consume `/color_detect/color_info` and command vendor services.
- Shows service-driven configuration of the detector.
- Not directly part of cube recognition unless later manipulation/tracking is added.

### `color_sorting`

Files:

- `src/vendor/example/example/color_sorting/color_sorting_node.launch.py`
- `src/vendor/example/example/color_sorting/color_sorting_node.py`

Launch behavior:

- Starts controller, color detection, and `example/color_sorting` with `example/config/color_sorting_roi.yaml`.

Node behavior:

- Subscribes to:
  - `/color_detect/color_info` (`interfaces/ColorsInfo`)
  - `/color_detect/image_result` (`sensor_msgs/Image`)
- Calls:
  - `/color_detect/set_circle_roi` (`interfaces/SetCircleROI`) to limit detection to the pick area.
  - `/color_detect/set_param` (`interfaces/SetColorDetectParam`) to detect red, green, and blue as circles.
- Uses stability gating: the object center must remain inside the pick ROI for more than 30 cycles before triggering a pick.
- Executes vendor arm action groups (`pick`, `place_center`, `place_left`, `place_right`) by color.
- Optional voice feedback uses `xf_mic_asr_offline`.

Reusable ideas:

- ROI narrowing before acting on detections.
- Temporal stability gate before triggering robot actions.
- Clear separation between detection output and downstream behavior.
- Useful pattern for a future pick-and-place phase, but not needed for the current recognition-only project.

## 4. Relevant vendor `interfaces` messages/services

Most relevant for cube recognition:

- `interfaces/ObjectInfo.msg`
  - Fields: `class_name`, `box`, `score`, `width`, `height`.
  - `box` is `[x_min, y_min, x_max, y_max]`.
  - This is the vendor object-detection result shape.

- `interfaces/ObjectsInfo.msg`
  - Field: `ObjectInfo[] objects`.
  - This is the vendor array wrapper used by `example/yolov5_detect/yolov5_node.py` on `~/object_detect`.

- `interfaces/ColorInfo.msg`
  - Fields: `color`, `width`, `height`, `x`, `y`, `radius`, `angle`.
  - Relevant only for color-blob baseline/reference behavior.

- `interfaces/ColorsInfo.msg`
  - Field: `ColorInfo[] data`.
  - Published by `/color_detect/color_info`.

- `interfaces/ColorDetect.msg`
  - Fields: `color_name`, `detect_type`.
  - Used to configure vendor color detection targets.

- `interfaces/ROI.msg`, `SetCircleROI.srv`, `SetLineROI.srv`, `SetColorDetectParam.srv`
  - Useful if reusing or wrapping the vendor color detector for calibration/baseline tests.

Also relevant even though it is not a color demo:

- `src/vendor/example/example/yolov5_detect/yolov5_node.py`
  - Subscribes to `/depth_cam/rgb/image_raw`.
  - Runs a TensorRT YOLOv5 wrapper.
  - Publishes `interfaces/ObjectsInfo` on `~/object_detect`, which resolves to `/yolov5/object_detect` for node name `yolov5`.
  - Publishes a debug/result image on `~/object_image` (`/yolov5/object_image`).
  - This is the strongest vendor reference for the current project's intended YOLOv5 + TensorRT path.

## 5. Output message recommendation: `vision_msgs/Detection2DArray`, vendor `ObjectsInfo`, or both?

Recommendation: publish both, with `vision_msgs/Detection2DArray` as the primary public project API and `interfaces/ObjectsInfo` as a vendor-compatibility output.

Rationale:

- Keep `/cube_detections` as `vision_msgs/Detection2DArray` because the existing project docs, architecture, and portfolio goal already specify a standard ROS 2 vision message. It is the better external integration contract.
- Add a vendor-shaped topic such as `/cube_detections/vendor_objects` or `/cube_objects` using `interfaces/ObjectsInfo` so future JetRover vendor demos or downstream nodes can consume detections without a custom adapter.
- The vendor YOLOv5 node already maps TensorRT detections to `interfaces/ObjectInfo`; reusing that shape is vendor-first without forcing the whole project to abandon standard ROS 2 messages.
- Do not publish only `ObjectsInfo`: it loses compatibility with standard ROS 2 vision tooling and would require updating the current documentation and any RViz/future consumers that expect `vision_msgs`.
- Do not publish only `Detection2DArray`: it ignores the vendor object-detection contract already present in `interfaces`.

Suggested topic split:

| Topic | Type | Purpose |
|---|---|---|
| `/cube_detections` | `vision_msgs/Detection2DArray` | Primary standard API |
| `/cube_detections/debug_image` | `sensor_msgs/Image` | Human visualization |
| `/cube_detections/vendor_objects` | `interfaces/ObjectsInfo` | JetRover/vendor compatibility |

## 6. Vendor color detection recommendation

Recommendation: use vendor color detection as a reference and optional baseline/fallback diagnostic, not as the main recognition path.

Why not main path:

- The project problem is to detect colored cubes as complete objects and distinguish cubes from non-cube colored regions.
- Vendor `color_detect` is LAB thresholding plus contour geometry. It detects colored blobs/lines/rectangles/circles, not learned cube objects.
- Current project constraints explicitly select YOLOv5 + TensorRT and state that classical color segmentation is not the primary detector.
- Lighting and LAB threshold tuning are known fragile points; the vendor README says demo configs are tuned to sample environments and should be expected to need retuning.

Where vendor color detection is still useful:

- Camera bring-up validation: proves `/depth_cam/rgb/image_raw`, `cv_bridge`, and debug image display are working.
- Lighting sanity check: if LAB thresholds fail badly, the YOLO model may also see poor color separation.
- Baseline metric: compare YOLO against a simple vendor color detector to show why learned object detection is better for cube recognition.
- Future manipulation: `color_sorting` has useful ROI/stability/action patterns if the project later adds pick-and-place.

More vendor-first main-path reference:

- Use `example/yolov5_detect/yolov5_node.py` as the implementation reference for the main path, not `color_detect`.
- It already demonstrates: subscribe to `/depth_cam/rgb/image_raw`, TensorRT inference wrapper, bounded queue, debug image publishing, and `interfaces/ObjectsInfo` output.

## 7. Risks and next research/architecture handoff notes

Risks:

- Environment variables are easy to miss: `need_compile` and `DEPTH_CAMERA_TYPE` are hard requirements for camera launch.
- Topic names should not be assumed until verified on the Jetson. The vendor launch remaps strongly indicate `/depth_cam/rgb/image_raw`, but hardware verification is still required.
- Vendor color detection is not equivalent to cube recognition; using it as the main detector would violate the project definition.
- Vendor YOLOv5 assets are present, but the existing project uses a Roboflow cube model. The architect/implementer should decide how much of the vendor `yolov5_trt.py` wrapper can be reused safely without copying brittle absolute paths.

Recommended next-stage handoff:

- Architecture/implementation should build around `peripherals/depth_camera.launch.py` and `/depth_cam/rgb/image_raw`.
- Main detector should remain YOLOv5 + TensorRT.
- Add `interfaces` as a dependency if the project publishes vendor-compatible `ObjectsInfo`.
- Keep vendor source read-only. If code reuse from `example/yolov5_detect` is needed, copy/adapt into the project package rather than editing `src/vendor`.
