# M5 Live Evaluation Report — JetRover cube_detection_node

**Date:** 2026-06-28
**Card:** t_15db4d42 (M5)
**Author:** implementer
**Status:** PARTIAL — M5 node code shipped, builds clean, TensorRT engine loads on
Jetson, all 29 parameters declared + verified live. **Live bag capture is blocked
on vendor bringup state** (see §3).

---

## 0. TL;DR

The M5 ROS 2 node (`recognition_of_different_colored_cubes/cube_detection_node.py`)
replaces the previous M1/M3 scaffold placeholder with a full TensorRT FP16 inference
+ M4c1 geometry post-filter pipeline. It subscribes to `/depth_cam/rgb/image_raw` +
`/depth_cam/depth/image_raw` via `message_filters.ApproximateTimeSynchronizer`,
publishes KEEP detections on the existing triple of topics, logs per-frame
latency p50 / p95 every 100 frames, and is fully runtime-tunable via rclpy
parameters.

| Subsystem | Status | Evidence |
|---|---|---|
| Node code (29 parameters, geometry filter, TensorRT) | ✅ DONE | this report + git `cf1cf7e` |
| Geometry filter as a proper package module | ✅ DONE | `recognition_of_different_colored_cubes/geometry_filter.py` |
| Package builds clean on the Jetson | ✅ DONE | `colcon build` finished in 4.54s, exit 0 |
| TensorRT FP16 engine loads on the Jetson | ✅ DONE | live log line: `TensorRT engine loaded: in=images (1, 3, 640, 640) out=output0 (1, 7, 8400)` |
| All M4c1 v2-only params threaded through to runtime | ✅ DONE | log shows `{raised_mm: 30, min_raised_frac: 0.20, max_planar_top_stddev_mm: 30, max_ratio: 1.2, inset_px: 1, annulus_outer_px: 15}` |
| Live RGB+depth sync + 30s cubes bag | ⏸ BLOCKED | vendor depth camera stalled again (see §3) |
| Live 30s empty bag (KEEP=0 at conf=0.50) | ⏸ BLOCKED | same |

The full M5 acceptance bar (criteria 2–5 in the card body) requires Maher to
restore the vendor depth-camera publish graph; see §3 for the minimal-touch
recovery procedure and §4 for the exact 30s bag commands that go once the
camera is back online.

---

## 1. What changed in the M5 commit

| File | Lines | What it does |
|---|---|---|
| `recognition_of_different_colored_cubes/cube_detection_node.py` | 641 | Full TensorRT + geometry-filter ROS 2 node |
| `recognition_of_different_colored_cubes/geometry_filter.py` | 260 | Embeds `compute_geometry` + `decide` as a package module (clean copy of the M4c1 helpers) |
| `config/params.yaml` | 53 | 29 runtime-tunable params, M4c1 defaults baked in |
| `package.xml` | +6 deps | `message_filters`, `numpy`, `PIL`, `torch`, `torchvision` (TensorRT/pycuda are Jetson-only) |
| `README.md` | +42 | M5 launch instructions + parameter table |
| `scripts/m5_capture_bag.py` | 99 | Jetson-side `ros2 bag record` wrapper for 30s captures |
| `scripts/m5_analyze_bag.py` | 161 | Dev-PC bag analyzer: per-class kept, publish rate, RGB hz |
| `scripts/m5_offline_replay.py` | 199 | End-to-end pipeline replay on saved sync RGB+depth (parity check before live) |
| `launch/detection.launch.py` | unchanged | still launches `cube_detection_node` with `params.yaml` |

Total: +1,193 / −230 lines across 7 files (commit `f571ea1`), +257 across 3 files
(followup commit `cf1cf7e`).

### 1.1 TensorRT backend — proven inline pattern

The node uses the same inline TensorRT 8.6.2 + pycuda 2024.1 pattern that
`scripts/test_inference.py` proved reliable on the Jetson (the helper-wrapped
variant silently produced all-zero outputs, per the docstring at the top of that
file). Single binding allocation, single shared CUDA stream across frames,
`execute_async_v2` + `stream.synchronize`. On the Jetson the engine binding
`images` is (1, 3, 640, 640) float32 and the output `output0` is (1, 7, 8400)
float32 — exactly what the M4a/M4b evidence gate observed.

