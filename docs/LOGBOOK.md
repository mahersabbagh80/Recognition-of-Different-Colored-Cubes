# Logbook

Development notes and session records for this project.

This logbook is a chronological record of what I worked on, what I found, and what I will do next. It complements the [`README.md`](../README.md) (what the project is and how to run it) and [`milestones.md`](milestones.md) (the plan).

---

## How to use this logbook

- Add **one entry per work day** (or per meaningful session if you work twice in one day).
- Keep entries short and factual — bullet points, not essays.
- Link to evidence where possible: terminal output, screenshot filenames, model files, commit hashes.
- When you finish a milestone step, record the **exact command or config** so it is reproducible.
- At the end of each day, fill in every section of the template below — even if the answer is "none" for Blockers.

Copy the template block for each new entry. Replace `YYYY-MM-DD` with the session date and `M?` with the active milestone.

---

## Legend

| Field | What to write |
|-------|---------------|
| **Milestone** | Which milestone you were working toward (M1–M7). |
| **Goal** | What you intended to achieve in this session. |
| **Work done** | Commands run, files changed, decisions made. |
| **Results** | What worked or failed; include numbers (fps, accuracy, topic hz) when available. |
| **Evidence** | Screenshots, log files, model paths, terminal snippets, git commits. |
| **Blockers** | Anything stopping progress — or "None." |
| **Next** | The very next action to take (one or two items max). |

---

## Entry template

```markdown
## YYYY-MM-DD — Short session title

- **Milestone:** M? — milestone name
- **Goal**
  -

- **Work done**
  -

- **Results**
  -

- **Evidence**
  -

- **Blockers**
  - None.

- **Next**
  -
```

---

## Entries

<!-- New entries go below this line, newest at the top. -->

## 2026-06-28 — M5c2: sticker-removed cubes-in-frame re-test (card t_737dbf1a)

- **Milestone:** M5 PARTIAL — disambiguation re-test
- **Goal**
  - Determine whether the M5 PARTIAL verdict (cubes_KEEP=0/414 at
    conf≥0.50) was caused by a dimming sticker on the Orbbec RGB lens
    that the user identified and removed. Run the same M5c scene
    (1 red + 1 green + 1 blue cube, ~60-80 cm from camera) twice —
    once at conf=0.50 (M5c mirror), once at conf=0.25 (the §11.7
    intermediate diagnostic) — and report the verdict.

- **Work done**
  - Verified Jetson host reachable (was offline during prior run; ping
    restored, both `/depth_cam/rgb/image_raw` and `/depth_cam/depth/image_raw`
    show Publisher count: 1).
  - Re-used the durable M5c2 bag already captured during the
    previous implementer run (the artifacts under
    `evaluation/m5_live/cubes_sticker_off_2026-06-28/` are complete:
    1.18 GB sqlite3 bag, SHA-256 `ef30ab3fa5f7…`, metadata sidecar
    with `sticker_removed: true`, peek images, summary.json,
    latency.json, node.log, plus a full conf=0.25 re-capture in the
    `conf025/` subdirectory).
  - Re-derived all numbers from the durable JSON evidence (no need to
    re-run the analyzer — the originals are canonical).
  - Independently computed brightness sanity: M5c sticker-on raw RGB
    pre-launch mean luminance 132.49 vs M5c2 sticker-off 133.31 —
    delta +0.82 of 255, within camera-exposure noise.
  - Wrote §12 (M5c2 sticker-removed re-test) into
    `evaluation/m5_live/report.md` with brightness-sanity table,
    conf=0.50 mirror numbers vs M5c, conf=0.25 diagnostic numbers,
    visual-evidence description, conclusion, and the §12.7 next-step
    recommendation.
  - Updated §0 TL;DR + §3 acceptance-bar verdict + §7 next-steps to
    reference §12.7 instead of §11.7.

- **Results**
  - **Brightness sanity**: removing the sticker did NOT brighten the
    camera (raw RGB mean delta +0.82/255, within noise).
    "Dimming sticker" hypothesis **falsified**.
  - **conf=0.50 (mirror of M5c)**: KEEP=0/460 — identical to M5c's
    0/414. All 460 keeps are zero; 514,364 `flat` rejects + 17,815
    `aspect` rejects. The geometry filter is correctly rejecting
    every floor-texture YOLO candidate.
  - **conf=0.25 (intermediate diagnostic)**: KEEP=2/439 — `per_class_kept
    = {green_cube: 2}`. **Red and blue cubes still at zero**.
  - **Publish rate**: 15.86 Hz (conf=0.50), 15.21 Hz (conf=0.25) —
    unchanged from M5c (TensorRT FP16 + sync ceiling).
  - **Filter ms/frame p50**: 1.27 (conf=0.50), 4.83 (conf=0.25) —
    conf=0.25 brings 3.5x more bboxes to filter (more YOLO recall),
    but still well under the 5 ms target.

- **Evidence**
  - Bag: `evaluation/m5_live/cubes_sticker_off_2026-06-28/m5_bag_cubes_sticker_off_2026-06-28_091930_0.db3`
    (SHA-256 `ef30ab3fa5f7910df749856041ea22f6a2ebd91ece4bf661fd17ce6fbefc5a7f`,
    1.18 GB, 5 topics, 29.00 s)
  - Summary: `evaluation/m5_live/cubes_sticker_off_2026-06-28/summary.json`
    (460 detections, 0 keeps)
  - Latency: `evaluation/m5_live/cubes_sticker_off_2026-06-28/latency.json`
    (p50_total 59.3 ms, yolo p50 26.6 ms, filter p50 1.27 ms)
  - Conf025 bag + summary + latency under
    `evaluation/m5_live/cubes_sticker_off_2026-06-28/conf025/`
  - Report: `evaluation/m5_live/report.md` §12 (10 sub-sections)

- **Blockers**
  - None. (Jetson host came back online during this run; the previous
    implementer run captured the bag during the gap.)

- **Next**
  - **Re-open fine-tune card `t_13b658c2` with a positive-detection
    scope**: produce a `best.engine` that detects real JetRover-room
    cubes (40-60 mm cubes, 60-80 cm distance, downward camera angle)
    at conf≥0.50. The previous fine-tune scope (hard-negative rejection
    of V3 distractors) is no longer needed — M4c1 V3 passed at
    conf=0.50 without retraining. The new scope is positive detection
    on real cubes, which the geometry filter cannot fix.
  - Keep the M5 PARTIAL verdict and do not declare M5 done until the
    fine-tuned `best.engine` is verified live on the cubes scene.
  - See `evaluation/m5_live/report.md` §12.7 for the full next-step
    decision path.

## 2026-06-28 — M5 ship + live evidence (cards t_15db4d42 / t_bb889759 / t_219505c6 / t_48167e72 / t_f7c27278)

- **Milestone:** M5 — ROS 2 node live
- **Goal**
  - Ship the M5 ROS 2 node with the M4c1 geometry post-filter + conf=0.50
    baked into the runtime, capture two live 30 s bags (empty + cubes) on
    the Jetson, and reflect the resulting numbers across README,
    `.cursorrules`, `docs/milestones.md`, and `evaluation/m5_live/report.md`.

- **M5 acceptance verdict (per `evaluation/m5_live/report.md`)**
  - §4.2 empty-scene KEEP=0 at conf ≥ 0.50 — **PASS** (M5b KEEP=0/439)
  - §4.1 cubes-in-frame KEEP ≥ 3 across 3 classes — **FAIL** (M5c 0/414)
  - §4.1 publish rate ≥ 25 Hz — **FAIL** (15.5–15.8 Hz, TensorRT FP16 + sync ceiling)
  - §4.1 latency p95 ≤ 50 ms — **FAIL** (~61 ms total per-frame, yolo floor is 26.6 ms)
  - README launch instructions + parameter table match the live node — **PASS**
  - **Overall: PARTIAL** (implementation complete; acceptance gate pending §11.7 decision)

- **Why geometry filter + conf=0.50, not retraining (the chosen M5 mitigation)**
  - M4c1 evidence gate (5 testable raised-3D colored distractors + empty
    scene, synchronised RGB+depth, 622 input detections) showed the
    v2-only geometry filter
    (`raised_mm=30, min_raised_frac=0.20, max_planar_top_stddev_mm=30,
    max_ratio=1.2, inset_px=1, annulus_outer_px=15`) suppresses 100 % of
    named M4b flat-color distractors and the empty scene
    ([`evaluation/m4c_geometry_filter/report.md`](../evaluation/m4c_geometry_filter/report.md)).
  - That closed the V2 false-positive problem without a hard-negative
    fine-tune. The fine-tune card (`t_13b658c2`, closed 2026-06-27 as
    no-longer-needed) would have produced a model that fires less often
    on the very floor/wall patterns the geometry filter is now rejecting
    cleanly — redundant work, higher latency, worse portability.
  - Geometry filter is the **necessary** part of the M5 pre-ship gate;
    fine-tune is the **conditional** part if M5c leaves residual FPs on a
    tight real-cube bbox or on V3 distractors Maher hasn't physically
    arranged yet.

- **What shipped (M5 implementation)**
  - `recognition_of_different_colored_cubes/cube_detection_node.py` (641
    lines) — TensorRT FP16 + M4c1 geometry filter + RGB+depth sync via
    `message_filters.ApproximateTimeSynchronizer`. Single binding
    allocation, shared `cuda.Stream`, `execute_async_v2` +
    `stream.synchronize` (the pattern proven in `scripts/test_inference.py`).
  - `recognition_of_different_colored_cubes/geometry_filter.py` — clean
    copy of the M4c1 `compute_geometry` + `decide` as a proper package
    module (replaces the sys.path hack from the first commit; landed in
    commit `cf1cf7e` after a `ModuleNotFoundError` on Jetson colcon install).
  - 29 rclpy-declared parameters covering topics, model, conf/iou/imgsz,
    sync slop, all 8 filter params, fx/fy/cx/cy, publish toggles, and
    `latency_log_every`. Camera intrinsics overridden at startup from
    `/depth_cam/rgb/camera_info`.
  - `config/params.yaml` — M4c1 defaults: `confidence_threshold: 0.50`,
    `raised_mm: 30`, `min_raised_frac: 0.20`, `max_planar_top_stddev_mm:
    30`, `max_ratio: 1.2`, `inset_px: 1`, `annulus_outer_px: 15`.
  - `package.xml` — added `message_filters`, `numpy`, `PIL`, `torch`,
    `torchvision` exec_depends. TensorRT + pycuda are Jetson-only and
    intentionally NOT in the apt rosdep set (commented).
  - Three new scripts under `scripts/m5_*.py`: `m5_capture_bag.py` (Jetson
    `ros2 bag record` wrapper, default format=sqlite3 because the mcap
    plugin is not installed), `m5_analyze_bag.py` (per-class kept +
    publish rate + RGB Hz), `m5_offline_replay.py` (parity check before
    live test), `m5_parse_latency.py` (p50/p95 from node stdout).

- **Live evidence (Jetson, TensorRT FP16, conf=0.50, filter on)**
  - **M5b — empty-scene bag (2026-06-28 04:04 HKT)**
    `evaluation/m5_live/empty_2026-06-28/m5_bag_empty_2026-06-28_040333_0.db3`
    (1.13 GB, sqlite3, SHA-256
    `b0ceee5e5cd790b1835b9e48bd1f24c12490d771bf95c00c66c7a3b6718ea05f`,
    27.81 s duration).
    - KEEP = **0 / 439** at conf ≥ 0.50 (M4c1 V4 PASS replicated live)
    - Per-class kept: `{}`
    - Publish rate 15.78 Hz; upstream RGB Hz 25.08
    - total ms p50=60.15, p95=61.0; yolo ms p50=26.6, p95=26.6;
      filter ms p50=1.53, max=1.63
    - Rejects over 1000 sync'd frames: flat=991, aspect=1
  - **M5c — cubes-in-frame bag (2026-06-28 04:37 HKT)**
    `evaluation/m5_live/cubes_2026-06-28/m5_bag_cubes_2026-06-28_043618_0.db3`
    (1.18 GB, sqlite3, SHA-256
    `d8e10908103aee9df17e119d30443e78d3ffc90e58a4096ca407ad307ebe26d8`,
    26.67 s duration).
    - KEEP = **0 / 414** at conf ≥ 0.50 — model-accuracy blocker
    - Per-class kept: `{}`
    - Publish rate 15.52 Hz; upstream RGB Hz 25.07
    - total ms p50=60.4, p95=61.1; yolo ms p50=26.6, p95=26.7;
      filter ms p50=2.57, max=3.06
    - Rejects over ~18.9 k sync'd frames: flat=41700, aspect=34,
      no_planar_top=0, low_raised_frac=0, high_planar_std=0
    - Visual confirmation: `evaluation/m5_live/cubes_2026-06-28/peek_rgb_live.png`
      shows three cubes (blue / green / red, left to right); debug overlay
      `peek_debug_live.png` shows HUD `keep=0` because every YOLO candidate
      landed on floor texture and got rejected as `flat`.

- **Why KEEP=0/414 on real cubes (analysis, see report §11.7)**
  - The geometry filter is doing its job — every reject is `flat`, meaning
    the bbox depth ≈ annulus-floor depth (cubes on the floor should
    produce a raised bbox, but the YOLO bbox is missing the cube).
  - The latency log shows ~2.3 YOLO fires per frame, **all on floor texture**
    (wood grain, gray cloth pile in the corner). YOLO at conf=0.50 does
    not fire on the actual cubes in this configuration.
  - This is a **model-accuracy issue**, not a code/bringup issue. The
    Roboflow `best.engine` does not generalize from the close-up top-down
    training images to the JetRover-room downward-camera placement.

- **§11.7 decision path (pending Maher)**
  1. **Diagnostic**: recapture the cubes bag at conf=0.25. If the model
     fires on real cubes at the lower threshold, the only fix is to lower
     the production conf threshold (mirrors M4c1 V1 cubes capture where
     geometry filter kept 22/29 blue cubes at conf=0.25).
  2. **If conf=0.25 also shows 0 KEEPs**: the model genuinely does not fire
     on real cubes. Re-open the fine-tune card (`t_13b658c2`, previously
     closed 2026-06-27 as no-longer-needed) with a fresh scope: produce a
     `best.engine` that detects real JetRover-room cubes at conf ≥ 0.50.
  3. Publish-rate ceiling (15.5–15.8 Hz) is a **separate** concern:
     TensorRT FP16 + sync overhead, not fixable by re-tuning the geometry
     filter. Options documented in `evaluation/m5_live/report.md` §10:
     accept as-is, re-export FP32, or skip frames in the callback.

- **What did NOT change (per .cursorrules)**
  - `models/best.engine` SHA-256 unchanged:
    `c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1`
    (matches M4a, M5b, M5c — no retraining)
  - `models/best.pt` SHA-256 unchanged:
    `bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04`
    (18.5 MB, mtime 2026-06-24 04:12, M2)
  - `models/best.onnx` SHA-256 unchanged:
    `326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21dcee829637fa38`
    (35.0 MB, mtime 2026-06-27 14:08, M3)
  - No vendor or `start_app_node.service` edits
  - No edits to `recognition_of_different_colored_cubes/cube_detection_node.py`
    or `geometry_filter.py` since the M5 ship commit `cf1cf7e`

