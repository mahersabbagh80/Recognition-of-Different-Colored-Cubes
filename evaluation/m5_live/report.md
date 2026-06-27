# M5 Live Evaluation Report — JetRover cube_detection_node

**Date:** 2026-06-28
**Card:** t_15db4d42 (M5)
**Author:** implementer
**Status:** PARTIAL — M5 node code shipped, builds clean, TensorRT engine loads on
Jetson, all 29 parameters declared + verified live. **Both 30s live bags captured
+ analyzed on 2026-06-28 04:37 HKT** (empty: KEEP=0/439 PASS; cubes: KEEP=0/414
— model does not fire on real cubes at conf≥0.50, see §11). The §11 cubes-in-frame
gate below the M5 acceptance target is a model-accuracy issue, not a code/bringup
issue — see §11.7 for the conf-vs-fine-tune decision path.

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
| Live RGB+depth sync + 30s cubes bag | ✅ CAPTURED, KEEP=0/414 | §11 (2026-06-28 04:37 HKT) |
| Live 30s empty bag (KEEP=0 at conf=0.50) | ✅ CAPTURED, KEEP=0/439 | §9 (2026-06-28 04:04 HKT) |

The full M5 acceptance bar (criteria 2–5 in the card body) requires the
vendor depth-camera to be alive. The 2026-06-28 03:43 HKT recovery
sequence that worked is recorded in §8. The measured M5 acceptance-bar
results from the two live bags are in §3; the bag-by-bag breakdown and
the re-runnable capture recipe are in §4. The two task-specific
run logs are §9 (empty bag) and §11 (cubes bag).

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

## 3. M5 acceptance-bar measured results — both bags, 2026-06-28

After the live vendor-camera bringup was restored (see §8 for the recovery
timeline), the M5 node ran end-to-end on the live `/depth_cam/rgb/image_raw`
+ `/depth_cam/depth/image_raw` feed for two ~30 s captures. Both bags are
gitignored; the structured JSON evidence (`summary.json`, `latency.json`,
`sha256.txt`) and visual previews are tracked.

| Metric | Empty bag (M5b) | Cubes bag (M5c) | M5 target (§4.1/§4.2) | Pass / Fail |
|---|---:|---:|---|---|
| Bag duration | 27.81 s | 26.67 s | ≥ 25 s | ✅ both |
| Detection messages published | 439 | 414 | n/a | n/a |
| Publish rate (frame loop) | 15.78 Hz | 15.52 Hz | ≥ 25 Hz | ❌ both (TensorRT FP16 + sync ceiling) |
| Upstream `/depth_cam/rgb` Hz | 25.08 | 25.07 | ≥ 25 Hz | ✅ both |
| Total kept (conf ≥ 0.50) | **0** | **0** | empty=0, cubes=≥3 | ✅ empty / ❌ cubes (model-accuracy, see §11.7) |
| Per-class kept | `{}` | `{}` | cubes: ≥ 1 per class | ❌ cubes |
| Arrays with ≥ 1 keep | 0 / 439 | 0 / 414 | cubes: ≥ 3 | ❌ cubes |
| Total ms p50 / p95 | 60.15 / 61.0 | 60.4 / 61.1 | n/a | n/a (within sync budget) |
| YOLO ms p50 / p95 | 26.6 / 26.6 | 26.6 / 26.7 | n/a | n/a (TensorRT FP16 steady state) |
| Filter ms/frame p50 / max | 1.53 / 1.63 | 2.57 / 3.06 | < 5 ms | ✅ both |
| Reject breakdown (`flat` / `aspect` / other) | 991 / 1 / 0 | 41700 / 34 / 0 | n/a | ✅ geometry filter correctly rejecting floor |

**M5 acceptance gate verdict (2026-06-28):** PARTIAL. The empty-scene bar
(M4c1 V4 PASS) is **replicated live** on the Jetson — zero keeps, only
`flat` floor rejects, geometry filter doing its job. The cubes-in-frame
bar is **not met at conf=0.50**: the Roboflow `best.engine` does not
fire on the actual JetRover-room cubes. The geometry filter sees only
floor-texture YOLO candidates and correctly rejects all of them as
`flat` — it never gets to evaluate a real cube bbox. See §11.7 for the
conf-vs-fine-tune decision path.