### 1.2 M4c1 v2-only filter params

These are the explicit parameters the M4c1 card passed on the consolidated V3+V4
re-run, now declared as ROS 2 parameters (any one of them can be flipped at
runtime via `ros2 param set /cube_detection_node <name> <value>`):

```yaml
filter_raised_mm: 30
filter_min_raised_frac: 0.20
filter_max_planar_top_stddev_mm: 30
filter_max_ratio: 1.2
filter_inset_px: 1
filter_annulus_outer_px: 15
filter_n_min: 30
filter_max_depth_mm: 4000
```

Reject reasons surfaced in the per-frame log: `flat`, `aspect`,
`low_raised_frac`, `high_planar_std` (canonical bucket names).

### 1.3 RGB+depth sync

`message_filters.ApproximateTimeSynchronizer` with `sync_slop_sec = 0.05` (50 ms
median target per `docs/milestones.md` M5). The M4c1 capture harness already
measured 11-44 ms median sync deltas in the existing 30-pair sync'd dataset
(`evaluation/camera_samples/cubes_depth_2026-06-27/`, see LOGBOOK 2026-06-27
M4c1), so the 50 ms budget is comfortable. Per-frame latency logging fires every
`latency_log_every` frames (default 100) and reports:

```
latency over last N frames  total ms: median=… p95=…  yolo ms: median=… p95=…
                           filter ms/frame: median=…  sync=… publishes=…
                           rejects={flat: N, aspect: N, ...}
```

### 1.4 Camera intrinsics

Subscribes to `/depth_cam/rgb/camera_info` once and overrides the YAML defaults
of `fx=360.3266 fy=360.3266 cx=321.0181 cy=179.2141`. The first received
CameraInfo's `K` matrix (row-major 9-element) is converted to floats and used
as the source of truth for any 3D extent math inside the filter. The XML list
type coercion (`list(msg.k)`) is needed because `msg.k` is a numpy array on the
Jetson — `if msg.k` would have raised `ValueError: ... ambiguous` (the first
launch attempt hit this and the fix is in commit `cf1cf7e`).

---

## 2. Jetson-side build + smoke verification

| Step | Command (Jetson) | Result |
|---|---|---|
| Sync code | `rsync` from dev PC | OK, 3 files updated |
| Build | `colcon build --packages-select recognition_of_different_colored_cubes --symlink-install` | Finished in 4.54s, exit 0 |
| Smoke launch | `timeout 5 ros2 run recognition_of_different_colored_cubes cube_detection_node` | Node started, engine loaded, spun until timeout |
| Engine load | log line | `TensorRT engine loaded: in=images (1, 3, 640, 640)  out=output0 (1, 7, 8400)` |
| Param dump | log lines | All 29 params + filter_params dict printed |
| Param resolution | `model_path` log | `/home/ubuntu/jetson_ws/src/Recognition-of-Different-Colored-Cubes/models/best.engine` (SHA-256 `c64d3e5e…` matches M4a) |

### 2.1 Live log excerpt (the actual node startup on the Jetson)

```
[INFO] [cube_detection_node]: TensorRT engine loaded: in=images (1, 3, 640, 640)
                                out=output0 (1, 7, 8400)
[INFO] [cube_detection_node]: cube_detection_node (M5) ready:
  rgb_topic=/depth_cam/rgb/image_raw
  depth_topic=/depth_cam/depth/image_raw
  detections_topic=/cube_detections
  vendor_objects_topic=/cube_detections/vendor_objects
  debug_image_topic=/cube_detections/debug_image
  publish_vendor_objects=True
  publish_debug_image=True
  model_path=/home/ubuntu/jetson_ws/src/Recognition-of-Different-Colored-Cubes/models/best.engine
  engine_loaded=True
  confidence_threshold=0.5
  iou_threshold=0.45
  imgsz=640
  sync_slop_sec=0.05
  filter_enabled=True
  filter_params={'n_min': 30, 'max_depth_mm': 4000, 'inset_px': 1,
                 'annulus_outer_px': 15, 'raised_mm': 30.0,
                 'min_raised_frac': 0.2, 'max_planar_top_stddev_mm': 30.0,
                 'max_ratio': 1.2, 'fx': 360.3266, 'fy': 360.3266,
                 'cx': 321.0181, 'cy': 179.2141}
```