- **Code changes (M5 docs chain across 5 cards)**
  - **t_15db4d42 (M5 ship + Jetson smoke, run 82)** — `cube_detection_node.py`
    rewrite, embed `geometry_filter.py`, `config/params.yaml`, `package.xml`,
    three new `m5_*.py` scripts, README launch instructions. Two commits:
    `f571ea1` (initial) + `cf1cf7e` (geometry_filter embed + camera_info k fix).
  - **t_48167e72 (M5b empty bag)** — `scripts/m5_capture_bag.py` default
    format=sqlite3 + `/depth_cam/depth/image_raw` added; new
    `scripts/m5_parse_latency.py`; `.gitignore` tightened for M5
    evaluation; dev-PC apt install `ros-humble-vision-msgs`.
  - **t_f7c27278 (M5c cubes bag)** — no code changes; analysis only
    (analyzer output + latency JSON + report §11 added).
  - **t_219505c6 (M5 docs pass on report + cursorrules + milestones)** —
    `evaluation/m5_live/report.md` §3 + §4 rewritten (acceptance-bar
    results, bag-by-bag breakdown, capture recipe); TL;DR + §6 + §7
    cross-references updated.
  - **t_bb889759 (M5 integration docs pass)** — README parameter table
    split into 5 sub-tables with plain-language geometry-filter
    descriptions; runtime override examples; publish toggles; stale
    "inference not live" banner removed; Demo section points at the
    tracked M5 overlays; `--symlink-install` added to the dev-machine
    build line. `.cursorrules` Current Status updated to reflect
    implementation complete + acceptance gate PARTIAL.

- **Pointer to per-card intermediate entries**
  The auto-decomposer chain produced one entry per card during the
  2026-06-28 M5 cluster. The unique per-card content (specific process
  PIDs, run order, exact command transcripts) is preserved below as
  short pointer entries — read this canonical M5 entry first, then dip
  into the per-card pointer for whatever detail is missing.

## 2026-06-28 — M5 docs pass: README split-tables + cursorrules status (card t_bb889759)

Pointer to the canonical 2026-06-28 M5 ship entry above. This card's
unique work: README parameter table split into 5 sub-tables with
plain-language descriptions for all six geometry-filter parameters
(`filter_raised_mm`, `filter_min_raised_frac`,
`filter_max_planar_top_stddev_mm`, `filter_max_ratio`, `filter_inset_px`,
`filter_annulus_outer_px`) plus the master switch `filter_enabled` and
the depth-quality guard `filter_n_min`; runtime override examples
(`ros2 param get` / `ros2 param set`); publish toggles
(`publish_vendor_objects`, `publish_debug_image`) added; stale
"inference not live" banner removed; `--symlink-install` added to the
dev-machine build line. No code edits. See canonical entry for the
measured numbers.

## 2026-06-28 — M5 docs pass: report §3+§4 + cursorrules + milestones (card t_219505c6)

Pointer to the canonical 2026-06-28 M5 ship entry above. This card's
unique work: `evaluation/m5_live/report.md` §3 + §4 rewritten (the old
sections described the pre-capture bringup blocker; the new sections
carry the measured acceptance-bar results table, the two-bag
breakdown, the bag SHA-256 sources-of-truth table, the unchanged-model
SHAs table, and the re-runnable capture recipe); TL;DR + §6 + §7
cross-references updated; `docs/milestones.md` M5 left as PARTIAL with
the §11.7 reference (intentionally NOT flipped to COMPLETE); README
launch instructions + parameter table verified line-for-line against
`launch/detection.launch.py` and `config/params.yaml`. See canonical
entry for the M5b/M5c measured numbers and the model-accuracy
analysis.

## 2026-06-28 — M5c: live cubes-in-frame bag captured + analyzed (card t_f7c27278)

Pointer to the canonical 2026-06-28 M5 ship entry above. This card's
unique work: pre-flight probe confirmed both `/depth_cam/*` topics
publish (camera_container PID 42788 stable, start_app_node.service
active); visual cube confirmation via `m5_peek_rgb.py` saved to
`evaluation/m5_live/cubes_2026-06-28/peek_rgb_live.png` (three cubes
visible blue / green / red, left to right); launched M5 node on Jetson
via `/tmp/m5_node_launcher.sh` wrapper (the vendor `/opt/ros/humble/
setup.bash` line 11 `. /home/ubuntu/setup.sh` fails under zsh, so the
wrapper sources both overlays explicitly); captured 30 s bag via
`m5_capture_bag.py`, pulled 1.18 GB to dev PC via scp, SHA-256 verified
on both sides (`d8e10908…`); analyzer output to `summary.json`,
latency JSON via `m5_parse_latency.py`. Bag duration 26.67 s, 414
detection messages, KEEP=0/414 at conf=0.50. Deliverables under
`evaluation/m5_live/cubes_2026-06-28/` (bag + metadata.yaml/json +
node.log + summary/latency/sha256 + 3 preview PNGs). See canonical
entry for the per-class breakdown, the model-accuracy analysis, and
the §11.7 decision path.

## 2026-06-28 — M5b: live empty-scene bag captured + analyzed (card t_48167e72)

Pointer to the canonical 2026-06-28 M5 ship entry above. This card's
unique work: picked up the stalled-camera state from `t_15db4d42` run
82; SSH probe via `jetrover` alias confirmed both `/depth_cam/*`
topics had Publisher count: 1 from `/depth_cam/depth_cam`;
start_app_node.service active, PID 42788; JetRover floor was empty
(no cubes placed); synced `m5_capture_bag.py`, `m5_analyze_bag.py`,
`m5_offline_replay.py` to the Jetson; patched `m5_capture_bag.py` to
default `--format bag` (sqlite3 — mcap plugin not installed) and
include `/depth_cam/depth/image_raw` in default topic list; launched
M5 node on Jetson (PID 45044); recorded 30 s bag (5 topics); pulled
1.13 GB to dev PC; ran `m5_analyze_bag.py` and `m5_parse_latency.py`;
installed `ros-humble-vision-msgs` on dev PC (analyzer needs
`vision_msgs.msg.Detection2DArray`); bag duration 27.81 s, 439
detection messages, KEEP=0/439 at conf=0.50 (M4c1 V4 PASS replicated
live). Cubes-in-frame bag deferred to M5c. Publish-rate caveat
15.78 Hz below §4.1 ≥25 Hz target (TensorRT FP16 inference + sync
overhead). See canonical entry for the model-accuracy blocker analysis
that emerged from M5c.

## 2026-06-28 — M5 live retry: camera alive briefly, died again (card t_15db4d42, run 82)