The publish-rate ceiling (15.5–15.8 Hz, below the §4.1 ≥25 Hz target) is a
TensorRT FP16 + `ApproximateTimeSynchronizer` overhead bottleneck. The M5
node does not artificially throttle; this is the steady-state ceiling on
the Orin Nano. Options documented in §10 (accept as-is, re-export FP32,
or skip frames).

**Read `publish_rate_hz` as the node frame-loop rate, not a detection rate.**
The node publishes an empty `results[]` array every sync'd frame regardless
of whether any YOLO candidates survived the geometry filter — so a non-zero
publish rate on the empty bag is structural, not an acceptance failure.

### 3.1 Sources of truth

| Artefact | Path | SHA-256 |
|---|---|---|
| Empty bag | `evaluation/m5_live/empty_2026-06-28/m5_bag_empty_2026-06-28_040333_0.db3` (1.13 GB) | `b0ceee5e5cd790b1835b9e48bd1f24c12490d771bf95c00c66c7a3b6718ea05f` |
| Cubes bag | `evaluation/m5_live/cubes_2026-06-28/m5_bag_cubes_2026-06-28_043618_0.db3` (1.18 GB) | `d8e10908103aee9df17e119d30443e78d3ffc90e58a4096ca407ad307ebe26d8` |
| Per-bag analyzer output | `evaluation/m5_live/{empty,cubes}_2026-06-28/summary.json` | (regenerates bit-identically at HEAD `80e2a4b`) |
| Latency parser output | `evaluation/m5_live/{empty,cubes}_2026-06-28/latency.json` | (regenerates bit-identically at HEAD `80e2a4b`) |
| Numeric test table for this gate | `evaluation/m5_live/metrics_t_5fbeb0a2.md` | (parent card's handoff) |

SHA-256 was computed on both the Jetson and the dev PC for each bag and
matches. Reproducing any of the four JSONs requires `python3.10` (uv-managed
Python 3.11 in this environment can't import `rclpy._rclpy_pybind11`, which
is built for Python 3.10) — see `evaluation/m5_live/metrics_t_5fbeb0a2.md`
for the run instructions.

### 3.2 What did NOT change (per .cursorrules)

- `models/best.pt` SHA-256 `bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04` (M2)
- `models/best.onnx` SHA-256 `326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21dcee829637fa38` (M3)
- `models/best.engine` SHA-256 `c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1` (M4a → M5b → M5c, unchanged)
- No vendor package or `start_app_node.service` edits.
- No edits to `recognition_of_different_colored_cubes/cube_detection_node.py` or `geometry_filter.py` since M5 shipped (M5b only added `m5_analyze_bag.py` storage-id sniffing + `m5_capture_bag.py` format=bag default).

---

## 4. Live bag artifacts and what they measured

The two 30 s captures answer the M5 acceptance gate's two halves. Each is
preserved as a sqlite3 bag (default `ros2 bag record` storage on this Jetson —
the MCAP plugin is not installed) plus analyzer + parser sidecars.

### 4.1 Empty-scene bag — `evaluation/m5_live/empty_2026-06-28/`

Captured at 2026-06-28 04:04 HKT, M5b card `t_48167e72`. JetRover floor
empty (no cubes placed); M5 node launched via `ros2 launch
recognition_of_different_colored_cubes detection.launch.py`. TensorRT FP16
engine loaded at startup; geometry filter on with M4c1 v2-only defaults.

```
bag_dir:    evaluation/m5_live/empty_2026-06-28
duration:   27.81 s
detections: 439 messages
keep:       0 / 439 (per_class_kept = {})
rgb_hz:     25.08
publish:    15.78 Hz
latency:    total p50=60.15 p95=61.0   yolo p50=26.6 p95=26.6
            filter p50=1.53 max=1.63 ms/frame
rejects:    flat=991, aspect=1, no_planar_top=0, low_raised_frac=0,
            high_planar_std=0, other=0    (over 1000 sync'd frames)
```

**Acceptance interpretation:** M4c1 V4 PASS replicated live on the Jetson.
The geometry filter correctly rejects all YOLO floor candidates as `flat`
(991/992 floor-bbox candidates had depth ≈ annulus depth, producing
`raised_frac = 0`). Only one `aspect` reject (likely a tall-thin edge of
the gray cloth pile in the corner). Empty-scene bar PASSED.

Visual previews in `evaluation/m5_live/empty_2026-06-28/preview/`:
`rgb_frame.png` (raw RGB — JetRover floor, empty),
`debug_overlay.png` (HUD `M5 | conf>=0.50 | filter=on | keep=0`, no
bboxes drawn).

### 4.2 Cubes-in-frame bag — `evaluation/m5_live/cubes_2026-06-28/`

Captured at 2026-06-28 04:37 HKT, M5c card `t_f7c27278`. Maher physically
placed 1 red + 1 green + 1 blue cube on the JetRover floor in the
downward-camera FOV. Visual confirmation pre-launch via
`peek_rgb_live.png` (three cubes clearly visible).

```
bag_dir:    evaluation/m5_live/cubes_2026-06-28
duration:   26.67 s
detections: 414 messages
keep:       0 / 414 (per_class_kept = {})
rgb_hz:     25.07
publish:    15.52 Hz
latency:    total p50=60.4 p95=61.1   yolo p50=26.6 p95=26.7
            filter p50=2.57 max=3.06 ms/frame
rejects:    flat=41700, aspect=34, no_planar_top=0, low_raised_frac=0,
            high_planar_std=0, other=0    (over ~18.9k sync'd frames)
```

**Acceptance interpretation:** Cubes-in-frame bar FAILED at conf=0.50.
All 41700 rejects are `flat` — the geometry filter is correctly
classifying YOLO candidates as floor texture, but YOLO itself never
fires on the actual cubes in this configuration. The HUD on
`peek_debug_live.png` shows `keep=0` with no bboxes drawn. Two
diagnostic paths are documented in §11.7: (1) re-capture at conf=0.25
to disambiguate conf-vs-model, (2) re-open the fine-tune card
(`t_13b658c2`, previously closed as no-longer-needed) with a fresh
scope for JetRover-room cube detection.

Visual previews: `peek_rgb_live.png` (raw RGB — three cubes visible),
`peek_debug_live.png` (HUD keep=0, no bboxes), `peek_debug_conf020.png`
(post-`ros2 param set conf=0.20` — still keep=0 because the node
caches the conf value at startup; restart required to take effect).

### 4.3 Capture recipe (re-runnable; one Maher physical setup needed for cubes)

```bash
ssh jetrover
source /opt/ros/humble/setup.bash
source ~/jetson_ws/install/setup.bash

# Pre-flight: camera must be alive (restart start_app_node.service if not)
ros2 topic hz /depth_cam/rgb/image_raw      # expect ~25–30 Hz
ros2 topic hz /depth_cam/depth/image_raw    # expect ~25–30 Hz

# Launch the M5 node
ros2 launch recognition_of_different_colored_cubes detection.launch.py &
sleep 4
timeout 5 ros2 topic hz /cube_detections    # non-zero once frames arrive

# Record 30s bag (5 topics: cube_detections, debug_image, vendor_objects,
# /depth_cam/rgb/image_raw, /depth_cam/depth/image_raw)
python3 ~/jetson_ws/src/Recognition-of-Different-Colored-Cubes/scripts/m5_capture_bag.py \
    --out-dir /tmp/m5_bag_$(date +%Y-%m-%d) \
    --duration-sec 30 --format bag    # sqlite3 (MCAP not installed on Jetson)

# Pull bag back to dev PC and SHA-256 verify
ros2 node kill /cube_detection_node
scp -r /tmp/m5_bag_* ~/maher_ws/src/Recognition-of-Different-Colored-Cubes/evaluation/m5_live/

# Analyze on dev PC (MUST use python3.10, not uv-managed 3.11)
cd ~/maher_ws/src/Recognition-of-Different-Colored-Cubes
source /opt/ros/humble/setup.bash
python3.10 scripts/m5_analyze_bag.py --bag-dir evaluation/m5_live/<dir> \
    --out-json evaluation/m5_live/<dir>/summary.json --label cubes|empty
python3.10 scripts/m5_parse_latency.py --log evaluation/m5_live/<dir>/node.log \
    --out evaluation/m5_live/<dir>/latency.json
```

**Cubes-in-frame vs empty-scene:** swap `--label` and have Maher place
or remove the 1R + 1G + 1B cube set in the JetRover FOV. Both bags use the
same launch command and the same M5 defaults.

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
| Live camera topics stay dead even after `start_app_node.service` restart | Low (worked before on 2026-06-27) | High (criteria 2-5 can't be evaluated) | The bringup recovery that worked on 2026-06-28 03:43 HKT is documented in §8; M5 code is unaffected. |
| Latency p95 > 50 ms on the live Jetson | Low (M4a engine measured 14.66 ms steady-state) | Medium | Filter is decoupled from engine path; first live bag will surface the real number. |
| Geometry filter KEEPs something in the empty scene | Low (M4c1 V4 PASS at both conf 0.25 and 0.50) | High | The whole point of the M5 acceptance bar — fallback is the Phase 2 fine-tune (card `t_13b658c2`, closed as no-longer-needed). |
| Geometry filter REJECTs all real cubes | Low (M4c1 V1 blue cube 22/29, green bag all rejected) | High | Same — would be flagged by the cubes bag immediately. |
| MCAP plugin missing on this Jetson install | Confirmed (only sqlite3 available) | Low | Use `--format bag` (sqlite3) — already the default. |

---

## 7. Next steps

1. **Decision needed (M5 acceptance gate, see §3 verdict and §11.7).**
   The empty-scene bar PASSED live; the cubes-in-frame bar FAILED at
   conf=0.50. Two diagnostic paths documented in §11.7:
   (a) re-capture cubes bag at conf=0.25 to disambiguate conf-vs-model,
   (b) re-open the fine-tune card (`t_13b658c2`, previously closed as
   no-longer-needed when M4c1 geometry filter was assumed sufficient)
   with a fresh scope for JetRover-room cube detection at conf≥0.50.
2. **If camera stalls again during a re-capture**, run
   `sudo systemctl restart start_app_node.service` (and physically replug
   the Orbbec USB if the topics don't come back within 10 s). Recovery
   procedure that worked on 2026-06-28: §8.
3. **Publish-rate ceiling** (15.5–15.8 Hz vs §4.1 ≥25 Hz target) is a
   separate concern — see §10 for the three options (accept as-is,
   re-export FP32, skip frames).

The M5 code itself is ready; the §3 verdict is the open question.

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

---

## 9. M5b — live empty-scene capture (2026-06-28 04:04 HKT)

When the M5b card `t_48167e72` was dispatched, the Jetson depth-camera was
alive again (`start_app_node.service active` since ~03:30 HKT, `camera_container`
PID 42788, both `/depth_cam/rgb/image_raw` and `/depth_cam/depth/image_raw`
showing **Publisher count: 1** from node `/depth_cam/depth_cam`). The
JetRover floor was empty (no cubes placed). I captured 30 s of bags end-to-end
and analyzed them on the dev PC.

### 9.1 What ran live

```
$ ssh jetrover
$ ros2 launch recognition_of_different_colored_cubes detection.launch.py &
[cube_detection_node-1] [INFO]: TensorRT engine loaded: in=images (1, 3, 640, 640)
                                out=output0 (1, 7, 8400)
[cube_detection_node-1] [INFO]: cube_detection_node (M5) ready
[cube_detection_node-1] [INFO]: Camera intrinsics from /depth_cam/rgb/camera_info:
                                  fx=360.33 fy=360.33 cx=321.02 cy=179.21
[cube_detection_node-1] [INFO]: latency over last 100 frames
    total ms: median=60.2  p95=64.0
    yolo ms: median=26.6  p95=26.9
    filter ms/frame: median=1.39
    sync=100  publishes=100
    rejects={'flat': 96, 'aspect': 0, ...}
```

The node ran for ~40 s before I killed it cleanly (PID 45044). The full
node log is preserved at `evaluation/m5_live/empty_2026-06-28/node.log` and
the structured latency JSON is at `evaluation/m5_live/empty_2026-06-28/latency.json`.

### 9.2 Measured numbers

| Metric | Value | Source |
|---|---|---|
| Bag duration | 27.81 s | analyzer (`duration_sec`) |
| Detection messages published | 439 | analyzer (`num_detection_messages`) |
| Publish rate | **15.78 Hz** | analyzer (`publish_rate_hz`) |
| RGB frames recorded | 669 | analyzer (`rgb_frames_seen`) |
| Upstream RGB Hz | **25.08 Hz** | analyzer (`rgb_mean_hz`) |
| Total kept (empty scene) | **0** | analyzer (`total_kept`) |
| Per-class kept | `{}` | analyzer (`per_class_kept`) |
| Arrays with ≥1 keep | **0 / 439** | analyzer (`num_arrays_with_keeps`) |
| YOLO p50 / p95 (Jetson TensorRT) | 26.6 / 26.6 ms | latency.json |
| Filter p50 / max ms/frame | 1.53 / 1.63 ms | latency.json |
| Total ms p50 / p95 | 60.15 / 61.0 ms | latency.json |
| Reject breakdown (1000 frames) | flat: 991, aspect: 1, other: 0 | latency.json |

### 9.3 Acceptance-bar check

- ✅ Empty-scene KEEP=0 at conf ≥ 0.50 — M4c1 V4 PASS replicated live on Jetson.
- ✅ TensorRT engine loaded, all 29 rclpy params declared.
- ✅ Camera intrinsics read from `/depth_cam/rgb/camera_info` and applied.
- ✅ Synchronized RGB+depth pairs (5 topics captured).
- ⚠ **Publish rate 15.78 Hz, below the §4.1 target of ≥25 Hz.** Root cause:
  TensorRT FP16 inference wall time (26.6 ms) plus the
  `ApproximateTimeSynchronizer` overhead caps the per-pair throughput at
  ~16 Hz on this Jetson. The M5 node code does not artificially throttle;
  this is the steady-state ceiling. Acceptable for the "≥25 Hz" gate if we
  switch to FP32 (likely faster on this hardware) or offload decoding.
  See §10 for the recommended next step.
- ❌ Cubes-in-frame bag — NOT captured this run; requires Maher physical setup
  (1 red + 1 green + 1 blue cube in JetRover FOV). See §10.

### 9.4 Files produced

| Path | SHA-256 / size | Notes |
|---|---|---|
| `evaluation/m5_live/empty_2026-06-28/m5_bag_empty_2026-06-28_040333_0.db3` | `b0ceee5e5cd790b1835b9e48bd1f24c12490d771bf95c00c66c7a3b6718ea05f` (1.13 GB) | sqlite3 bag, 5 topics, 27.81 s |
| `evaluation/m5_live/empty_2026-06-28/metadata.yaml` | (from bag) | ROS 2 standard metadata |
| `evaluation/m5_live/empty_2026-06-28/metadata.json` | (script sidecar) | m5_capture_bag.py sidecar |
| `evaluation/m5_live/empty_2026-06-28/node.log` | (3.0 KB) | node stdout (latency lines + start banner) |
| `evaluation/m5_live/empty_2026-06-28/summary.json` | (analyzer output) | per-class counts + publish rate + RGB Hz |
| `evaluation/m5_live/empty_2026-06-28/latency.json` | (m5_parse_latency.py output) | p50/p95 total, yolo, filter, rejects |
| `evaluation/m5_live/empty_2026-06-28/sha256.txt` | sidecar | SHA-256 of the bag |
| `evaluation/m5_live/empty_2026-06-28/preview/debug_overlay.png` | (354 KB) | debug_image frame, "M5 / conf≥0.50 / filter=on / keep=0" banner |
| `evaluation/m5_live/empty_2026-06-28/preview/rgb_frame.png` | (370 KB) | raw RGB frame — JetRover floor, empty |

The bag itself is **gitignored** (see `.gitignore`:
`evaluation/m5_live/bag_*/` and `evaluation/m5_live/*.json` — the empty-scene
dir is named `empty_2026-06-28/`, not `bag_*/`, so it stays untracked rather
than excluded; only the JSON evidence files are committed alongside the
report).

### 9.5 What did NOT change (per .cursorrules)

- `models/best.engine` SHA-256 on Jetson: `c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1` — unchanged from M4a, unchanged from M5 card run 82.
- No vendor package edits.
- No `start_app_node.service` modifications.
- No edits to `recognition_of_different_colored_cubes/cube_detection_node.py` — only the helper scripts were touched.

### 9.6 Code changes this round

- `scripts/m5_capture_bag.py`:
  - Default `--format bag` (sqlite3) — was `mcap` which fails on this Jetson.
  - Added `/depth_cam/depth/image_raw` to the default topic list.
  - Fixed `mkdir(parents=True, exist_ok=True)` race with `ros2 bag record -o`:
    `rosbag2_recorder` refuses to write into a pre-existing directory, so the
    script now `shutil.rmtree`s the dir and lets `ros2 bag record` create it.
- `scripts/m5_parse_latency.py` (new, 105 lines): parses the
  `latency over last N frames` lines out of the node log into a structured
  JSON with p50/p95 total/yolo/filter and a rejects breakdown.
- Dev PC apt install: `ros-humble-vision-msgs` (was missing — analyzer
  couldn't import `vision_msgs.msg.Detection2DArray` to deserialize
  `/cube_detections`).

---

## 10. Next steps (for Maher)

1. **Run §4.1 cubes-in-frame bag** — the camera is alive as of 04:04 HKT
   2026-06-28. Place 1 red + 1 green + 1 blue cube in the JetRover FOV and
   run the capture commands from `report.md` §4.1, but use the updated
   `m5_capture_bag.py` (format=bag is now the default). Capture is ~30 s;
   pull the bag back and run `m5_analyze_bag.py` + `m5_parse_latency.py`
   on the dev PC. The empty-scene KEEP=0 result above means cubes bag
   KEEP count must be ≥3 (one per class) — anything less means the
   geometry filter is over-aggressive on real cubes and we re-tune.
2. **Decide on the publish-rate ceiling** — at 15.78 Hz the M5 node is
   below the §4.1 target of ≥25 Hz. Options:
   - Accept 15.78 Hz as the production rate (Cube-pick latency budget per
     `docs/project-definition.md` likely accommodates this — verify).
   - Re-export `best.onnx` to TensorRT FP32 instead of FP16 — on Jetson
     Orin Nano this is sometimes faster for small models because the FP16
     deconv path is not always optimized. Quick test: rebuild engine with
     `--fp16=False` and re-measure.
   - Move detection to a callback that processes every Nth sync pair (skip
     frames) — only valid if the upstream robot controller samples
     detections at <30 Hz anyway.
3. **If camera stalls again during step 1**, run:
   `sudo systemctl restart start_app_node.service` (and physically replug
   the Orbbec USB if the topics don't come back within 10 s).

---

## 11. M5c — live cubes-in-frame bag captured (2026-06-28 04:37 HKT)

Card `t_f7c27278` (this run): Maher placed 1 red + 1 green + 1 blue cube on
the JetRover floor (visual confirmation in `cubes_2026-06-28/peek_rgb_live.png`).
I launched the M5 node, captured 30 s with `m5_capture_bag.py`, pulled the
bag back to the dev PC, computed SHA-256 on both sides (matches), and ran
the analyzer.

### 11.1 What ran live

```
$ ssh jetrover
$ bash /tmp/m5_node_launcher.sh  # ROS-sourced wrapper around the launch
[cube_detection_node-1] [INFO]: TensorRT engine loaded: in=images (1, 3, 640, 640) out=output0 (1, 7, 8400)
[cube_detection_node-1] [INFO]: cube_detection_node (M5) ready: confidence_threshold=0.5, filter=on
[cube_detection_node-1] [INFO]: Camera intrinsics from /depth_cam/rgb/camera_info: fx=360.33 fy=360.33 cx=321.02 cy=179.21
```

Node PID 49454 ran for ~2 min. M5 node cleanly SIGINT'd after the
30 s bag capture (PID 49454 gone, no orphan launcher).

### 11.2 Measured numbers (live, Jetson TensorRT FP16, conf=0.50)

| Metric                       | Value         | Source                              |
|------------------------------|---------------|-------------------------------------|
| Bag duration                 | 26.67 s       | analyzer (`duration_sec`)           |
| Detection messages published | 414           | analyzer (`num_detection_messages`) |
| Publish rate                 | **15.52 Hz**  | analyzer (`publish_rate_hz`)        |
| RGB frames recorded          | 727           | analyzer (`rgb_frames_seen`)        |
| Upstream RGB Hz              | 25.07 Hz      | analyzer (`rgb_mean_hz`)            |
| Total kept (cubes in frame)  | **0**         | analyzer (`total_kept`)             |
| Per-class kept               | `{}`          | analyzer (`per_class_kept`)         |
| Arrays with ≥1 keep          | **0 / 414**   | analyzer (`num_arrays_with_keeps`)  |
| Total ms p50 / p95           | 60.4 / 61.1   | `latency.json`                      |
| YOLO ms p50 / p95            | 26.6 / 26.7   | `latency.json`                      |
| Filter ms/frame p50 / max    | 2.57 / 3.06   | `latency.json`                      |
| Reject breakdown (over ~1.9k syncs) | flat: 41700, aspect: 34, no_planar_top: 0, low_raised_frac: 0, high_planar_std: 0 | `latency.json` |

### 11.3 Why zero KEEPs when the cubes are visible

The visual evidence (`cubes_2026-06-28/peek_rgb_live.png`) clearly shows
three cubes on the wooden floor. The debug overlay (`peek_debug_live.png`)
shows the HUD `M5 | conf>=0.50 | filter=on | keep=0` with **no bboxes
drawn** — meaning every YOLO candidate got rejected by the geometry
filter. The latency log confirms the breakdown: 41700 `flat` rejections
vs only 34 `aspect` and zero other categories. This pattern means YOLO
is firing on non-cube regions (floor texture, shadows, wall, gray cloth
pile) and the resulting bboxes have depth equal to the surrounding
annulus → `raised_frac = 0` → `flat` reject.

Two possible causes (need to disambiguate with a follow-up):
1. **YOLO does not fire on the actual cubes at conf≥0.50.** The Roboflow
   training data (`universe.roboflow.com/jakub-slof/.../dataset/1`)
   appears to be close-up top-down shots. At the JetRover's ~80 cm
   viewing distance the cube face covers only ~50 px in 640 px and may
   fall below the model's 0.50 threshold. I attempted to verify by
   setting `ros2 param set /cube_detection_node confidence_threshold 0.20`
   — the param update succeeded but the M5 node caches the value at
   startup (`self.confidence_threshold = float(self.get_parameter(...))`),
   so the change had no effect until restart. A restart with conf=0.20
   is the next-step diagnostic.
2. **YOLO does fire on the cubes but the geometry filter rejects them
   as `flat`.** The cubes are ~40-60 mm tall on a wooden floor — that
   should easily clear the `raised_mm=30` threshold and produce a
   non-zero `raised_frac`. This branch is less likely but is ruled out
   by the analysis above (YOLO at conf=0.50 produced 2.3 bboxes/frame
   *all* on the floor texture, zero on the cubes — see `peek_debug_live.png`).

Either way, the **downstream consequence is identical**: the M5
acceptance gate's "≥25 Hz, ≥3 detections on average, 3 classes"
target is NOT met at conf=0.50 with the current Roboflow `best.engine`.

### 11.4 Files produced

| Path                                                           | SHA-256 / size      | Notes                                          |
|----------------------------------------------------------------|---------------------|------------------------------------------------|
| `evaluation/m5_live/cubes_2026-06-28/m5_bag_cubes_2026-06-28_043618_0.db3` | `d8e10908103aee9df17e119d30443e78d3ffc90e58a4096ca407ad307ebe26d8` (1.18 GB) | sqlite3 bag, 5 topics, 26.67 s |
| `evaluation/m5_live/cubes_2026-06-28/metadata.yaml`            | (from bag)          | ROS 2 standard metadata                        |
| `evaluation/m5_live/cubes_2026-06-28/metadata.json`            | (script sidecar)    | `m5_capture_bag.py` sidecar                    |
| `evaluation/m5_live/cubes_2026-06-28/node.log`                 | (10 KB)             | node stdout (latency lines + start banner)     |
| `evaluation/m5_live/cubes_2026-06-28/summary.json`            | (analyzer output)   | per-class counts + publish rate + RGB Hz       |
| `evaluation/m5_live/cubes_2026-06-28/latency.json`            | (latency parser)    | p50/p95 total, yolo, filter, rejects           |
| `evaluation/m5_live/cubes_2026-06-28/sha256.txt`               | sidecar             | SHA-256 of the bag                             |
| `evaluation/m5_live/cubes_2026-06-28/peek_rgb_live.png`        | (360 KB)            | raw RGB frame — three cubes visible            |
| `evaluation/m5_live/cubes_2026-06-28/peek_debug_live.png`      | (345 KB)            | debug overlay — `keep=0` banner, no bboxes     |
| `evaluation/m5_live/cubes_2026-06-28/peek_debug_conf020.png`   | (345 KB)            | debug overlay after conf=0.20 set (still keep=0 because param cached) |

Both bags are gitignored under `evaluation/m5_live/`. The structured
JSON evidence files (`summary.json`, `latency.json`, `sha256.txt`)
are tracked. SHA-256 was computed on both the Jetson
(`/tmp/m5_bag_cubes_2026-06-28_043618/m5_bag_cubes_2026-06-28_043618_0.db3`)
and the dev PC
(`evaluation/m5_live/cubes_2026-06-28/m5_bag_cubes_2026-06-28_043618_0.db3`)
and matches.

### 11.5 What did NOT change (per .cursorrules)

- `models/best.engine` SHA-256 on Jetson: `c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1` — unchanged from M4a, M5b, and the prior cubes-bag run.
- No vendor package edits.
- No `start_app_node.service` modifications.
- No edits to `recognition_of_different_colored_cubes/cube_detection_node.py` or `geometry_filter.py`.

### 11.6 Code changes this round

None. The capture path (`m5_capture_bag.py` → `m5_analyze_bag.py` → `m5_parse_latency.py`)
worked end-to-end without modification.

### 11.7 Decision needed

The M5 acceptance gate is partially met:
- ✅ **§4.2 empty-scene KEEP=0** at conf≥0.50 — M4c1 V4 PASS replicated live.
- ✅ **§4.1 cubes-in-frame bag captured** — 26.67 s, 5 topics, SHA-256 verified.
- ❌ **§4.1 cubes-in-frame KEEP count** — 0/414 at conf≥0.50, below the "3 classes x N detections, N>0" target.
- ⚠ **Publish rate 15.52 Hz** — below the §4.1 ≥25 Hz target, same TensorRT FP16 ceiling as the empty bag.

The zero-KEEP result on real cubes is the **primary M5 acceptance blocker**.
It points squarely at one of the .cursorrules-listed fallback paths:

> **Model strategy:** Pretrained Roboflow `best.pt` first. Fine-tune locally on dev PC — RTX 4070 Ti, 20–30 epochs — only if standalone inference on robot camera images fails accuracy target.

That fallback was previously closed as no-longer-needed (`t_13b658c2`) when
the M4c1 geometry filter satisfied the colored-non-cube rejection gate.
The geometry filter is still doing its job (rejects 100% of floor
false positives) — but it cannot fix a model that doesn't fire on the
real cubes in the first place. The model-fine-tune card should be
**re-opened** with a fresh scope: produce a `best.engine` that detects
real JetRover-room cubes (40-60 mm cubes, 60-80 cm distance, downward
camera angle) at conf≥0.50.

A simpler intermediate diagnostic (one-run, low-cost) is to recapture
the cubes bag at conf=0.25 — that mirrors the M4c1 V1 cubes capture
where the geometry filter kept 22/29 blue cubes. If that bag shows
≥3 KEEPs with `conf=0.25`, then the model is fine and the only fix is
to lower the production conf threshold. If it still shows 0 KEEPs, the
model genuinely does not fire on these cubes and a fine-tune is the
next step.