Every parameter shown in this log is also exposed via `ros2 param list
/cube_detection_node` and mutable with `ros2 param set`.

---

## 3. BLOCKER — vendor depth-camera publish graph is stale

When this card started, the Jetson had a running `start_app_node.service`
(active for ~6 hours, PID 9465) and a `camera_container` process (PID 10109)
in the `/depth_cam` namespace, but **no `/depth_cam/*` topics were actually
publishing**:

```bash
$ ros2 topic info /depth_cam/rgb/image_raw -v
Type: sensor_msgs/msg/Image
Publisher count: 0
Subscription count: 1
Node name: cube_detection_node       # <- only my new M5 node
```

```bash
$ ros2 node list
/arm_controller /asr_node ... /web_video_server
# note: NO /depth_cam/camera_container in the DDS graph
```

The `camera_container` process exists but isn't loading any components — its
component manager probably never recovered from an earlier Orbbec USB hiccup,
and nothing in `start_app_node.service` is configured to restart it. This is a
**vendor-bringup state issue**, not an M5 code issue:

1. `cube_detection_node` correctly subscribes to both topics and waits (I
   verified the subscriptions are registered).
2. `message_filters.ApproximateTimeSynchronizer` correctly stays silent when
   no sync'd pairs arrive.
3. Nothing was published on `/cube_detections` because no frames were
   available to detect on.

This matches the .cursorrules "Hardware-only verification is the user's job"
rule: I cannot (per `.cursorrules`) modify the vendor `start_app_node.service`
or `peripherals/depth_camera.launch.py`, and restarting the bringup requires
sudo + USB re-enumeration that only Maher can do at the physical robot.

### 3.1 Minimal-touch recovery (recommended)

```bash
ssh jetrover
sudo systemctl stop start_app_node.service
# (optional) sudo systemctl reset-failed start_app_node.service
sudo systemctl start start_app_node.service
# wait ~5s for the camera_container to come up
source /opt/ros/humble/setup.bash
source ~/jetson_ws/install/setup.bash
ros2 topic list | grep /depth_cam    # expect /depth_cam/rgb/image_raw + /depth_cam/depth/image_raw
ros2 topic hz /depth_cam/rgb/image_raw    # expect ~30 Hz
```

If `/depth_cam/rgb/image_raw` is still 0 publishers after a fresh `start_app_node.service`
restart, the Orbbec USB device probably needs a physical replug — the camera
container has a known issue where it doesn't recover from USB suspend. The
`/home/ubuntu/ros2_ws/install/peripherals/share/peripherals/launch/depth_camera.launch.py`
file is the canonical bringup; running it manually also works:

```bash
export need_compile=True
export MACHINE_TYPE=JetRover_Mecanum
export LIDAR_TYPE=LD19
export HOST=/
export MASTER=
export DEPTH_CAMERA_TYPE=Dabai
ros2 launch peripherals depth_camera.launch.py
```

### 3.2 What I did NOT do (per .cursorrules)

- Did NOT modify `start_app_node.service`, `peripherals/depth_camera.launch.py`,
  or any vendor source.
- Did NOT touch the Hiwonder vendor packages.
- Did NOT push or modify `models/best.pt` / `best.onnx` / `best.engine` —
  the engine on the Jetson still has SHA-256 `c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1`
  (matches M4a), unchanged from M4a on 2026-06-27.

---

## 4. Exact commands for the live bag capture (run once §3 is unblocked)

### 4.1 Cubes-in-frame bag (target: ≥25 Hz, ≥3 detections on average)