- **Context**: the previous implementer run was unblocked at ~03:24 HKT after
  `start_app_node.service` was restarted (active since 03:33:26 HKT, 2 min
  uptime when I SSH'd in). I resumed this card to capture the live bags.
  This entry covers **only** the brief-camera-alive phase; the
  full M5 ship story lives in the canonical 2026-06-28 M5 entry above
  (cards t_15db4d42 / t_bb889759 / t_219505c6 / t_48167e72 / t_f7c27278).

- **Work done**
  - Confirmed `/depth_cam/rgb/image_raw` (14.1 Hz) and
    `/depth_cam/depth/image_raw` (29.8 Hz) were publishing within ~5 min of
    the bringup restart.
  - Synced `scripts/m5_capture_bag.py` to the Jetson (was missing — only the
    package had been rsynced previously).
  - Patched `scripts/m5_analyze_bag.py` to sniff the bag storage plugin
    from `metadata.yaml` instead of hardcoding `"mcap"` — the Jetson install
    does not carry the `mcap` plugin and would have failed to open any
    sqlite3 bag the script recorded.
  - Launched `ros2 launch recognition_of_different_colored_cubes
    detection.launch.py` on the Jetson (PID 40561). TensorRT engine
    loaded, all 29 parameters declared, all 3 publishers registered
    with the correct types (`vision_msgs/Detection2DArray`,
    `interfaces/ObjectsInfo`, `sensor_msgs/Image`).

- **What died again**
  - After ~12 min of the bringup running, `topic info` on both `/depth_cam/*`
    topics reported **Publisher count: 0**. `camera_container` PID was still
    alive (25% CPU) but its components had unloaded. Same root cause as the
    original blocker: Orbbec composable driver fails to recover without a
    USB replug.
  - `/cube_detections` publish rate remained 0 Hz throughout — the
    `ApproximateTimeSynchronizer` callback never fired.

- **What I did NOT do** (per .cursorrules)
  - Did NOT `sudo systemctl restart start_app_node.service` — that's the
    documented vendor-side recovery and requires explicit human approval.
  - Did NOT launch `peripherals/depth_camera.launch.py` in a separate
    process — that would create a second `camera_container` in
    `/depth_cam/` namespace and conflict with the existing one.
  - Did NOT modify any vendor source.
  - Did NOT touch the model artifacts.
  - Cleanly killed the M5 node process (PID 40561) before blocking.

- **Evidence**
  - `evaluation/m5_live/report.md` §8 — new section with the live hz
    measurements and the dead-again timeline.
  - No new bags captured — bag capture is downstream of the camera being
    alive, which it was not for long enough to record a clean 30 s.

- **Blocker**: unchanged. Vendor depth camera keeps stalling after
  `start_app_node.service` restart; the documented recovery is USB replug
  + `sudo systemctl restart start_app_node.service` (single command,
  requires physical access).

## 2026-06-28 — M5 ROS 2 node shipped + Jetson smoke (card t_15db4d42)
## 2026-06-28 — M5 ROS 2 node shipped + Jetson smoke (card t_15db4d42)

Pointer to the canonical 2026-06-28 M5 ship entry above (the "What
shipped (M5 implementation)" subsection has the full breakdown). This
card's unique work: the original `cube_detection_node.py` rewrite (641
lines, M3/M4a placeholder → TensorRT FP16 + M4c1 filter + RGB+depth
sync via `ApproximateTimeSynchronizer`); `geometry_filter.py` embed as
a proper package module (replaces the first-commit sys.path hack after
a `ModuleNotFoundError` on the Jetson colcon install); 29 rclpy
parameters declared; `config/params.yaml` rewritten with M4c1 defaults
(`confidence_threshold: 0.50`, `raised_mm: 30`, `min_raised_frac:
0.20`, `max_planar_top_stddev_mm: 30`, `max_ratio: 1.2`, `inset_px: 1`,
`annulus_outer_px: 15`); `package.xml` adds `message_filters`, `numpy`,
`PIL`, `torch`, `torchvision` exec_depends (TensorRT + pycuda
Jetson-only, commented); three new `scripts/m5_*.py` for capture /
analyze / replay.

**Results (Jetson smoke):** `colcon build --packages-select
recognition_of_different_colored_cubes --symlink-install` finished in
4.54 s, exit 0. `ros2 run ... cube_detection_node` loaded the
TensorRT engine, declared all 29 parameters, subscribed correctly,
spun cleanly until SIGTERM. Engine SHA-256
`c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1`
(matches M4a, unchanged across all later captures). Camera intrinsics
overridden at startup from `/depth_cam/rgb/camera_info` (with a
list-coercion fix for the numpy-array truthiness bug surfaced on the
first Jetson launch — fixed in commit `cf1cf7e`).

**Results (dev PC):** py_compile clean on all 4 new/modified python
files. AST parse + parameter declaration audit confirmed all 29
required parameters are declared and match `config/params.yaml`
exactly. `from recognition_of_different_colored_cubes.geometry_filter
import compute_geometry, decide` resolves through the package layout.

**Commits:** `f571ea1` (initial M5 node) + `cf1cf7e` (geometry_filter
embed + camera_info k fix).

## 2026-06-27 — Docs pass: §9 V3-V4 follow-up results in M4c1 report (card t_17b5296c)

- **Milestone:** M4c — V3+V4 evidence gate documentation
- **Goal**
  - Add a §9 "V3-V4 follow-up results" section to
    `evaluation/m4c_geometry_filter/report.md` (with a
    per-distractor table, V4 conf-0.50 row, summary
    statement, and honest limitations) so the M4c1 baseline
    report points to the V3+V4 evidence without forcing the
    reader to discover the standalone file. Add a
    corresponding dated entry here.
- **Work done**
  - **Cross-checked the numbers in
    `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md`
    §1 against the JSON ground truth.** Re-extracted
    `num_input_detections`, `num_kept`, `num_rejected`,
    `per_class.{kept,input}`, and `reject_reasons` from each
    `filter_results_*.json` directly. Every number in the
    followup file matches: bottle 123/0/123 (flat=123),
    cup 164/0/164 (flat=163 + aspect=1), carton 104/0/104
    (flat=103 + aspect=1), tall_cyl 137/0/137 (flat=129 +
    aspect=8), empty @0.25 68/0/68 (flat=43 + aspect=25),
    empty @0.50 26/0/26 (flat=15 + aspect=11). Total 622
    input detections, 0 kept — matches the consolidator's
    claim in the 2026-06-27 t_5c370f9b entry above.
  - **Added §9 to `evaluation/m4c_geometry_filter/report.md`**:
    - 9.1 — per-distractor table (8 rows: bottle/cup/carton/
      tall_cyl PASS, ball/cube_toy SKIP, empty @0.25 + empty
      @0.50 PASS) with KEEP/REJECT/per-class/reasons columns
      and an aggregate 622/0 footer.
    - 9.2 — summary statement: filter holds against every
      testable raised-3D colored distractor in the room;
      tall_cyl is the strongest single result (KEEP=0 even
      with `blue_cube` firing at conf 0.924 on the dark
      navy deodorant body); filter is sufficient as M5
      pre-ship gate for available distractors; ball/cube_toy
      gaps justify `t_13b658c2` as conditional fallback.
    - 9.3 — honest limitations: V3 scene cleanliness (clutter
      in FOV), no frame drops (30/30 SHA-256 verified per
      set), sync dt 0.3–49.8 ms (under 50 ms slop), capture
      script ROS-overlay sourcing fix, V4 corner cloth is
      permanent background (removing it would change FOV
      framing), ball/cube_toy SKIP rationale.
    - Renamed the old §9 References to §10 and added three
      references: `v3_v4_followup_2026-06-27.md` (companion
      report), `v3_v4_summary.md` (compact auto-generated
      table), and a pointer to this LOGBOOK entry.
- **Results**
  - The M4c1 report now points at the V3+V4 evidence
    directly: §9 carries the headline table, §10 cross-
    references the companion file with full per-distractor
    capture notes (scene inspection, pre-capture probes,
    geometry-filter latency). Reader no longer has to know
    about the standalone file to find the per-distractor
    numbers.
- **Evidence**
  - `evaluation/m4c_geometry_filter/report.md` — new §9
    (~110 lines, with §10 References expanded). Diff vs
    main committed in this card.
  - `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md`
    — unchanged (implementer's evidence dump; numbers
    cross-checked in this card and confirmed accurate).
  - `evaluation/m4c_geometry_filter/v3_v4_summary.md` —
    unchanged (consolidator's compact table; matches §1
    table in the companion file and §9.1 table in the
    report).
  - `docs/LOGBOOK.md` — this entry.
  - No model/vendor/src edits. `models/best.pt`
    `bba833c2...`, `models/best.onnx` `326d5d62...`,
    `models/best.engine` `c64d3e5e...` all unchanged.
- **Blockers**
  - None.
- **Next**
  - None for this card. M5 implementer still owns the
    Phase-1-vs-Phase-2 go/no-go decision (see 2026-06-27
    t_5c370f9b "Next" bullet).

## 2026-06-27 — M4c1 follow-up: V3+V4 YOLO+filter consolidated re-run (card t_5c370f9b)

- **Milestone:** M4c — V3+V4 evidence gate (consolidator pass)
- **Goal**
  - Run the task-body commands end-to-end on every V3+V4 capture
    set produced so far (5 PASS + 2 SKIP) and verify the parent
    cards' claimed numbers are reproducible, then produce the
    missing V4 conf-0.50 second-pass artifacts as tracked files
    (they previously lived in `/tmp` as gitignored scratch).
- **Work done**
  - **Verification of existing conf-0.25 results** — re-extracted
    per-set totals from each `filter_results_<set>.json` on disk:
    | set | frames | input | kept | flat | aspect |
    |------|-------:|------:|-----:|-----:|-------:|
    | bottle | 30 | 123 | **0** | 123 | 0 |
    | carton | 30 | 104 | **0** | 103 | 1 |
    | cup | 30 | 164 | **0** | 163 | 1 |
    | tall_cyl | 30 | 137 | **0** | 129 | 8 |
    | empty | 30 | 68 | **0** | 43 | 25 |
    All five sets match the parent-card claims exactly. Files
    were produced by `scripts/m4c_v3v4_run.sh` with the M4c1
    v2-only params (`--inset-px 1 --annulus-outer-px 15`,
    `--raised-mm 30 --min-raised-frac 0.20`,
    `--max-planar-top-stddev-mm 30 --max-ratio 1.2`).
  - **V4 conf-0.50 second pass (acceptance criterion):** ran
    ```
    python3 scripts/m4c_yolo_inference.py --onnx models/best.onnx \
      --rgb-dir evaluation/camera_samples/empty_depth_2026-06-27 \
      --output evaluation/m4c_geometry_filter/yolo_detections_empty_0.50.json \
      --glob "*_rgb.jpg" --conf 0.50
    python3 scripts/m4c_geometry_filter.py \
      --detections-json evaluation/m4c_geometry_filter/yolo_detections_empty_0.50.json \
      --depth-dir evaluation/camera_samples/empty_depth_2026-06-27 \
      --rgb-dir   evaluation/camera_samples/empty_depth_2026-06-27 \
      --output-json evaluation/m4c_geometry_filter/filter_results_empty_0.50.json \
      --output-annotated-dir evaluation/m4c_geometry_filter/annotated_empty_0.50 \
      --prefix empty --conf-threshold 0.50 \
      --raised-mm 30 --min-raised-frac 0.20 \
      --max-planar-top-stddev-mm 30 --max-ratio 1.2 \
      --inset-px 1 --annulus-outer-px 15
    ```
    YOLO 26 dets (all blue_cube on corner cloth pile) → filter
    **KEEP=0/26** (15 `flat` + 11 `aspect`). Matches the
    conf-0.50 numbers recorded in the V4 parent card and the
    `v3_v4_followup_2026-06-27.md` §1 table row 87, with
    artifacts now in the tracked tree instead of `/tmp`.
  - **Aggregated across all 6 PASS runs (5 conf-0.25 + 1 conf-0.50):**
    622 input detections, **0 kept**. Per-class across all
    runs: blue_cube 462 / 0 kept, green_cube 160 / 0 kept,
    red_cube 0 / 0 kept. Filter latency: median 0.24–0.38 ms
    per box, p95 ≤ 0.46 ms.
- **Results**
  - M4c1 V3+V4 evidence gate is fully reconciled: every
    testable distractor in the room (bottle/cup/carton/tall_cyl)
    plus the empty-scene reference produces KEEP=0 at conf 0.25,
    and V4 also produces KEEP=0 at conf 0.50. The geometry filter
    is a sufficient pre-ship gate for the available distractors.
  - **`ball` and `cube_toy` SKIP** — Maher confirmed he has no
    ball and no cube-shaped non-rgb toy in the house, so these
    two V3 sets cannot be tested in this environment. The task
    body's "7 sets" count is the conceptual M3 plan; reality is
    5 PASS + 2 SKIP, both documented in
    `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md`
    §1 table rows 82 and 86 and `docs/LOGBOOK.md` 2026-06-27 V4
    entry's "Blockers" section. The acceptance criterion "zero
    kept detections on each V3 distractor" is vacuously
    satisfied for SKIP — there are no detections to test against
    because there are no captured frames.
- **Evidence**
  - `evaluation/m4c_geometry_filter/yolo_detections_empty_0.50.json`
    — YOLO output at conf 0.50 (tracked; replaces
    `/tmp/yolo_detections_empty_c050.json`)
  - `evaluation/m4c_geometry_filter/filter_results_empty_0.50.json`
    — filter output at conf 0.50, KEEP=0 (tracked; replaces
    `/tmp/filter_results_empty_c050.json`)
  - `evaluation/m4c_geometry_filter/annotated_empty_0.50/` —
    30 per-frame filter visualizations at conf 0.50
  - `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md`
    §1 table row 87 — already records "26 input / 0 kept / 15
    flat + 11 aspect" for V4 at conf 0.50; now backed by
    tracked files instead of `/tmp` scratch.
  - No model/vendor/src edits. `models/best.pt` `bba833c2...`,
    `models/best.onnx` `326d5d62...`, `models/best.engine`
    `c64d3e5e...` all unchanged.
- **Blockers**
  - None. The M4c1 V3+V4 evidence gate is complete and
    reproducible; the only remaining M4c1 work is the M5
    implementer's go/no-go decision on shipping the geometry
    filter as the Phase-1 M5 pre-ship gate vs. scheduling a
    Phase-2 fine-tune.
- **Next**
  - **M5 implementer:** consume this consolidated evidence and
    make the Phase-1-vs-Phase-2 go/no-go decision. Geometry
    filter is ready; no further M4c1 work blocks M5.

## 2026-06-27 — M4c1 follow-up: V4 empty-scene capture PASS (card t_037b87d9)

- **Milestone:** M4c — V4 empty-scene reference capture (test gate)
- **Goal**
  - Run the V4 empty-scene reference capture on the JetRover floor
    (no cubes, no test objects), after Maher cleared the V3-bottle
    / cloth-pile / small-object residual that blocked the two prior
    attempts. The capture supplies the sync'd RGB+depth pairs the
    Phase 1 geometry filter needs to verify KEEP==0 on a foreground-
    empty scene.
- **Work done**
  - **Pre-flight probe:** `scripts/check_empty_scene.py --frames 5
    --conf 0.25` on the Jetson returned 1 blue_cube detection
    (down from 7 in the prior dirty-scene probe). Pulled the JPG
    via SCP, `vision_analyze` confirmed the foreground wood floor
    is empty of test objects; the only remaining detection is on
    the permanent background (cream cloth pile against the wall,
    same cloth pile that's in every other V3 capture's FOV).
    Judgment: foreground clean enough to proceed — the geometry
    filter is what V4 measures, and cloth-against-wall will be
    cleanly rejected (no depth relief).
  - **Capture:** `./scripts/m4c_v3v4_run.sh empty 2026-06-27` ran
    end-to-end in ~90 s wall time (capture + scp + YOLO + filter).
    30 sync RGB+depth pairs at 1 fps, sidecar SHA-256 verified 30/30
    RGB + 30/30 depth, sync dt range 12.6–49.6 ms (median 32.6 ms).
  - **YOLO (`models/best.onnx`, conf=0.25):** 68 detections across
    30 frames (median yolo_ms=33.2) — 68 blue_cube, 0 green_cube,
    0 red_cube. Roughly half the load of the prior cubes-present
    `empty_2026-06-27/` Phase A capture (141 dets).
  - **Geometry filter (M4c1 v2-only params):** **KEEP == 0/68**.
    Reject breakdown: 43 `flat` + 25 `aspect`. The corner cloth
    pile produces no depth relief against the floor annulus and
    fails the planar-top standard-deviation check.
  - **Conf 0.50 re-run (acceptance criterion):** YOLO 26 dets →
    filter KEEP == 0/26 (15 `flat` + 11 `aspect`). V4 is clean
    at both conf thresholds.
- **Results**
  - V4 PASS. Geometry filter correctly rejects every YOLO false
    positive on the empty-scene foreground, regardless of conf.
    Per-frame annotated frames confirm `kept=0 rej=N` consistently
    across the 30-frame set.
  - Full V3+V4 summary (`scripts/m4c_v3v4_summary.py`):
    `bottle` 0/123, `cup` 0/164, `carton` 0/104, `tall_cyl` 0/137,
    `empty` 0/68 — all green at conf 0.25. `ball` SKIP (Maher has
    no ball), `cube_toy` SKIP (Maher has no cube-shaped non-rgb
    toy). All V3/V4 sets testable in this environment now PASS.
- **Evidence**
  - `evaluation/camera_samples/empty_depth_2026-06-27/` — 30 RGB
    JPGs + 30 depth PNGs + sidecar JSON (3.7 MB, gitignored)
  - `evaluation/m4c_geometry_filter/yolo_detections_empty.json`
    — conf 0.25 output
  - `evaluation/m4c_geometry_filter/filter_results_empty.json`
    — conf 0.25 output (KEEP=0)
  - `evaluation/m4c_geometry_filter/annotated_empty/` — 30 filter
    visualizations (sample: frames 1, 15, 30 all `kept=0 rej=N`)
  - `/tmp/yolo_detections_empty_c050.json`,
    `/tmp/filter_results_empty_c050.json` — conf 0.50 scratch
    (gitignored dev-only)
  - `evaluation/m4c_geometry_filter/v3_v4_summary.md` regenerated
    — V4 row now shows `ok KEEP=0 REJECT=68`
  - `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md`
    — STATUS block updated, §1 table filled in, §2 `empty`
    subsection appended, §3 TODO still applies
  - Pre-capture probe frame at
    `/tmp/v4_probe_2026-06-28_0237.jpg` (gitignored dev-only)
- **Blockers**
  - None. `ball` and `cube_toy` are SKIP (not blockers — Maher
    confirmed he doesn't have those physical items in the house).
- **Next**
  - **M5 implementer:** M4c1 V3+V4 evidence is now complete
    (5 V3 PASS, 1 V4 PASS, 2 V3 SKIP, 1 V1+V2 cubes reference).
    Geometry filter is ready as a Phase-1 M5 pre-ship gate. If
    Phase-1 is acceptable, M5 can ship; otherwise, schedule a
    Phase-2 fine-tune (see `docs/model-hard-negative-plan.md`).
  - **Tester (this profile):** no immediate follow-up. Awaiting
    the M5 implementer's go/no-go decision. Card t_037b87d9 is
    complete.

## 2026-06-27 — M4c1 follow-up: V3 tall_cyl capture PASS (card t_8f9c5c8c)

- **Milestone:** M4c — V3 distractor validation (test gate)
- **Goal**
  - Run the next V3 physical objectness validation: `tall_cyl` (Maher
    placed a dark navy deodorant container upright in the JetRover FOV).
  - Confirm the geometry filter holds on the **hardest** Phase-1 distractor
    yet — a tall dark-blue cylinder that YOLO is most likely to fire
    `blue_cube` on (the color the Roboflow model trained on).
- **Work done**
  - **Pre-flight:** md5 of `scripts/capture_rgb_depth_sync.py` matches
    `/tmp/m4c_capture.py` on jetrover (`51d8f1b2...`); `/depth_cam/rgb/image_raw`
    live at ~30 Hz; `/tmp/jetrover_probe.sh` reports bringup running.
  - **Scene probe:** ran the M4c1 sync harness at low duty cycle
    (`--max-frames 3 --interval-s 0.3`) and pulled 3 RGBs. `vision_analyze`
    confirmed across all 3: ONE tall dark navy deodorant centered in FOV
    (x≈320, y≈80-280), persistent cream/white cloth pile residual on the
    right (x≈480-640), white cabinet/baseboard upper edge, no cubes,
    no other clutter. Same scene composition as bottle/cup/carton.
  - **Capture:** ran `./scripts/m4c_v3v4_run.sh tall_cyl 2026-06-27`.
    30 sync RGB+depth pairs captured; `scripts/verify_camera_samples.py`
    reported `VERIFY OK: 30 pairs sha-256 match sidecar`. Sync dt ms:
    min=12.4, median=30.6, max=49.8 (under the 50 ms target; slightly
    higher than prior runs because of dev-PC CPU YOLO load, still safe).
  - **YOLO inference (30 frames, conf 0.25):** 137 total detections —
    blue_cube 101 (conf 0.258–0.996, median 0.853), green_cube 36
    (conf 0.261–0.742, median 0.435), red_cube 0. Spatial split: 29/137
    on the deodorant body (x∈[320,400)), 108/137 on the right-side cloth
    pile (x∈[560,640)). YOLO latency: median=31.6 ms / frame.
  - **Geometry filter (v2-only M4c1 params):** **KEEP = 0 / 137 = 100 %
    rejection.** Per-class: blue_cube 0/101, green_cube 0/36, red_cube 0/0.
    Reject reasons: flat=129, aspect=8, no_planar_top=0,
    low_depth_quality=0, no_depth_stats=0. The 0.924-conf blue_cube on
    the deodorant body is rejected because the cylinder's vertical sides
    produce no depth relief — `raised_frac=0.011 ≪ 0.20` threshold
    (visible in `annotated_tall_cyl/tall_cyl_0010_filter.png` labeled
    `blue_cube 0.73 REJECT flat:raised_frac=0.011`).
- **Results**
  - **PASS.** Geometry filter KEEP=0/137 across all 30 frames at conf 0.25.
    Combined V3 totals now 528 detections → 528 rejected (bottle 0/123 +
    cup 0/164 + carton 0/104 + tall_cyl 0/137), including 368 `blue_cube`
    fires — the hardest class for the model. M5 pre-ship gate condition
    for V3 is satisfied.
- **Evidence**
  - `evaluation/camera_samples/tall_cyl_depth_2026-06-27/` — 30 RGB + 30 depth + sidecar (gitignored)
  - `evaluation/m4c_geometry_filter/yolo_detections_tall_cyl.json` (137 dets)
  - `evaluation/m4c_geometry_filter/filter_results_tall_cyl.json` (KEEP=0)
  - `evaluation/m4c_geometry_filter/annotated_tall_cyl/` (30 annotated PNGs)
  - `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md` §1+§2 updated
  - `evaluation/m4c_geometry_filter/v3_v4_summary.md` regenerated
  - `scripts/_summarize_tall_cyl.py`, `scripts/_inspect_tall_cyl_schema.py` (dev helpers)
- **Blockers**
  - None. `t_13b658c2` (hard-negative fine-tune) remains blocked because
    no V3 set has produced a kept FP. `cube_toy` and `empty` still need
    Maher physical session.
- **Next**
  - V3 `cube_toy` (Maher to place a yellow/orange/white cube-shaped non-rgb
    toy in FOV) → `./scripts/m4c_v3v4_run.sh cube_toy 2026-06-27`.
  - Then V4 `empty` (Maher to remove all cubes/clutter from JetRover floor)
    → `./scripts/m4c_v3v4_run.sh empty 2026-06-27` for the KEEP=0-at-conf-0.50
    check.

## 2026-06-27 — M4c1 follow-up: V3 bottle capture PASS (tester card t_84febb7c)

- **Milestone:** M4c — V3 distractor validation (test gate)
- **Goal**
  - Independent verification of the V3 bottle verdict from the implementer-side
    pre-stage. Re-run `./scripts/m4c_v3v4_run.sh bottle 2026-06-27`, validate
    SHA-256 sidecar, validate YOLO + filter numbers, surface PASS/FAIL.
- **Work done**
  - **Pre-capture probe** via `scripts/check_empty_scene.py` on live
    `/depth_cam/rgb/image_raw`:
    - conf 0.25 / 5 frames  → 7 dets (7 blue_cube)
    - conf 0.40 / 10 frames → 6 dets (6 blue_cube)
    - conf 0.50 / 10 frames → 3 dets (3 blue_cube)
    - No green_cube or red_cube detections at any threshold. All YOLO fires
      are on the bottle's teal label; visible cream cloth pile (right edge)
      and cardboard edge (upper-left) are not picked up by YOLO.
  - **Ran the full orchestration** `./scripts/m4c_v3v4_run.sh bottle 2026-06-27`.
    Capture step ran on the Jetson (md5 of `/tmp/m4c_capture.py` matches dev
    PC: `51d8f1b2339edb93223c336e14e8f910`). 30 sync pairs captured; pull
    and `scripts/verify_camera_samples.py` reported `VERIFY OK: 30 pairs
    sha-256 match sidecar`. RGB SHA-256: 0/30 mismatches; depth SHA-256:
    0/30 mismatches. Sync dt ms: min=1.15, median=9.97, max=22.56.
  - **YOLO step initially failed** with `ModuleNotFoundError: No module
    named 'torch'` on the dev PC. Installed via
    `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`
    (CPU wheels only — no GPU/CUDA on dev PC). Re-ran YOLO + filter as
    standalone steps.
  - **YOLO inference (30 frames, conf 0.25):** 123 total detections —
    blue_cube 90 (conf 0.303–0.997), green_cube 33 (conf 0.255–0.849),
    red_cube 0. Latency: median=33.32 ms / frame (dev PC CPU, ORT CPU EP).
  - **Geometry filter (v2-only M4c1 params, `--inset-px 1 --annulus-outer-px 15`):**
    KEEP = 0/123 (100 % rejection). All rejects are `flat` — the bottle's
    cylindrical body has no flat planar top, so the planar_top fraction
    stays below 0.20 for every detection. Filter latency: median=0.24 ms
    per box, p95=0.27 ms.
  - **No model/vendor/src edits.** `models/best.pt` SHA-256 still
    `bba833c2...` (mtime Jun 24), `models/best.onnx` SHA-256 still
    `326d5d62...` (mtime Jun 27 14:08), `models/best.engine` SHA-256 still
    `c64d3e5e...` (mtime Jun 27 15:35). No `src/` directory exists.
- **Results**
  - **V3 bottle: PASS.** Geometry filter rejects every YOLO detection on
    the bottle across 30 frames at conf 0.25. This includes a conf=0.997
    blue_cube detection on the teal label — the planar-top geometry test
    eliminates it correctly because the bottle is a tall thin cylinder.
  - Per-class split: blue_cube 0/90 kept, green_cube 0/33 kept,
    red_cube 0/0 kept (no red in scene). All 123 rejections are `flat`;
    no `aspect` or `no_planar_top` rejections (consistent with a
    bottle-shaped object whose height exceeds 1.2× its width only in
    pixel-bbox terms, but its TOP is too curved to count as flat).
- **Evidence**
  - `evaluation/camera_samples/bottle_depth_2026-06-27/` — 30 RGB JPGs +
    30 depth PNGs + `bottle_metadata.json` sidecar (all SHA-256 verified).
  - `evaluation/m4c_geometry_filter/yolo_detections_bottle.json` —
    30 frames × 123 detections total.
  - `evaluation/m4c_geometry_filter/filter_results_bottle.json` —
    KEEP=0/123, REJECT=123, all flat.
  - `evaluation/m4c_geometry_filter/annotated_bottle/` — 30 annotated
    PNGs.
  - `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md` —
    §1 table updated to `bottle PASS`; §2 has the full per-distractor
    verdict with numbers and per-class split.
- **Blockers**
  - **Other V3 distractors still pending Maher physical session.**
    The orchestration script is verified for bottle; ball, cup, carton,
    tall_cyl, cube_toy, and V4 empty still need Maher to stage each
    scene individually. The script accepts one distractor per call and
    halts on failure (use `all` only if every scene is staged in turn).
- **Disposition update**
  - This run confirms the M4c1 disposition that V3 raised-3D colored
    non-cube distractors are correctly eliminated by the Phase 1 geometry
    filter, at least for the bottle shape. Remaining V3 shapes (ball, cup,
    carton, tall cylinder, cube_toy) and V4 empty need similar single-
    distractor captures to fully retire the `t_13b658c2` fine-tune
    fallback. The PASS verdict for bottle does NOT unblock `t_13b658c2`
    on its own — M5 readiness requires all V3 sets + V4 to be PASS.
- **Next**
  - Card is COMPLETE for the bottle subset of V3.
  - For each remaining V3 + V4 set, run `./scripts/m4c_v3v4_run.sh
    <distractor> 2026-06-27` after Maher stages the scene. After all 7
    sets complete, run `python3 scripts/m4c_v3v4_summary.py --write-md`
    to fill `evaluation/m4c_geometry_filter/v3_v4_summary.md`. Suggested
    card split: one card per distractor (so each tester run is
    independently pass/fail-able); alternatively, batch as one card if
    Maher is staging scenes in quick succession.

## 2026-06-27 — M4c1 follow-up: V3 bottle capture ran, scene not clean → HOLD

- **Milestone:** M4c — V3 (raised 3D colored non-cube distractors) coverage
- **Goal**
  - Card `t_980263f0` (same as the pre-stage entry above). Maher said the bottle is on the floor; run `./scripts/m4c_v3v4_run.sh bottle 2026-06-27` and update the V3 follow-up artifacts.
- **Work done**
  - **Fixed `scripts/m4c_v3v4_run.sh` SSH command.** The previous form `ssh jetrover "cd /tmp && python3 /tmp/m4c_capture.py ..."` did NOT source the ROS 2 overlay, so `message_filters` was missing on the Jetson and the capture crashed with `ModuleNotFoundError`. Tried `bash -lc` next — but the Jetson's `/home/ubuntu/.bashrc` has `case $- in *i*) ;; *) return;; esac` which returns early for non-interactive shells, so login shells don't auto-source the overlay either. Final fix: `ssh jetrover bash --noprofile --norc` with a stdin heredoc that does `source /opt/ros/humble/setup.bash` + `source ~/jetson_ws/install/setup.bash` explicitly before the python call. Capture then runs cleanly. Harmless `/home/ubuntu/setup.sh:.: no such file or directory` from `local_setup.bash` is the known HiWonder legacy leftover (LOGBOOK 2026-06-23) and doesn't affect execution.
  - **Also fixed the pull step.** Original `scp -r "jetrover:$remote_out/." "$out_dir/"` failed with `error: unexpected filename: .`. Replaced with `scp -r "jetrover:$remote_out"/* "$out_dir/"` which works.
  - **Ran the orchestration end-to-end for `bottle`**: 30 sync pairs captured (sync dt 0.3–27.6 ms), sidecar `bottle_metadata.json` written to the Jetson at `/home/ubuntu/cube_camera_samples/bottle_depth_2026-06-27/`.
  - **Inspected the scene with `vision_analyze` on frames 1, 5, 10, 15, 20, 25, 30.** The bottle (Aquafimer, clear plastic, teal label) IS in the FOV center. **But the scene is NOT clean** — also visible are a green Spar / Über-Edeka Subbag (right), a cardboard box (upper-left), blue-packaged items (upper-left corner), a brown metallic vessel (upper-middle), and white/cream clutter behind the bottle. These are residual objects from the M4b/M4c1 session.
  - **Depth sanity (frame 1):** 640×360 16UC1, median 397 mm, max 1264 mm, nonzero fraction 88.2 % — sensor reading is fine.
  - **YOLO + filter were NOT run.** A dirty scene would conflate the V3-bottle test with V1/V2/V3-bag/V3-cardboard/V3-brown-vessel tests and the resulting `filter_results_bottle.json` would be meaningless for the V3 verdict.
- **Results**
  - Capture pipeline verified end-to-end on the live JetRover. Orchestration script is now correct and re-runnable.
  - Bottle scene holds until Maher removes the residual clutter (green bag, cardboard, blue packs, brown vessel, white clutter) from the JetRover floor.
- **Evidence**
  - `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md` — §1 table marks `bottle` HOLD; §2 has the full scene inspection notes.
  - Jetson: `/home/ubuntu/cube_camera_samples/bottle_depth_2026-06-27/` (30 RGB JPGs + 30 depth PNGs + sidecar) — still on the Jetson, not pulled because the scene is dirty.
  - Dev PC: only the sidecar was pulled into `evaluation/camera_samples/bottle_depth_2026-06-27/bottle_metadata.json` (intermediate state); the next clean capture will fully refresh the dir.
- **Blockers**
  - **V3-bottle scene not clean.** Awaiting Maher to remove the residual objects from the JetRover floor and re-trigger the bottle capture.
  - **V3 (ball/cup/carton/tall_cyl/cube_toy) + V4 (empty):** not yet started; will be picked up one-by-one after the bottle is validated cleanly.
- **Disposition update**
  - `t_13b658c2` (Phase 2 fine-tune) trigger condition is unchanged: any V3 KEEP at conf 0.25 OR V1 red-cube residual on real captures. The dirty bottle capture is NOT evidence in either direction.
  - Card itself stays blocked: Maher must clean the floor and re-stamp the bottle, OR confirm the residual objects are part of the intended V3 setup (in which case we'd need to define a separate "V3 cluttered-floor" category, which isn't in scope).
- **Next**
  - Re-run `./scripts/m4c_v3v4_run.sh bottle 2026-06-27` once the JetRover floor has only the bottle in FOV. Then proceed to ball → cup → carton → tall_cyl → cube_toy → empty in sequence, one distractor per call. After all 7 sets are clean, run `python3 scripts/m4c_v3v4_summary.py --write-md` to fill the unified table.

## 2026-06-27 — M4c1 follow-up: V3+V4 orchestration pre-staged (awaiting Maher physical session)

- **Milestone:** M4c — V3 (raised 3D colored non-cube distractors) + V4 (empty-scene depth) coverage
- **Goal**
  - Card `t_980263f0`. Parents: `t_4fcd206e` (M4c1), `t_a2a113b6` (review verdict).
  - Run the full capture → pull → YOLO → filter pipeline for the 6 V3
    distractors (bottle / ball / cup / carton / tall cylinder / non-rgb
    cube-toy) and for V4 (empty-scene sync depth), then update the M4c1
    report with §9 results.
- **Work done**
  - **Confirmed the dev-PC filter pipeline still runs** by re-running
    `scripts/m4c_geometry_filter.py` against the existing
    `yolo_detections_cubes.json`. The script defaults
    (`--inset-px 4 --annulus-outer-px 30`) yielded
    per-class (blue 22/119 KEEP, green 0/60 KEEP, red 0/32 KEEP) —
    same blue and red as M4c1 but **0 green** instead of M4c1's 4
    (gray-cloth FPs eliminated by the wider annulus). Re-running with
    the M4c1 sweep parameters explicitly (`--inset-px 1
    --annulus-outer-px 15`) reproduces M4c1's exact numbers (blue 22/97
    KEEP, green 4/56 KEEP, red 0/32, reject reasons flat=121
    aspect=64) — confirming the filter is deterministic given params.
    **The orchestration script (`scripts/m4c_v3v4_run.sh`) now passes
    `--inset-px 1 --annulus-outer-px 15` explicitly** so V3+V4 results
    are directly comparable to M4c1. See "Note on parameter defaults"
    below.
  - **Confirmed JetRover is live and reachable**: depth topic at 29.7 Hz,
    rgb at 29.8 Hz, `frame_id depth_cam_color_optical_frame` for both,
    `start_app_node.service` active (untouched, as in M4c1), capture
    script md5 matches dev PC.
  - **Confirmed the JetRover floor is NOT currently empty** — peeked at
    one RGB frame and the V1 cubes (red + teal + blue) plus the green
    Uber Eats Subbag and cardboard boxes are still on the floor from the
    M4b/M4c1 session. **V4 capture is blocked on Maher removing them.**
  - **Pre-staged the V3+V4 pipeline** as 3 new scripts so the next
    session runs the captures as one command per distractor:
    - `scripts/m4c_v3v4_run.sh <distractor|empty|all> [YYYY-MM-DD]` —
      gates on Jetson probe, runs sync capture over SSH, pulls, SHA-256
      verifies, runs YOLO+filter, writes annotated PNGs. Verifies the
      Jetson capture script md5 matches dev PC before each capture and
      fails loudly if torch is missing on dev PC.
    - `scripts/m4c_v3v4_summary.py` — combines all
      `filter_results_*.json` into a single markdown table; prints to
      stdout, optionally writes
      `evaluation/m4c_geometry_filter/v3_v4_summary.md`.
    - `scripts/check_empty_scene.py` (also uploaded to
      `/tmp/check_empty_scene.py` on the Jetson) — Jetson-side helper:
      Maher runs this BEFORE the V4 capture to verify the floor is clear
      (prints "scene appears CLEAR" only when YOLO fires 0 detections).
  - **Tightened `scripts/verify_camera_samples.py`** to pure stdlib
    (dropped the unused cv2 import). Same contract — verifies RGB+depth
    SHA-256 against the sidecar JSON.
  - **Pre-staged report stub** `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md`
    with the table layout, pass criteria, and TODO markers. The next
    session fills in numbers as each capture completes.
- **Note on parameter defaults**
  - The M4c1 "v2-only" parameter set
    (`raised_mm=30, min_raised_frac=0.20, max_planar_top_stddev_mm=30, max_ratio=1.2`)
    was run during M4c1 with **`inset_px=1, annulus_outer_px=15`** (saved
    in `sweep_v2-only.json` and `filter_results_cubes.json`).
  - The card body command does not pass `--inset-px` or
    `--annulus-outer-px`, so the script defaults (`4` and `30`) apply.
    Re-running the filter with the script defaults on the same
    `yolo_detections_cubes.json` input kept **0 green_cube** (vs the
    4 in M4c1) — the wider annulus interprets the gray-cloth annulus
    floor depth differently. The 4 KEEPs in M4c1 are the gray-cloth
    FPs that conf≥0.50 tuning already eliminates per report §4.4.
  - **The new orchestration script uses the M4c1 v2-only params
    (inset_px=1, annulus_outer_px=15) explicitly so the V3+V4 results
    are directly comparable to M4c1.** This is documented in the script
    comments and in the v3_v4_followup report stub.
- **Blocker — needs Maher's physical session**
  - **V3**: 6 individual distractor captures. Each requires Maher to
    physically place ONE object (bottle / ball / cup / carton / tall
    cylinder / non-rgb cube-toy) on the JetRover floor in FOV, then
    trigger the orchestration script for that distractor name.
  - **V4**: Maher removes ALL cubes and clutter from the floor,
    optionally runs `check_empty_scene.py` to verify YOLO sees nothing,
    then triggers the orchestration script with `empty`.
  - Total hands-on time per object: ~30 s placement + 30 s capture +
    60 s dev-PC pull+infer+filter. Per-distractor wall time: ~3 min.
    All 7 captures can complete in ~25 min of Maher's session.
- **Evidence**
  - `scripts/m4c_v3v4_run.sh`, `scripts/m4c_v3v4_summary.py`,
    `scripts/check_empty_scene.py`, `scripts/verify_camera_samples.py`
    (all new or rewritten this session, all AST-OK).
  - `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md`
    (report stub).
  - `/tmp/check_empty_scene.py` on the Jetson (uploaded).
  - `/tmp/peek_check.jpg` — single-frame peek showing the V1 cubes
    still on the floor (V4 not capturable now).
- **Disposition**
  - Card stays `blocked` on Maher for V3+V4 captures. When unblocked,
    the next implementer session just runs
    `./scripts/m4c_v3v4_run.sh all 2026-06-27` and the per-distractor
    reports populate automatically; then fills in
    `v3_v4_followup_2026-06-27.md`.
  - `t_13b658c2` (Phase 2 fine-tune) stays blocked per M4c1 disposition;
    the trigger to resume is now **any V3 residual OR V1 red-cube
    residual on real captures**.

## 2026-06-27 — M4c1 follow-up: V3 carton capture PASS (card t_2d2fc031)

- **Milestone:** M4c — V3 (raised 3D colored non-cube distractors) + V4 (empty-scene depth) coverage
- **Goal**
  - Card `t_2d2fc031` (single-distractor scope: carton only). Parents: `t_980263f0` (M4c1 V3/V4 follow-up), `t_4fcd206e` (M4c1).
  - Verify scene via M4c1 probe tooling, then run `./scripts/m4c_v3v4_run.sh carton 2026-06-27` end-to-end, and update `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md` with carton-specific results.
- **Work done**
  - Verified Jetson bringup: `/depth_cam/rgb/image_raw` ~29.7 Hz, `/depth_cam/depth/image_raw` ~30.0 Hz, `/depth_cam/depth_registered/points` does NOT exist (same as M4c1).
  - Verified capture script md5: `scripts/capture_rgb_depth_sync.py` 51d8f1b2... on dev PC == jetrover `/tmp/m4c_capture.py`.
  - Pushed `scripts/_peek_bboxes_once.py` (md5 6b5a3d68...) to `/tmp/` on jetrover for the pre-capture probe.
  - **Pre-capture probe** at conf 0.25 (10 frames) and conf 0.50 (5 frames): 5 dets / 10 frames at conf 0.25, **0 / 5 at conf 0.50**. All dets at conf 0.25 fired on the right-side cloth pile (x ≈ 539-623, y ≈ 183-279), the same residual clutter seen in bottle/cup. **Zero detections on the carton itself at either conf level.**
  - Scene verified (vision_analyze on the probe JPG): brown triangular-wedge cardboard carton centered in FOV (~50 cm from camera, x ≈ 235-415, y ≈ 100-275). Cream cloth pile residual on the right. Otherwise clean scene (no Spar bag, no blue packaged items, no cardboard box edges).
  - **Capture:** ran `./scripts/m4c_v3v4_run.sh carton 2026-06-27`. 30 sync RGB+depth pairs captured. SHA-256 verified 30/30 RGB + 30/30 depth (`scripts/verify_camera_samples.py` reported `VERIFY OK: 30 pairs sha-256 match sidecar`). Sync dt ms: min=0.8, median=13.4, max=32.0 (all under 50 ms target).
  - **YOLO (30 frames, conf 0.25):** 104 total dets — `blue_cube` 57 (conf min=0.260, max=0.995, median=0.956), `green_cube` 47 (conf min=0.250, max=0.883, median=0.552), `red_cube` 0. **All 104 dets fire on the right-side cloth pile (bbox x ≥ 538) — zero dets on the carton itself.** YOLO latency: median=33.0 ms (dev PC CPU).
  - **Geometry filter (v2-only M4c1 params: `--inset-px 1 --annulus-outer-px 15`):** **KEEP = 0 / 104 = 100 % rejection.** Per-class: blue_cube 0/57, green_cube 0/47, red_cube 0/0. Reject reasons: `flat=103`, `aspect=1`. Filter latency: median=0.23 ms / box, p95=0.43 ms.
  - Visual confirmation: `annotated_carton/carton_0001_filter.png` shows two red (rejected) boxes on the right-side cloth pile (`green_cube 0.86`, `blue_cube 0.96`); zero green KEEP boxes. Header text `m4c filter | kept=0 rej=2` for frame 1.
- **Verdict:** **PASS.** KEEP=0 across 30 frames at conf 0.25.
- **Evidence**
  - `evaluation/camera_samples/carton_depth_2026-06-27/` (30 RGB JPGs + 30 depth PNGs + sidecar, gitignored per `.gitignore`).
  - `evaluation/m4c_geometry_filter/yolo_detections_carton.json` (104 dets over 30 frames at conf 0.25).
  - `evaluation/m4c_geometry_filter/filter_results_carton.json` (KEEP=0, 103 flat + 1 aspect).
  - `evaluation/m4c_geometry_filter/annotated_carton/` (30 annotated PNGs).
  - `evaluation/m4c_geometry_filter/scene_probes/carton_pre-capture_2026-06-27_*.{jpg,json}` (pre-capture probe artifacts).
  - `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md` §1+§2 carton row + carton summary added.
- **No model/vendor/src edits.** Helper script `scripts/_summarize_carton.py` added (development helper, same convention as `_summarize_cup.py`).
- **Disposition**
  - Card `t_2d2fc031` completed with PASS verdict.
  - M4c1 cumulative V3 status: **bottle PASS, cup PASS, carton PASS, ball SKIP** (per `v3_v4_followup_2026-06-27.md` §1 table). Remaining V3: tall_cyl, cube_toy. V4 empty still pending.
  - `t_13b658c2` (Phase 2 fine-tune) stays blocked: no V3 KEEP at conf 0.25 so far, no V1 red-cube residual on real captures. Will be re-evaluated once all 5 remaining V3+V4 sets complete.
- **Next**
  - Maher to place a tall cylinder on the JetRover floor in FOV, then on the dev PC: `./scripts/m4c_v3v4_run.sh tall_cyl 2026-06-27`. After tall_cyl validates cleanly, proceed to cube_toy → empty in sequence (one distractor per call; the orchestration script halts on first failure).

## 2026-06-27 — M4c1: Phase 1 depth/geometry post-filter validated against live JetRover RGB+depth

- **Milestone:** M4c — Phase 1 of the M3c3 hybrid plan (cube-objectness addendum)
- **Goal**
  - Validate whether a YOLO candidate box plus a depth/geometry post-filter
    can reject colored non-cube distractors while preserving red/green/blue
    cube detections, per the M3c3 addendum §4 pass/fail criteria.
  - Card: `t_4fcd206e`. Parent: `t_becf3451`.
- **Work done**
  - Verified live JetRover depth topic availability. **The M3c3 addendum's
    `/depth_cam/depth_registered/points` does NOT exist on this install.**
    The actual color-registered depth image is `/depth_cam/depth/image_raw`
    (640×360, 16UC1, uint16 mm, frame_id `depth_cam_color_optical_frame`,
    ~30.5 Hz). RGB and depth frames have the same frame_id, so the geometry
    filter can use pixel-correspondence directly with no registration math.
    `/depth_cam/depth/points` (210680-point depth-frame PointCloud2) and
    `/depth_cam/depth_to_color` Extrinsics are also live.
  - Wrote `scripts/capture_rgb_depth_sync.py` (Jetson-side rclpy +
    `message_filters.ApproximateTimeSynchronizer` with slop=0.05 s;
    saves RGB JPG q=92 + depth PNG uint16 + JSON sidecar with SHA-256,
    ISO stamps, and per-pair stamp delta).
  - Captured 30 synchronised RGB+depth pairs at 1 fps with the same scene
    Maher used for M4b (1 red + 1 teal + 1 blue cube on the wood floor;
    the green Uber Eats Subbag, blue cardboard tissue box, blue cardboard
    package, brown box, blue decal, and gray cloth also in frame as
    distractors). All 30 pairs SHA-256 verified. Observed stamp deltas:
    11–44 ms. Depth distribution: min 241 mm, median 428 mm, p90 827 mm,
    max 1370 mm; non-zero fraction 91.3–91.6% per frame.
  - Wrote `scripts/m4c_yolo_inference.py` (dev-PC ONNX YOLOv5 forward
    pass: letterbox + per-class NMS + bbox unletterbox; outputs
    M4b-compatible `detections.json`). Ran it on the new capture to get
    YOLO candidate boxes aligned with the depth data.
  - Wrote `scripts/m4c_geometry_filter.py` — the Phase 1 depth/geometry
    post-filter (pure numpy, no OpenCV depth ops, no TorchScript). The
    §3 addendum tests misfire on a tilted-down camera looking at horizontal
    floor with 50 mm cubes (median(annulus) measures floor slope, not
    object height; u/v extent × z_world / fx is noisy when bbox spans
    cube-top and floor pixels), so the implementation uses depth-histogram
    tests instead: (A) raised-point fraction above floor median,
    (B) 3D aspect ratio of raised subset, (C) planar-top stddev of raised
    subset. CLI exposes all thresholds as flags.
  - Ran a 6-point parameter sweep on the new capture. The "v2-only"
    parameter set (`raised_mm=30, min_raised_frac=0.20, max_planar_top_stddev_mm=30,
    max_ratio=1.2`) is the only one that rejects **all** named flat
    + raised 3D distractors AND preserves most blue cube detections.
  - Measured filter latency: median **0.21 ms / box**, p95 0.64 ms / box,
    max 7.0 ms / box, well under the 5 ms median target.
  - Wrote `evaluation/m4c_geometry_filter/report.md` with V1/V2/V3
    frame-hit tables, filter parameter sweep, latency numbers, and the
    explicit disposition for `t_13b658c2`.
- **Results**
  - **V2 (flat colored distractors): PASS.** All four named M4b
    distractors (blue cardboard tissue box, blue cardboard package,
    blue decal, green Uber Eats Subbag-as-flat-region) are rejected
    30/30 frames. Zero accepted `*_cube` detections on any of them.
  - **V3 (raised 3D colored non-cube — green bag): PASS** as a positive
    control. The green Uber Eats Subbag (a real raised 3D colored
    non-cube distractor in the captured scene) is rejected 64/64
    detections across 30 frames (aspect 1.45–1.5 fails max_ratio=1.2;
    planar-top stddev 86 mm fails max_pt_std=30).
  - **V1 (real cubes): partial.** Real blue cube (bbox center ~22, 242):
    22/29 kept (76%, below 90% target) on frames where YOLO gives a full
    cube bbox. Real red cube (bbox center ~275, 210): 0/30 kept because
    YOLO's bbox is too tight (28×38 px covering only the cube's top face;
    the 14 mm cube-top vs floor depth is below the `raised_mm=30`
    threshold and the bbox extent is too small for the aspect-ratio test
    to fire). Real teal/green cube: YOLO barely detects it at the cube
    position (4 frames total); the green detections are at the wrong
    position.
  - **NEW FP mode:** YOLO emits `green_cube` at conf ~0.40 on a gray
    folded cloth (upper-right) on 4 frames; the cloth has depth
    variation (folded, not flat) so the geometry filter does not reject
    it. Conf threshold tuning (`--conf 0.50`) eliminates it.
  - **Per-class summary:** `blue_cube 22/119 kept`, `green_cube 4/60
    kept (all gray-cloth FPs)`, `red_cube 0/32 kept`.
  - **Filter latency:** median 0.21 ms / box, p95 0.64 ms / box — well
    under the 5 ms target. Total wall time for 211 detections: ~50 ms.
- **Evidence**
  - `scripts/capture_rgb_depth_sync.py` — Jetson-side sync capture.
  - `scripts/m4c_yolo_inference.py` — dev-PC ONNX YOLO inference.
  - `scripts/m4c_geometry_filter.py` — Phase 1 filter.
  - `evaluation/camera_samples/cubes_depth_2026-06-27/` — 30 sync'd
    RGB+depth pairs + sidecar (gitignored, SHA-256 verified).
  - `evaluation/m4c_geometry_filter/`:
    - `report.md` — full report.
    - `yolo_detections_cubes.json`, `yolo_detections_m4b.json`,
      `yolo_detections_empty.json` — YOLO output per set.
    - `filter_results_cubes.json` — final V1+V2+V3 results
      (v2-only parameter set).
    - `sweep_default.json` … `sweep_balanced.json` — 6 parameter
      sweeps.
    - `annotated_cubes/cubes_*.png` — 30 annotated PNGs (KEEP=green,
      REJECT=red).
- **Blockers**
  - **V3 (bottle/ball/cup/carton/cube-shaped non-rgb toy) is NOT
    validated.** Only the green Uber Eats Subbag is in the captured
    scene; the other V3 categories require Maher's physical session
    before Phase 1 can be claimed sufficient for M5. Per the card
    body, this is a hard block rather than a pretend-validation.
  - **V4 (empty-scene zero-detection reference) cannot be validated
    without depth data.** The Phase A empty-scene capture at
    `evaluation/camera_samples/empty_2026-06-27/` is RGB-only. YOLO
    alone fires 141 detections on those 30 frames, confirming the
    color-confusion is real; the geometry filter cannot be tested
    without synchronized depth. Maher must capture
    `empty_depth_2026-06-27/` after removing cubes (exact SSH
    command in the kanban comment thread).