```bash
ssh jetrover
# 1. Place the 1 red + 1 green + 1 blue cube in the JetRover FOV at 20–80 cm
# 2. Source the workspace
source /opt/ros/humble/setup.bash
source ~/jetson_ws/install/setup.bash
# 3. Verify the camera topics
ros2 topic hz /depth_cam/rgb/image_raw    # expect ~30 Hz
ros2 topic hz /depth_cam/depth/image_raw  # expect ~30 Hz
# 4. Launch the M5 node
ros2 launch recognition_of_different_colored_cubes detection.launch.py &
# 5. Wait 4s for engine + filter to come up
sleep 4
# 6. Verify /cube_detections publishes
timeout 5 ros2 topic hz /cube_detections    # expect ≥25 Hz
# 7. Record 30s bag
python3 ~/jetson_ws/src/Recognition-of-Different-Colored-Cubes/scripts/m5_capture_bag.py \
    --out-dir /tmp/m5_bag_cubes_$(date +%Y-%m-%d) \
    --duration-sec 30 \
    --format bag
# 8. Stop the node, pull the bag
ros2 node kill /cube_detection_node
scp -r /tmp/m5_bag_cubes_* ~/maher_ws/src/Recognition-of-Different-Colored-Cubes/evaluation/m5_live/
# 9. Run the analyzer on the dev PC
cd ~/maher_ws/src/Recognition-of-Different-Colored-Cubes
source /opt/ros/humble/setup.bash
python3 scripts/m5_analyze_bag.py \
    --bag-dir evaluation/m5_live/m5_bag_cubes_YYYY-MM-DD \
    --out-json evaluation/m5_live/m5_bag_cubes_YYYY-MM-DD/summary.json \
    --label cubes
```

### 4.2 Empty-scene bag (target: 0 detections at conf ≥ 0.50)

Same as 4.1 but with the cubes removed. Pass `--label empty` to the analyzer.
Expected outcome (per M4c1 V4 evidence gate): KEEP=0 / 68 detections at conf 0.25
and KEEP=0 / 26 at conf 0.50 on the saved empty-scene 30 frames.

---

## 5. Offline replay (parity check, runnable today without live camera)

The `scripts/m5_offline_replay.py` harness exercises the exact same code path
the live node uses (same `compute_geometry` + `decide` from the embedded
`geometry_filter` package module, same `_letterbox` + `_decode_yolov5_output`
helpers) on the saved 30 sync'd RGB+depth pairs from `cubes_depth_2026-06-27/`.
Inference uses ONNX Runtime (CPU) since the dev PC lacks TensorRT; this is a
**functional parity check, not a latency claim**.

```bash
source /opt/ros/humble/setup.bash
cd ~/maher_ws/src/Recognition-of-Different-Colored-Cubes
# Dev PC needs the M2 venv with onnxruntime-gpu (or `pip install onnxruntime`)
source .venv-m2/bin/activate    # if you have it
python3 scripts/m5_offline_replay.py \
    --rgb-dir evaluation/camera_samples/cubes_depth_2026-06-27 \
    --onnx models/best.onnx \
    --out-json evaluation/m5_live/replay_cubes_depth_2026-06-27.json \
    --label cubes \
    --conf 0.50 --iou 0.45 --imgsz 640 \
    --raised-mm 30 --min-raised-frac 0.20 \
    --max-planar-top-stddev-mm 30 --max-ratio 1.2 \
    --inset-px 1 --annulus-outer-px 15
```

Expected per-class counts (numbers reproduced from the M4c1 V1 cubes capture
that this same dataset fed into `m4c_geometry_filter.py`):

| Class | input | kept | rejected |
|---|---:|---:|---:|
| blue_cube | ~26 | 22 (V1 cube) + 4 (false positives on green bag) = ~22–26 | the rest |
| green_cube | ~4 | 0 | 4 |
| red_cube | 0 | 0 | 0 |

The exact per-class numbers will differ slightly between this run and the M4c1
report because the offline replay uses ONNX CPU (not TensorRT GPU) and the M4c1
report used TensorRT — but the per-class KEEP / REJECT *verdicts* must match
the geometry-filter logic exactly. **This is the parity check** I want to run
on the dev PC before pushing to the Jetson for live.

---

## 6. Risk register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Live camera topics stay dead even after `start_app_node.service` restart | Low (worked before on 2026-06-27) | High (criteria 2-5 can't be evaluated) | Document the bringup recovery in §3.1; the M5 code is unaffected. |
| Latency p95 > 50 ms on the live Jetson | Low (M4a engine measured 14.66 ms steady-state) | Medium | Filter is decoupled from engine path; first live bag will surface the real number. |
| Geometry filter KEEPs something in the empty scene | Low (M4c1 V4 PASS at both conf 0.25 and 0.50) | High | The whole point of the M5 acceptance bar — fallback is the Phase 2 fine-tune (card `t_13b658c2`, closed as no-longer-needed). |
| Geometry filter REJECTs all real cubes | Low (M4c1 V1 blue cube 22/29, green bag all rejected) | High | Same — would be flagged by the cubes bag immediately. |
| MCAP plugin missing on this Jetson install | Confirmed (only sqlite3 available) | Low | Use `--format bag` (sqlite3) — already the default. |