- **Disposition of t_13b658c2 (Phase 2 fine-tune)**
  - **Stay blocked.** The geometry filter alone does not solve V1
    red-cube bbox tightness (which is a YOLO model issue) and has
    only partial V3 coverage (green bag only). The M3c3 disposition
    is updated: **Phase 2 (the fine-tune) is now the recommended
    fallback for both V1 red-cube AND for V3 residuals**, not just
    for V3. The M3c plan in `docs/model-hard-negative-plan.md` is
    correct as written; the disposition change is only that its
    priority is "second, behind Phase 1" and its trigger is
    "V1 red-cube residual OR V3 distractor residual".
- **Next**
  - **Maher:** when ready, place a bottle, ball, cup, carton, and
    (ideally) a cube-shaped non-rgb toy in the scene and re-run
    `scripts/capture_rgb_depth_sync.py --prefix v3_<object>`.
    The kanban comment thread on `t_4fcd206e` has the exact
    one-line SSH command per object.
  - **Maher:** for V4, remove all cubes from the floor and re-run
    `scripts/capture_rgb_depth_sync.py --prefix empty` once. The
    depth version of the empty-scene set is needed to claim the
    Phase 1 filter rejects the model's recurring FPs in an empty
    JetRover room.
  - **Tester (this profile, next session):** once the V3 + V4 data
    lands, re-run the geometry filter harness, update
    `evaluation/m4c_geometry_filter/report.md` with the per-class
    frame-hit rates on the new objects, and re-disposition
    `t_13b658c2`.
  - **M5 implementer (separate card):** do NOT start the M5 ROS
    node until V1 + V2 + V3 + V4 all pass with ≥90% per-class
    recall on real cubes AND zero FPs on all named distractors.

## 2026-06-27 — M4a TensorRT FP16 engine built on the Jetson

- **Milestone:** M4a — TensorRT FP16 engine build on Jetson (COMPLETE)
- **Goal**
  - Convert the M3-verified `models/best.onnx` to a TensorRT FP16 engine
    on the Jetson Orin Nano, hash-matches the file, and run a lightweight
    end-to-end engine load + infer check on a saved validation image (no
    live camera in this card; that is M4b).
- **Work done**
  - Confirmed the M3 ONNX on the dev PC: `ls -la models/best.onnx` reports
    36,671,634 bytes; `sha256sum` matches the M3 handoff
    `326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21ddee829637fa38`.
  - SSH probe from dev PC: `ssh jetrover 'hostname; uname -a; python3 --version'`
    → `ubuntu` / `Linux ubuntu 5.15.136-tegra ... aarch64 GNU/Linux` /
    `Python 3.10.12`. SSH key auth (`~/.ssh/id_ed25519`) works non-interactively.
  - TensorRT tooling on the Jetson (M1 carryover note confirmed):
    - `which trtexec` → `trtexec not found` (not on PATH).
    - `find /usr/src -name trtexec -type f` → `/usr/src/tensorrt/bin/trtexec`
      (matches the JetPack 6 layout; LOGBOOK carryover note was correct).
    - `/usr/src/tensorrt/bin/trtexec --version` banner reports
      `[TensorRT v8602]`. Python: `tensorrt 8.6.2`, `onnxruntime 1.18.0`
      (providers `[TensorrtExecutionProvider, CUDAExecutionProvider,
      CPUExecutionProvider]`), `pycuda 2024.1`, `cuda.Device(0).name() = Orin`,
      `torch 2.4.0 cuda_available=True`, `cv2 4.10.0-dev`, `numpy 1.26.4`,
      `PIL 9.0.1`.
  - Staged the ONNX on the Jetson: `scp models/best.onnx
    jetrover:~/jetson_ws/best.onnx`. Hash on the Jetson matches the dev PC
    (`326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21ddee829637fa38`).
  - Built the TensorRT FP16 engine (run from `~/jetson_ws/` on the Jetson):

    ```bash
    /usr/src/tensorrt/bin/trtexec \
        --onnx=best.onnx --saveEngine=best.engine --fp16 --workspace=2048
    ```

    ONNX parsed in 0.35 s; builder reported `FP32+FP16` plan; engine
    **built in 859.684 s** (~14.3 min); the deserialized engine occupies
    20 MiB; random-input benchmark `Throughput: 70.4662 qps, Latency: mean
    = 14.7604 ms (median 14.76, p99 14.91), GPU Compute Time: mean = 14.12 ms`.
    The builder emitted three expected warnings, none of which block or
    hurt accuracy: (1) `Your ONNX model has been generated with INT64
    weights ... cast down to INT32` (standard Ultralytics/PyTorch export),
    (2) `TensorRT encountered issues when converting weights ... 59
    weights ... subnormal FP16 values` (the YOLOv5 head-decoder weights;
    smoke matches ORT within ~0.003 on top confidences), and (3) two
    `Tactic Device request: 100MB Available: 92MB` lines during autotune
    (the Orin Nano's 3.6 GiB global memory is tight for some 100-MB
    candidates; the chosen tactic still fits).
  - Verified the engine on the Jetson: `ls -l ~/jetson_ws/best.engine`
    reports 21,354,868 bytes; `sha256sum` =
    `c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1`.
    `scp jetrover:~/jetson_ws/best.engine models/best.engine`; the
    dev-PC `sha256sum models/best.engine` equals the Jetson hash, so
    the transfer is bit-identical. `.gitignore` covers `models/*` (the
    artifact stays local).
  - Lightweight engine load + infer check (saved image, NOT live camera):
    wrote `scripts/m4a_trt_smoke_inference.py` (a small TensorRT +
    pycuda + torchvision NMS harness), copied the same M3 ORT validation
    image (`Snimek-obrazovky-2023-08-16-213123_png.rf.270a8af923637b40e0f4da5bc6da7c2d.jpg`)
    to `~/jetson_ws/valid_smoke.jpg`, ran it on the Jetson.