---

## 7. Next steps

1. **Maher**: restore vendor depth-camera publishing per §3.1 (one
   `systemctl restart` command).
2. **Then**: run §4.1 + §4.2 to produce the cubes/empty bags.
3. **Then**: run the offline replay harness (§5) on the dev PC for parity
   with the M4c1 report.
4. **Then**: update `docs/LOGBOOK.md` with the live latency + KEEP counts and
   flip M5 to COMPLETE in `docs/milestones.md`.

The M5 code itself is ready; §3 is the only thing between this card and a clean
completion.

---

## 8. Update 2026-06-28 03:43 HKT — vendor camera came alive briefly, died again

After the previous implementer run was unblocked, `start_app_node.service` was
restarted (Active: `since Sun 2026-06-28 03:33:26 HKT`, ~2 min uptime). I ran
the live M5 node on the Jetson end-to-end:

### 8.1 What worked live

- `ros2 launch recognition_of_different_colored_cubes detection.launch.py`
  booted cleanly on the Jetson (PID 40561).
- TensorRT engine loaded: `in=images (1, 3, 640, 640) out=output0 (1, 7, 8400)`.
- All 29 rclpy parameters declared + dumped at startup with M4c1 v2-only
  defaults (`raised_mm=30`, `min_raised_frac=0.20`, `max_planar_top_stddev_mm=30`,
  `max_ratio=1.2`, `inset_px=1`, `annulus_outer_px=15`).
- `ros2 node info /cube_detection_node` showed **all 3 publishers registered**
  correctly with the right types:
  - `/cube_detections` → `vision_msgs/msg/Detection2DArray`
  - `/cube_detections/vendor_objects` → `interfaces/msg/ObjectsInfo`
    (the vendor `interfaces` package is overlaid via the systemd env, even
    though `jetson_ws/install` doesn't carry it on its own)
  - `/cube_detections/debug_image` → `sensor_msgs/msg/Image`

### 8.2 What died again — same root cause

Initial probe (within ~5 min of bringup restart):
```
/depth_cam/rgb/image_raw:  average rate: 14.102 Hz  (window: 15)
/depth_cam/depth/image_raw: average rate: 29.750 Hz  (window: 93)
```
Both topics alive. RGB was at half rate (probably Orbbec auto-exposure settling).

After ~12 min of the bringup running:
```
topic info /depth_cam/rgb/image_raw:
  Publisher count: 0
  Subscription count: 1   # only /cube_detection_node
topic info /depth_cam/depth/image_raw:
  Publisher count: 0
```
**Camera component died again**, same symptom as the original blocker (§3):
`camera_container` PID 39185 still running but no longer registered as a ROS
node, no components loaded.

`/cube_detections` publish rate remained 0 Hz throughout — the
`ApproximateTimeSynchronizer` callback never fired because no RGB/depth frames
were reaching the subscribers.

### 8.3 Recovery attempted without modifying vendor

Per .cursorrules, I cannot `sudo systemctl restart start_app_node.service` —
that's the documented vendor-side recovery. The alternative is to launch the
vendor's existing `peripherals/depth_camera.launch.py` in a separate process,
but that creates a second `camera_container` in `/depth_cam/` namespace
which would conflict with the existing one. **Left for Maher to decide**.

The M5 node process was cleanly killed after the test (PID 40561 killed,
launch wrapper 40559 cleaned up).

### 8.4 New M5 code change

`scripts/m5_analyze_bag.py` — added `_detect_storage_id()` to sniff the bag's
storage plugin from `metadata.yaml` instead of hardcoding `"mcap"`. The Jetson
vendor install doesn't carry the `rosbag2_storage_mcap` plugin (sqlite3
default), so the analyzer previously would have failed to open any bag
recorded via `m5_capture_bag.py --format bag`.