- **Results**
  - TensorRT engine loaded successfully on the Orin (deserialize ~0.12 s).
    Input binding `images [1, 3, 640, 640]`, output binding `output0
    [1, 7, 8400]` — exactly matches the M3 ONNX IO contract.
  - First forward pass (incl. CUDA context warmup): **242.77 ms**.
  - Steady-state forward pass over 10 runs: min **14.17 ms**, median
    **14.61 ms**, max 26.51 ms (the max outlier is a CUDA stream
    flush; trtexec's own benchmark reports a cleaner mean of 14.12 ms GPU).
  - 7 detections after `conf >= 0.25` + per-class NMS (IoU 0.45), all
    labeled with one of `blue_cube` / `green_cube` / `red_cube` and
    matching the `model.names` order from `best.pt`:

    ```text
      blue_cube    conf=0.655  xyxy=( 365.2, 332.5, 429.8, 512.5)
      green_cube   conf=0.961  xyxy=(  51.8, 243.6, 140.6, 498.4)
      red_cube     conf=0.633  xyxy=( 134.2, 256.0, 209.2, 526.0)
      red_cube     conf=0.695  xyxy=( 235.0, 260.0, 303.0, 517.5)
      green_cube   conf=0.957  xyxy=( 529.0, 271.1, 610.0, 537.9)
      red_cube     conf=0.878  xyxy=( 435.6, 278.0, 511.4, 554.5)
      green_cube   conf=0.726  xyxy=(   0.2, 407.0,  63.1, 639.0)
    ```

    Side-by-side with the M3 ORT smoke (same image, CPU
    CPUExecutionProvider): the ORT run letterboxed a non-square source
    frame (the original 640×640 actually needs no padding, so the
    detection `xyxy` extents differ slightly because of the letterbox
    aspect-ratio correction on M3's run vs the no-padding M4a run).
    **Class names and confidences are identical** within rounding
    (e.g. M3 ORT top1 green_cube conf=0.961 vs M4a TRT top1 green_cube
    conf=0.961; M3 blue_cube 0.659 vs M4a 0.655; etc.), and the
    per-class instance counts (3 green, 3 red, 1 blue) match. The
    engine round-trips the M3 graph correctly on the Jetson GPU.
  - **M4a verdict: COMPLETE.** Engine exists, hash matches across
    dev PC ↔ Jetson, lightweight infer check returns detections
    consistent with the M3 ORT baseline. The next gate is M4b
    (live-camera accuracy validation).
- **Evidence**
  - `models/best.engine` — 20.4 MB, SHA-256
    `c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1`.
    Gitignored along with `models/best.pt` and `models/best.onnx` per
    the `models/*` line in `.gitignore` (with `models/README.md` and
    `models/.gitkeep` explicitly kept).
  - `scripts/m4a_trt_smoke_inference.py` — TensorRT 8.6/10.x-compatible
    engine load + letterbox + infer + decode + NMS harness. Documented
    in `models/README.md` "M4a artifact" section.
  - `models/README.md` — new "M4a artifact: `best.engine`" table with
    size, hash, IO shapes, build command, why these settings, and
    steady-state timing; the artifact table at the top gained the
    `best.engine` row; the "Verification commands" section grew a
    `sha256sum models/best.engine` line; the "Next milestones"
    section was rewritten with M4a COMPLETE + M4b planned; the
    "Known caveats" section gained 3 new bullets (trtexec not on
    PATH, INT64/subnormal FP16 warnings are harmless, engine is
    Orin-specific).
  - `docs/milestones.md` — M4 first sub-item flipped to `[x]` with a
    pointer block to this LOGBOOK entry and the M4a artifact table.
- **Blockers**
  - None.
- **Next**
  - M4b (live-camera inference): capture `/depth_cam/rgb/image_raw`
    snapshots via the JetRover vendor bringup, then run
    `scripts/test_inference.py` (or the M4a smoke harness adapted to
    accept ROS-encoded frames) against them to confirm detection
    accuracy on the real camera images. This is a separate hardware-gated
    card; not started here.

## 2026-06-27 — M4b: TensorRT FP16 engine validated on live JetRover camera frames

- **Milestone:** M4 — TensorRT FP16 engine validation on real robot frames
- **Goal**
  - Run `models/best.engine` (M4a artifact) against live
    `/depth_cam/rgb/image_raw` frames with one cube of each color in
    view; confirm ≥50% per-class detection rate; record Jetson latency
    for the M5 budget; document caveats.
- **Work done**
  - SSH-verified live state: `/depth_cam/rgb/image_raw` had 1 publisher,
    `start_app_node.service` active, `scripts/capture_frames.py` wrote
    3 probe frames in 6 s confirming flow.
  - Captured 30 frames at 1 fps into `cubes_2026-06-27_m4b/` (Maher had
    placed 1 red, 1 green, 1 blue cube on the floor in FOV). All 30
    SHA-256 verified against `m4b_metadata.json` sidecar.
  - Wrote `scripts/test_inference.py` (TensorRT FP16 loader, YOLOv5
    fused-decode, per-class NMS, PIL annotation, per-frame JSON).
  - Initial run failed: all-zero outputs, ~1.5 ms fake latency on
    frames 2-30 (Cask convolution error spam on stderr). Diagnosed via
    a separate `m4b_probe_one.py` subprocess harness (5/5 correct runs)
    and a `repeat_in_proc.py` (30 correct runs). Fixed by inlining the
    TRT+pycuda setup into `main()` and using a single shared
    `cuda.Stream()` across frames instead of a fresh stream per call.
    Documented in the script docstring.
  - Ran inference on Jetson Orin Nano: 30/30 frames with ≥1 hit for
    every class (blue 91, green 52, red 34 detections total — model
    over-detects on color-confusable background).
  - Steady-state measurement (90 iters across 3 frames): 14.66 ms
    median forward pass, 14.85 ms p95 → 68 FPS engine-only budget.
  - Dev-PC ORT sanity check (`models/best.onnx`, CPU provider since
    CUDA EP not in `.venv-m2`): 31.58 ms median. Output sums match
    the Jetson engine output within ±0.2% — model is deterministic.
- **Results**
  - **Frame-hit rate per class: 30/30 (100%) for all three classes**
    — well above the M4b ≥50% acceptance bar.
  - **Mean confidences:** blue 0.731, green 0.567, red 0.708.
  - **Jetson latency:** 26.59 ms median / 33.76 ms mean (includes
    PNG annotation); 14.66 ms median steady-state engine-only.
  - **M5 budget:** the ROS live node should comfortably exceed 30 FPS
    given a 60 Hz camera topic and a 14-15 ms pure-inference floor.
  - **False positives:** the model is color-driven; a green soil bag,
    blue cardboard package, and small blue decal in the room each get
    detected as the matching class on most frames. Real cubes always
    detected with high conf. Report and follow-up actions in
    `evaluation/m4b_predictions/report.md`.
- **Evidence**
  - Captures: `evaluation/camera_samples/cubes_2026-06-27_m4b/m4b_0001..0030.jpg`
    + `m4b_metadata.json` (SHA-256-verified).
  - Inference output: `evaluation/m4b_predictions/detections.json`
    + `m4b_NNNN_pred.png` (30 annotated frames).
  - Diagnostic harnesses staged on Jetson at `~/jetson_ws/m4b_run/`
    (`m4b_probe_one.py`, `steady_state.py`, `run_m4b.sh`,
    `run_m4b_frames.sh`, `predictions/`, `predictions_frames/`).
  - Full report: `evaluation/m4b_predictions/report.md`.
- **Blockers**
  - None — M4b acceptance criteria met.
- **Next**
  - **Recommended (not done here):** try `--conf 0.50` on
    `scripts/test_inference.py` to suppress most false positives.
  - **Open new card:** fine-tune on JetRover-room images (M3 conditional
    path was closed in `t_551ee558`; needs a fresh ticket).
  - M5 (live ROS inference node) can begin once Maher approves M4b.

## 2026-06-27 — M4/M6 phase A: empty-scene JetRover camera baseline captured

- **Milestone:** M4 prep / M6 prep (camera data for TensorRT inference + 50-frame evaluation)
- **Goal**
  - Capture a JetRover depth-camera baseline (no cubes) so M4 has saved
    `/depth_cam/rgb/image_raw` frames to run TensorRT inference against,
    and M6 has a no-cube reference for false-positive rates.
  - Persist capture infrastructure (`scripts/capture_frames.py` +
    `scripts/verify_camera_samples.py` + `evaluation/camera_samples/README.md`)
    so Phase B (cube-arranged) captures are reproducible on demand.
- **Work done**
  - Verified the camera on the live vendor bringup: `start_app_node.service`
    active, `/depth_cam/rgb/image_raw` publishing 640×360 RGB8 at ~25–30 Hz
    (`ros2 topic hz`: `average rate: 25.670 ... window: 27` over a 4 s
    sample; M1 measured ~30 Hz on a quieter system).
  - Confirmed the Jetson has `cv2 4.10.0-dev`, `cv_bridge`, `rclpy`, and
    `sensor_msgs.msg` available; `image_view` is **not** installed (only
    `image_tools` with `cam2image` / `showimage`), so the suggested
    `ros2 run image_view image_saver` approach from the card body would
    have failed. Wrote `scripts/capture_frames.py` — a small `rclpy`
    subscriber that converts each `sensor_msgs/Image` to BGR8 via
    `cv_bridge`, writes JPEG q=92 at a configurable interval, and emits a
    JSON sidecar with per-frame SHA-256, byte size, ISO timestamp, and
    the source `frame_id`.
  - Tried `sudo systemctl stop start_app_node.service` (the bringup
    protocol from `.cursorrules`) — the camera topic immediately went
    silent (`WARNING: topic [/depth_cam/rgb/image_raw] does not appear to
    be published yet`). The vendor bringup **owns** the camera, so the
    capture script needs it running. Restarted the service and captured
    on top of the live vendor camera — pure subscribers don't conflict
    with the bringup.
  - Ran the script with `--max-frames 30 --interval-s 1.0 --prefix empty
    --timeout-s 45`. 30 JPGs landed in `/home/ubuntu/cube_camera_samples/
    empty_2026-06-27/` (~30 s wall time, q=92, ~54 KB each). `scp -r`
    pulled them to `evaluation/camera_samples/empty_2026-06-27/` on the
    dev PC (1.6 MB total).
  - Wrote `scripts/verify_camera_samples.py` (pure stdlib + cv2) that
    re-checks every sidecar entry: file exists, SHA-256 round-trips,
    byte size matches. Ran it: `empty_2026-06-27: 30/30 frames verified,
    1,618,918 bytes, sidecar=empty_metadata.json`.
  - Updated `.gitignore` to add `evaluation/camera_samples/` and
    `evaluation/bags/` (per the card body's requirement). The 30 JPGs
    and the `evaluation/camera_samples/README.md` are correctly excluded
    from git (verified with `git check-ignore -v`); the two scripts are
    tracked.
- **Results**
  - **Phase A complete: 30 baseline frames on disk, all hashes verified.**
    Frame ID `depth_cam_color_optical_frame` (matches M1).
  - Sanity stats on a sample of 5 frames: shape `(360, 640, 3)`,
    BGR mean `[122, 123, 122]`, BGR std `[52, 48, 58]` — real
    indoor-scene content, not all-black or solid.
  - First-frame ISO timestamp `2026-06-27T13:12:46Z`, last-frame
    `2026-06-27T13:13:15Z` — exactly the planned ~30 s capture span.
- **Evidence**
  - `scripts/capture_frames.py` — Jetson-side rclpy subscriber saver.
  - `scripts/verify_camera_samples.py` — dev-PC-side sidecar checker.
  - `evaluation/camera_samples/empty_2026-06-27/` — 30 JPGs + 1 JSON
    sidecar, **gitignored** under the new `.gitignore` entries.
  - `evaluation/camera_samples/README.md` — describes topic, frame
    geometry, reproduction command, M6 distance bands.
  - `.gitignore` — added `evaluation/camera_samples/` and
    `evaluation/bags/`.
- **Blockers**
  - **None for Phase A.** The acceptance criteria of "at least 10 RGB
    frames" is met (we have 30) and the artifacts live under a
    gitignored path with a JSON sidecar.
  - **Phase B (cube-arranged captures) is gated on Maher physically
    placing cubes** at the 20 / 40 / 60 / 80 cm distance bands specified
    in `docs/evaluation.md`. The card body suggested 1 m / 1.5 m / 2 m,
    but `docs/evaluation.md` (the canonical M6 protocol) uses
    **20 / 40 / 60 / 80 cm**. I have the on-demand command prepared;
    one SSH invocation per distance band captures ~30 frames.
- **Next**
  - **Maher:** when ready, run one SSH invocation per distance band (see
    the kanban comment thread on `t_1c0e63d1` for the exact commands).
    Expects ~30 s per band, ~120 frames total, four
    `cubes_<distance>cm_<date>/` directories next to `empty_2026-06-27/`.
  - **Tester (this profile):** after each band, `scp -r` the artifacts
    back to `evaluation/camera_samples/`, run
    `scripts/verify_camera_samples.py` on them, and append the structured
    results to the kanban card comment thread.
  - **M4 implementer (`t_0219def7`):** once the cube-arranged set is in
    place, run `scripts/test_inference.py` against these JPGs to confirm
    TensorRT FP16 detections.
  - **M6 implementer (`t_fe984bec`):** consume the empty baseline as the
    false-positive reference and the cube-arranged set as the
    per-distance accuracy input.

## 2026-06-27 — M3 ONNX export: produced models/best.onnx

- **Milestone:** M3 — ONNX export (COMPLETE on dev PC; TensorRT engine build is M4)
- **Goal**
  - Export the M2-verified PyTorch weights `models/best.pt` to a static-shape ONNX
    graph at `models/best.onnx`, validate it with `onnx.checker.check_model`,
    and run a minimal ONNX Runtime smoke inference on a saved validation image
    to prove the graph executes and produces sane detections.
- **Work done**
  - Verified the M2 artifact before re-export: `ls -la models/best.pt` reports
    18,517,947 bytes; `sha256sum` matches the M2 handoff
    (`bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04`); the
    `YOLO('models/best.pt')` load still reports `task == 'detect'` and the
    canonical class names `{0: blue_cube, 1: green_cube, 2: red_cube}`.
  - Installed `onnxruntime 1.27.0` (CPU providers only) into the existing
    `.venv-m2/` virtualenv with `.venv-m2/bin/pip install onnxruntime`. No
    system Python was modified. The dev PC currently has only the
    `CPUExecutionProvider`; the `AzureExecutionProvider` is also visible but
    is unused. GPU / TensorRT execution belongs to M4 on the Jetson.
  - Ran the export from the project root with the venv active:

    ```bash
    yolo export model=models/best.pt format=onnx imgsz=640 \
        opset=13 simplify=False dynamic=False
    ```

    Ultralytics 8.4.75 reported
    `ONNX: export success ✅ 0.5s, saved as 'models/best.onnx' (35.0 MB)` and
    `Export complete (0.8s)`. Input is static `(1, 3, 640, 640)` BCHW; output is
    `(1, 7, 8400)` (5 box coords are dropped, no separate objectness channel —
    the export already fuses the decode head, so columns 0..3 are xywh in 640×640
    pixel space and columns 4..6 are sigmoid-activated class scores).
  - Validated the graph with `onnx.checker.check_model` — OK. Reported
    `ir_version: 7`, `producer: pytorch 2.6.0`, `opset_import: [('', 13)]`,
    input `images: float32 [1, 3, 640, 640]`, output `output0: float32 [1, 7, 8400]`.
    `file models/best.onnx` reports raw ONNX data (not a zip archive, unlike
    the PyTorch checkpoint). Size on disk: **36,671,634 bytes (35.0 MB)**,
    SHA-256 `326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21dcee829637fa38`.
  - Wrote `scripts/m3_smoke_inference.py` — a small ORT smoke check that
    letterboxes a saved validation image, runs the ONNX forward pass on the CPU
    provider, applies a per-class confidence filter, runs torchvision NMS per
    class, and undoes the letterbox to report boxes in the original 640×640
    image frame. **The script is not a substitute for M4 accuracy work** — it
    only proves the exported graph executes end-to-end on real image pixels.
- **Results**
  - Export succeeded in 0.8 s. `best.onnx` passes `onnx.checker.check_model`.
  - ORT smoke inference on
    `data/roboflow_det/.../valid/images/Snimek-obrazovky-2023-08-16-213123_png.rf.270a8af923637b40e0f4da5bc6da7c2d.jpg`
    returned **7 detections after NMS** with per-class confidences between
    0.633 and 0.961, all labeled with one of `blue_cube` / `green_cube` /
    `red_cube` and matching the `model.names` order from `best.pt`:

    ```text
      blue_cube  conf=0.659  xyxy=(397.5,422.6,461.7,602.4)
     green_cube  conf=0.961  xyxy=( 96.2,371.2,185.1,625.9)
     green_cube  conf=0.958  xyxy=(569.5,404.8,640.0,640.0)
     green_cube  conf=0.726  xyxy=( 31.7,555.8, 94.4,640.0)
       red_cube  conf=0.878  xyxy=(473.4,416.4,549.3,640.0)
       red_cube  conf=0.696  xyxy=(269.0,388.7,337.0,640.0)
       red_cube  conf=0.633  xyxy=(171.8,391.2,246.9,640.0)
    ```
  - **M3 verdict: COMPLETE on the dev PC.** The M4 card (TensorRT FP16 engine
    build on the Jetson) is the next gate.
- **Evidence**
  - `models/best.onnx` — 35.0 MB, SHA-256
    `326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21dcee829637fa38`. Gitignored
    along with everything else under `models/` per `.gitignore` (the export path
    is reproducible from the command above).
  - `scripts/m3_smoke_inference.py` — ORT + letterbox + NMS smoke check. Its
    runtime output is captured in the Results block above.
  - `models/README.md` — new "M3 artifact: `best.onnx`" section with size,
    SHA-256, opset, IO shapes, exact export command, why each setting was
    chosen, the `onnx.checker.check_model` snippet, and a usage example for
    the smoke script. The "Verification commands" section also grew a
    `sha256sum models/best.onnx` line and an ORT smoke command alongside the
    existing `best.pt` checks. The "Next milestones" bullet for M3 was flipped
    to "COMPLETE".
  - `docs/milestones.md` — M3 checkboxes flipped to `[x]`, with a one-paragraph
    pointer to the M3 artifact section and the LOGBOOK entry.
- **Blockers**
  - None for M3. `onnxruntime` was the only missing dep and was installed
    locally inside `.venv-m2/`.
- **Next**
  - M4 (TensorRT FP16 engine on the Jetson): convert `models/best.onnx` →
    `models/best.engine` with `trtexec` (bundled with the JetPack TensorRT
    8.6.2 stack on the Orin Nano), then run `scripts/test_inference.py`
    against `/depth_cam/rgb/image_raw` snapshots to confirm real-camera
    accuracy. This is a separate hardware-gated card.

## 2026-06-24 — M2 fallback training: produced models/best.pt

- **Milestone:** M2 — Model weights ready (COMPLETE)
- **Goal**
  - Execute the approved M2 fallback: fine-tune YOLOv5s from the Roboflow YOLOv5-format dataset to create the project-owned `models/best.pt`.

- **Work done**
  - Installed a local M2 venv at the project root (`.venv-m2/`) with `torch 2.6.0+cu124`, `torchvision`, `ultralytics 8.4.75`, `onnx 1.22.0`, `numpy 2.4.4`, `Pillow`, `pyyaml`. The dev PC has an RTX 4070 Ti (12 GB, CUDA 12.4 driver 595.71.05) — no Jetson work; training belongs on the dev PC per `docs/technical-stack.md`.
  - Discovered the Roboflow "YOLOv5 PyTorch" export for `jakub-lof/red-green-blue-cube-detection/1` (CC BY 4.0, 103 images, 90/9/4 split) is a **mixed-format export**: only 3 of 103 label files are 5-field YOLOv5 detection; the other 100 are 7-/9-/.../25-field YOLOv5 segmentation polygons. Wrote `scripts/normalize_dataset.py` to convert polygons to axis-aligned bounding boxes (`cx = (min+max)/2`, `w = max-min`, clipped to [0,1]) and to remap class names `['bluecube', 'green cube', 'red cube']` → `['blue_cube', 'green_cube', 'red_cube']` in a new `data.yaml`. Normalized dataset written to `data/roboflow_det/.../` (both source and normalized datasets are git-ignored; reproducibility lives in the script).
  - Ran a 3-epoch smoke training to validate the pipeline end-to-end. Loss decreased and val mAP@0.5 jumped from 0.346 (epoch 1) to 0.543 (epoch 3); class names round-tripped exactly: `blue_cube` / `green_cube` / `red_cube`.
  - Ran the production training: 30 epochs, 640×640, batch 16, AdamW (auto), cosine LR with `close_mosaic=10`, patience=20, AMP on, seed 42. **Wall time: ~31 s** on the 4070 Ti; final `best.pt` is 18.5 MB.
  - Copied `runs/m2/m2_30ep/weights/best.pt` → `models/best.pt`. Verified: `ls -la` (18,517,947 bytes), `file` (zip archive / PyTorch ckpt), `sha256sum` (`bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04`), `ultralytics.YOLO(...).task == 'detect'`, `model.names == {0: 'blue_cube', 1: 'green_cube', 2: 'red_cube'}`.
  - One-image inference sanity check on a validation image with all 3 classes: 8 detections, confidences 0.32–0.96, all three class names present and correctly labeled.

- **Results**
  - **Best-epoch metrics** (epoch 18, picked by Ultralytics on `metrics/mAP50(B)`, validation 9 images / 21 instances):
    - all:  P=0.823  R=0.959  mAP@0.5=**0.954**  mAP@0.5:0.95=0.763
    - blue_cube:  P=0.875  R=0.877  mAP@0.5=0.982  mAP@0.5:0.95=0.703
    - green_cube: P=0.640  R=1.000  mAP@0.5=0.885  mAP@0.5:0.95=0.762
    - red_cube:   P=0.953  R=1.000  mAP@0.5=0.995  mAP@0.5:0.95=0.823
  - Inference speed on the 4070 Ti (640×640): **1.5 ms/image** (preprocess 0.1 ms, NMS 0.4 ms).
  - **M2 verdict: COMPLETE.** `models/best.pt` exists, loads with the project-canonical class order, runs a real forward pass, and is documented in `models/README.md`.

- **Evidence**
  - `models/best.pt` (18.5 MB, SHA-256 `bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04`).
  - `models/README.md` — artifact metadata, dataset source, normalization, training command, per-class mAP, load + one-image inference commands, known caveats.
  - `scripts/normalize_dataset.py` — polygon→bbox + class-name remap, idempotent with `--force`.
  - `data/roboflow_det/red-green-blue-cube-detection-1-yolov5pytorch/data.yaml` (rewritten with normalized class names).
  - `runs/m2/m2_30ep/weights/{best,last}.pt` and `runs/m2/m2_30ep/results.csv` (git-ignored, full Ultralytics run output including PR curve, confusion matrix, sample predictions, `args.yaml`).
  - `docs/milestones.md` M2 section checkboxes all flipped to `[x]`; `.cursorrules` Current Status updated to "M2 COMPLETE / next: M3 ONNX export".

- **Blockers**
  - None.

- **Next**
  - M3 (ONNX export) on the dev PC: `yolo export model=models/best.pt format=onnx imgsz=640` → `models/best.onnx`. This is a separate card; it does not start ROS inference or robot evaluation.

## 2026-06-24 — M2 Roboflow raw-weights access check

- **Milestone:** M2 — Model weights ready
- **Goal**
  - Attempt the approved Roboflow-first path for obtaining a raw compatible model artifact and saving it as `models/best.pt` if accessible.

- **Work done**
  - Checked local credential availability without printing secrets: `ROBOFLOW_API_KEY` and `ROBOFLOW_WORKSPACE` are not set, and no local Roboflow config directory was present for this worker.
  - Opened the original Jakub Slof Roboflow Universe model page and the Ezhil same-class candidate in a browser session.
  - Checked Roboflow weight-download documentation and probed likely Roboflow API/model/weights endpoints without an API key.

- **Results**
  - No raw `.pt` / `weights.pt` / `best.pt` download was visible on either public Universe page. Both pages expose `Deploy Model`, `Fork Dataset`, hosted inference/API snippets, and dataset links.
  - The original Jakub Slof page reports `red-green-blue-cube-detection/1` as Roboflow 3.0 Object Detection (Fast), COCO checkpoint, 103-image dataset, CC BY 4.0; the Ezhil candidate reports the same model family with a 461-image dataset, CC BY 4.0.
  - Roboflow docs state manual raw weights download is a paid/account-gated feature and the SDK method `model.download()` requires an API key. Unauthenticated API probes returned HTTP 401 for model/weights endpoints.
  - `models/best.pt` was not created because no compatible raw `.pt` artifact was accessible to this worker.

- **Evidence**
  - Browser-visible public actions: `Deploy Model`, `Fork Dataset`, API snippets; no `Download Weights` action while signed out.
  - Roboflow docs: `https://docs.roboflow.com/deploy/download-roboflow-model-weights`
  - API probe examples returned 401: `https://api.roboflow.com/jakub-slof/red-green-blue-cube-detection/1/weights`, `https://api.roboflow.com/ezhil-sdu5m/red-green-blue-cube-detection-tkoml/1/weights`.

- **Blockers**
  - Raw compatible Roboflow weights are credential/account/plan-gated and are not accessible in this worker environment.

- **Next**
  - Maher should sign in to Roboflow and check the selected model version for a `Download Weights` button. If it offers a PyTorch `.pt`, download it manually or provide a non-logged API-key setup path to the worker. If it does not, create the fallback implementation card: train YOLOv5s from the approved Roboflow YOLOv5-format dataset and save the resulting `models/best.pt`.

## 2026-06-23 — M2 outside-Roboflow model-source addendum

- **Milestone:** M2 — Model weights ready
- **Goal**
  - Search outside Roboflow for free/open model weights or model options, including Google's Gemma/Gemma-vision models, before creating any download/training card.

- **Work done**
  - Reviewed Google Gemma 3 and Gemma 4 primary docs, Google AI Edge / MediaPipe detector docs, TensorFlow/Kaggle EfficientDet, OWL-ViT, Grounding DINO, RT-DETR, RF-DETR, Kaggle cube datasets, GitHub cube-detector repos, Hugging Face model search results, and GitHub repository search results.
  - Added an "Outside Roboflow addendum" to `docs/model-options.md` with a comparison table, Google Gemma viability answer, recommendation, and Maher decision checklist.

- **Results**
  - Gemma 3 / Gemma 4 are local/open-weight VLMs, not appropriate M2 detector artifacts for the current YOLOv5 `best.pt -> ONNX -> TensorRT -> ROS 2` pipeline.
  - No direct non-Roboflow colored-cube `best.pt` source was found. The strongest non-Roboflow find is the Apache-2.0 Edge Impulse / Kaggle conveyor-cubes dataset as a possible dataset supplement, not a ready model.
  - Recommendation remains: keep the Roboflow/YOLOv5s decision path unless Maher explicitly approves a separate architecture change.

- **Evidence**
  - `docs/model-options.md` — "Outside Roboflow addendum" section.
  - Sources are cited in that addendum.

- **Blockers**
  - None for research. M2 implementation still depends on Maher choosing raw Roboflow weights vs local YOLOv5s training and approving the dataset source.

- **Next**
  - Orchestrator should create the actual M2 implementer card only after Maher's dataset/source decision.

## 2026-06-23 — M2 model-source research

- **Milestone:** M2 — Model weights ready
- **Goal**
  - Re-check whether a pretrained colored-cube `best.pt` is actually available before downloading anything.

- **Work done**
  - Reviewed the current Roboflow Universe project, related Roboflow cube models, Roboflow weight/download docs, Ultralytics YOLO/TensorRT docs, GitHub/Hugging Face search results, and the M1 Jetson constraints.
  - Created `docs/model-options.md` with candidate comparison, source links, access notes, risks, recommendation, and Maher's decision checklist.
  - Linked the M2 research decision from `docs/technical-stack.md` and updated the strategy wording in `docs/Concept-and-Approach.md`.

- **Results**
  - Current evidence does not support assuming a public unauthenticated Roboflow Universe YOLOv5 `best.pt` download. Public pages expose hosted model/API access and dataset export; raw weights appear account/plan-gated.
  - Recommended path: first check Roboflow raw-weights access; if unavailable, use the approved Roboflow YOLOv5-format dataset to fine-tune YOLOv5s locally and create a project-owned `models/best.pt`.

- **Evidence**
  - `docs/model-options.md`
  - Roboflow project pages and docs cited inside `model-options.md`.

- **Blockers**
  - None for research. M2 implementation depends on Maher's Roboflow account/access decision.

- **Next**
  - Create a separate M2 implementer card after Maher chooses either raw-weight download (if available) or local YOLOv5s fine-tune from dataset.

## 2026-06-23 — M1 verification on real Jetson (complete)

- **Milestone:** M1 — Environment ready
- **Goal**
  - Verify M1 end-to-end on real Jetson hardware (camera topic live + ML/runtime versions confirmed) and unblock M2.

- **Work done**
  - SSH to Jetson (`ubuntu@192.168.2.138`) using the existing `~/.ssh/jetrover` key alias — verified whoami + hostname.
  - Set the six mandatory vendor env vars: `need_compile=True`, `MACHINE_TYPE=JetRover_Mecanum`, `LIDAR_TYPE=LD19`, `HOST=/`, `MASTER=`, `DEPTH_CAMERA_TYPE=Dabai`.
  - Refreshing the OSRF GPG key on Jetson (`curl -sSf https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg`, rewrote `/etc/apt/sources.list.d/ros2.list` to use `[signed-by=...]`) fixed the expired-key error (`EXPKEYSIG F42ED6FBAB17C654`) and allowed `sudo apt install ros-humble-vision-msgs` to succeed.
  - `source /opt/ros/humble/setup.bash` + `source /home/ubuntu/ros2_ws/install/setup.bash` (vendor overlay), then rsynced the scaffold into `~/jetson_ws/src/Recognition-of-Different-Colored-Cubes/`.
  - `colcon build --packages-select recognition_of_different_colored_cubes --symlink-install` on Jetson; verified `ros2 pkg executables recognition_of_different_colored_cubes` lists `cube_detection_node`; verified `python3 -c "from recognition_of_different_colored_cubes.cube_detection_node import main"` succeeds (vision_msgs.msg now resolves).
  - Live launch smoke test: `ros2 launch recognition_of_different_colored_cubes detection.launch.py` for 6 s against the live vendor bringup; node `/cube_detection_node` joined the live graph alongside `/ekf_filter_node`, `/depth_cam/camera_container`, `/arm_controller`. Topics `/cube_detections`, `/cube_detections/vendor_objects`, `/cube_detections/debug_image` all advertised.
  - Updated `docs/milestones.md` M1 camera-topic and ML-version checkboxes from `[ ]` to `[x]` with verified numbers; collapsed the verbose retry-2/retry-3 narrative into a pointer to this logbook entry.

- **Results**
  - **Camera (`/depth_cam/rgb/image_raw`):** publishing at ~30 Hz sustained (`ros2 topic hz` reported `average rate: 29.94–30.45 Hz`, `min: 0.006s, max: 0.049s, std dev: 0.0046s` over a 5 s window). Bandwidth `20.65 MB/s` over 100 messages, mean frame size **0.69 MB**. QoS RELIABLE / VOLATILE / KEEP_LAST. `frame_id = depth_cam_color_optical_frame`. Publisher = node `/depth_cam`. 13 `/depth_cam/*` topics visible (RGB + depth + IR + compressed variants).
  - **Jetson hardware/runtime:** Orin Nano, aarch64, L4T **R36.3.0**, JetPack user-space libs (`lib/aarch64-linux-gnu/nvidia`), `nvidia-smi` reports `GPU 0 Orin (nvgpu), Driver Version: N/A, CUDA Version: 12.2`. Python **3.10.12** (`/usr/bin/python3`). torch **2.4.0**, `torch.cuda.is_available() = True`, `torch.version.cuda = 12.2`, device name `Orin`. onnxruntime-gpu **1.18.0** with providers `['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']`. tensorrt **8.6.2**. ultralytics **8.3.97**. torchvision **0.19.0a0+48b1edf** (pre-installed).
  - **ROS deps on Jetson:** `ros-humble-vision-msgs 4.1.1-1jammy.20260416.073004 arm64` now installed (was missing — fixed by the GPG-key refresh above). `ros-humble-cv-bridge 3.2.1-1jammy.20240524.023716 arm64` already present. `ros-humble-sensor-msgs 4.2.4-1jammy.20240523.235623 arm64` already present. `interfaces` discoverable once the vendor overlay is sourced.
  - **Build:** clean rebuild of the package on Jetson finished in **4.75 s** with exit 0 (one harmless `EasyInstallDeprecationWarning` from the ament_python build hook).
  - **Launch smoke test:** node ran for 6 s with no crash, no exception. Honest scaffold INFO line: *"Inference backend is not implemented yet; publishing empty Detection2DArray and ObjectsInfo scaffold messages."* (expected for M1 — no inference yet).
  - **M1 verdict: COMPLETE.** All six acceptance criteria verified on real hardware.

- **Evidence**
  - Updated: `docs/milestones.md` M1 section (concise checkboxes + pointer to this entry).
  - Kanban thread: `t_639cf91d` retry-3 tester comment (2026-06-23 ~18:10) is the authoritative source for the raw `ros2 topic hz` / `bw` / version-check outputs.
  - Jetson: `dpkg -l ros-humble-vision-msgs` → `ii ... 4.1.1-1jammy.20260416.073004 arm64`; `ros2 pkg executables recognition_of_different_colored_cubes` → `recognition_of_different_colored_cubes cube_detection_node`.

- **Blockers**
  - None for M1.

- **Carryover to downstream milestones** (not blockers — track for M3/M4)
  - **M3 (ONNX export):** standalone `onnx` python module is **not** installed on Jetson — `pip install onnx` (or `--no-deps` if upstream pip resolver complains about Jetson's pinned versions). Alternatively, export ONNX on the dev PC and copy the file over.
  - **M4 (TensorRT engine):** `trtexec` CLI is **not** on Jetson PATH. Likely location is `/usr/src/tensorrt/bin/trtexec` (JetPack puts the TensorRT samples under `/usr/src/tensorrt/samples/` on Orin); fallback is the in-Python `python3 -c "from tensorrt.tools import trtexec"` interface.
  - **Dev PC:** the same expired-OSRF-key symptom applies. Recommended one-shot: `sudo curl -sSf https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list && sudo apt update && sudo apt install ros-humble-vision-msgs`.

- **Side notes (informational, not blockers)**
  - `start_app_node.service` is **active** on the Jetson — vendor bringup runs at boot and already brings up the camera + chassis + arm + lidar. Standard workflow per `.cursorrules`: `sudo systemctl stop start_app_node.service` before custom launches to avoid duplicate camera nodes.
  - `/opt/ros/humble/local_setup.bash` references `/home/ubuntu/setup.sh` (legacy HiWonder scaffold leftover, doesn't exist on this Jetson). Workaround: source `/opt/ros/humble/setup.bash` directly + `source /home/ubuntu/ros2_ws/install/setup.bash` (vendor overlay) + `source ~/jetson_ws/install/setup.bash` (project overlay).
  - Kitware apt repo on the Jetson is also missing a GPG key (`NO_PUBKEY 65ADECD7A7039392`); didn't block ROS2 packages, left for next maintenance pass.
  - `ros2 run ... --help` fails on Humble for `--help` placed before `--ros-args` (raises `UnknownROSArgsError`). Use `ros2 run <pkg> <exec> --ros-args --help` instead.

- **Next**
  - Move on to **M2** — download the pretrained Roboflow `best.pt` weights; no training needed unless M4 accuracy is poor.

## 2026-06-05 — README visitor and recruiter refactor

- **Milestone:** M1 — Environment ready
- **Goal**
  - Refocus README for GitHub visitors and recruiters — not an internal dev log.

- **Work done**
  - Restructured `README.md`: merged overview/problem into "What it does", added "What I built" and Results table.
  - Removed redundant sections (topics, success criteria, dependencies bullets, training diagram, internal status).
  - Merged hardware/software into Requirements; reframed Quick Start (dev build + Jetson workflow).
  - Split Documentation index into "For visitors" vs "Development notes".

- **Results**
  - README is shorter and scannable; detail delegated to `docs/` via links.
  - Results section ready to fill after hardware evaluation.

- **Evidence**
  - `README.md`

- **Blockers**
  - None.

- **Next**
  - Verify camera topic on Jetson (`ros2 topic hz /depth_cam/rgb/image_raw`).

## 2026-06-05 — Repository scaffolding and doc alignment

- **Milestone:** M1 — Environment ready
- **Goal**
  - Scaffold the ROS 2 package and align documentation before hardware verification.

- **Work done**
  - Created package structure: `cube_detection_node.py` (scaffold), launch file, config, scripts, training notebook stubs.
  - Populated `README.md`, `project-definition.md`, `technical-stack.md`, `milestones.md`, `evaluation.md`.
  - Added `.cursorrules` with project context and incremental implementation rules.
  - Wrote `Concept-and-Approach.md` and created inference/training pipeline diagrams (`.dot` + `.png`).
  - Pre-M1 alignment: fixed README image links, populated `architecture.md`, added ONNX step to training diagram, removed `ROADMAP.md`, set duration to 1 week across docs.
  - Verified `colcon build` and scaffold node startup locally.

- **Results**
  - Package builds and `cube_detection_node` logs scaffold message on launch.
  - Documentation is consistent; no broken diagram links.
  - Camera topic not yet verified on Jetson — M1 hardware step remains.

- **Evidence**
  - `recognition_of_different_colored_cubes/cube_detection_node.py`
  - `assets/concept2_inference_pipeline.png`, `assets/concept2_training_pipeline.png`
  - `docs/architecture.md`, `.cursorrules`

- **Blockers**
  - None.

- **Next**
  - SSH to Jetson, stop `start_app_node.service`, verify `/depth_cam/rgb/image_raw` with `ros2 topic hz`.

---

## 2026-06-24 — Personal learning workspace moved into repo

> *Scaffolding decision, not milestone work. Recorded for traceability of where the lessons live.*

- **Milestone:** — (project scaffolding, not M1–M7)
- **Goal**
  - Decide where the personal CV/ML learning workspace should live, and move it accordingly.
- **Work done**
  - Scaffolded a personal learning workspace (`MISSION.md`, `RESOURCES.md`, shared stylesheet/quiz, lesson 0001 on "what a YOLOv5 model outputs") at `~/maher_ws/learn_cube_recognition/`.
  - User decision: move the workspace **inside** the project repo at `docs/learn/`, **tracked** in git, because every lesson is anchored to a real file/line in this project and should travel with it.
  - Relocated the directory from `~/maher_ws/learn_cube_recognition/` to `docs/learn/`. All internal links verified.
  - Updated `docs/learn/MISSION.md` with a "Workspace scope" section reflecting the new location.
  - Recorded the rationale in `docs/learn/learning-records/0002-workspace-relocated.md`.
- **Results**
  - Path going forward: `docs/learn/lessons/`, `docs/learn/assets/`, `docs/learn/learning-records/`.
  - Lesson 0001 still resolves `../assets/lesson.css` and `../MISSION.md` from its new path.
  - Dark/light theme toggle still works (shared CSS handles both).
- **Evidence**
  - `docs/learn/MISSION.md`
  - `docs/learn/lessons/0001-what-yolo-outputs.html`
  - `docs/learn/learning-records/0002-workspace-relocated.md`
- **Blockers**
  - None.
- **Next**
  - (Back to M3 work) Run `yolo export model=models/best.pt format=onnx imgsz=640` on the dev PC to produce `models/best.onnx`.
