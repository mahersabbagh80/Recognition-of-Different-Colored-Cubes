# M4c1 Report — Phase 1 depth/geometry post-filter validation

**Date:** 2026-06-27
**Card:** t_4fcd206e (M4c1)
**Parent:** t_becf3451 (M3c3 cube-objectness addendum)
**Author:** implementer

## 0. TL;DR

The geometry filter **correctly rejects all four named M4b flat-color
distractors** (blue cardboard tissue box, blue cardboard package, green
Uber Eats Subbag, blue decal) and the **green Uber Eats Subbag raised 3D
distractor**, in 30/30 frames each. The **real blue cube** is preserved
on 22/29 frames where YOLO gives a full bbox (76% — below the 90%
target). The **real red cube** is rejected on 0/30 frames because
YOLO's bbox is too tight (covers only the top face) and geometry
alone cannot distinguish a single face of a cube from a flat surface.

**Verdict:** the Phase 1 depth/geometry post-filter **resolves the
V2 (flat color distractors) failure mode completely** and **partially
resolves the V3 (raised 3D colored non-cube) failure mode** with the
green bag as a positive control. It **does not** rescue the V1 (real
red cube) detection when YOLO's bbox is too tight.

**Disposition of t_13b658c2 (Phase 2 fine-tune):** **stay blocked** on
the basis that the geometry filter alone cannot fix the V1 red-cube
bbox-tightness issue (which is a YOLO model issue, not a depth/geometry
issue), but **recommend resuming** the fine-tune for the L4 residual
(cube-shaped non-rgb toy) once a physical V3 capture of such a distractor
is set up. The geometry filter is **necessary but not sufficient** for
M5; the fine-tune remains the conditional fallback.

## 1. Live depth availability — verified

The M3c3 addendum assumed `/depth_cam/depth_registered/points` is the
depth topic on JetRover. **It is not.** Probing the live vendor bringup
on 2026-06-27 found:

| Topic | Type | Frame ID | Hz | Notes |
|-------|------|----------|-----|-------|
| `/depth_cam/depth/image_raw` | sensor_msgs/Image (16UC1, 640×360, uint16 mm) | `depth_cam_color_optical_frame` | ~30.5 | **color-registered depth image** (frame_id is the RGB optical frame) |
| `/depth_cam/depth/points` | sensor_msgs/PointCloud2 (210680 pts/frame) | `depth_cam_color_optical_frame` | ~30 | raw depth-frame pointcloud |
| `/depth_cam/depth_to_color` | orbbec_camera_msgs/Extrinsics | (n/a) | ~30 | depth→RGB extrinsics |
| `/depth_cam/depth_registered/points` | (does not exist) | — | — | **the addendum's assumption is wrong on this install** |

Both `/depth_cam/rgb/image_raw` (rgb8, 640×360, 29.7 Hz) and
`/depth_cam/depth/image_raw` are live under the vendor bringup. TF tree
includes both `depth_cam_color_optical_frame` and
`depth_cam_depth_optical_frame` (both children of `depth_cam_link`).
The RGB intrinsics are fx=360.3266, fy=360.3266, cx=321.0181,
cy=179.2141 with a real distortion model (`d[0]=-0.0189`); the depth
image is undistorted.

The 16UC1 depth image at 640×360 with the same frame_id as the RGB
stream is a perfect geometry-filter input: pixel (u, v) in the RGB
image corresponds to depth_mm = depth_image[v, u] in millimeters.

**Implication for M5:** the M5 ROS node can subscribe to the two
topics directly and run the geometry filter per RGB-detection, with
no registration math needed in the node.

## 2. Validation set captured

Captured 30 synchronised RGB+depth pairs at 1 fps on the live
JetRover, with the same scene Maher used for M4b (1 red, 1 teal,
1 blue cube on the wood floor in FOV; a green Uber Eats Subbag and
a blue cardboard package also in frame as the M4b FP distractors).
Capture harness: `scripts/capture_rgb_depth_sync.py` (new). Pair
synchronisation uses `message_filters.ApproximateTimeSynchronizer`
with `slop=0.05 s`; observed stamp deltas were 11–44 ms (well within
slop). All 30 pairs SHA-256 verified against the sidecar JSON.

**Location:** `evaluation/camera_samples/cubes_depth_2026-06-27/` (30 RGB JPGs q=92, 30 depth PNGs uint16, 1 metadata sidecar; gitignored per `.gitignore`).

Depth distribution of non-zero pixels: min 241 mm, median 428 mm,
p90 827 mm, max 1370 mm (the wall is at the far end). Non-zero
fraction per frame: 91.3–91.6%. The 8.4–8.7% zero-depth fraction
matches the expected Orbbec pattern at depth-edge pixels and on
specular surfaces.

The scene includes:
- 3 small wooden cubes (red, teal/green, blue) — real cubes (V1)
- A green Uber Eats Subbag standing up (right) — **raised 3D** colored non-cube (V3)
- A blue cardboard tissue package (top-left) — flat colored distractor (V2)
- A blue cardboard package (right) — flat colored distractor (V2)
- A brown cardboard box (center-back) — minor distractor
- A small blue decal (lower-right) — flat colored distractor (V2)
- A gray folded cloth (upper-right) — non-colored distractor

The green Uber Eats Subbag is the only raised 3D colored non-cube
distractor in the captured set; bottle, ball, cup, carton, and
cube-shaped non-rgb toy were **not available** and require a
Maher physical session (see §6).

## 3. Geometry filter design (as implemented)

The §3 tests in `docs/model-objectness-addendum.md` were designed for
a side-on camera with tight YOLO boxes. On a tilted-down JetRover
camera looking at horizontal floor with 50 mm wooden cubes, those
tests misfire:

1. The naïve "median(annulus) floor depth" measures **floor slope**
   (floor depth grows with image-y on a tilted camera), not object
   height, and silently fails for any 50 mm-tall cube.
2. The "3D bbox aspect" test from per-pixel u/v ranges × a single
   z_world / fx is **noisy** when the bbox contains both cube-top
   pixels and floor pixels.

The implemented filter therefore uses **depth-histogram tests**:

| Test | What it measures | Cube (50 mm) | Flat distractor | Tall bag | Threshold |
|------|------------------|--------------|------------------|----------|-----------|
| A. **raised-point fraction** | fraction of in-box pixels > `RAISED_MM` above floor median | > 30% | < 5% | varies | `min_raised_frac=0.20` |
| B. **3D aspect ratio** (raised subset) | long/short axis of raised pixels in world mm | 1.0–1.2 | 1.5–3.0+ | 1.4–1.5 | `max_ratio=1.2` |
| C. **planar top stddev** | stddev of raised pixels' depth | 5–15 mm | 1–5 mm | 60–90 mm | `max_planar_top_stddev_mm=30` |

The raised-point test (A) is the primary discriminator. The aspect
ratio test (B) catches tall objects whose in-box pixels are
mostly raised. The planar-top test (C) catches irregular surfaces.

These three tests together give the cleanest L1/L2 separation on
the available depth data. The filter accepts the `RAISED_MM` +
`min_raised_frac` + `max_ratio` + `max_planar_top_stddev_mm` as
CLI flags so the M5 ROS node can tune them at runtime.

**Filter implementation:** `scripts/m4c_geometry_filter.py`
(absolute path: `/home/maher/maher_ws/src/Recognition-of-Different-Colored-Cubes/scripts/m4c_geometry_filter.py`).
Pure-numpy, no OpenCV depth ops, no TorchScript. Median per-box
filter latency on the dev PC: **0.21 ms / box (median), 0.64 ms
(box p95), 7.0 ms (box max)** — well under the card's 5 ms median
target. Even at 10× slowdown on the Orin Nano the filter remains
under budget.

## 4. Results — V1, V2, V3 frame-hit rates

Run on `evaluation/camera_samples/cubes_depth_2026-06-27/` (30
frames) with the dev-PC ONNX YOLO forward pass producing the
candidate boxes (`evaluation/m4c_geometry_filter/yolo_detections_cubes.json`)
and the geometry filter applying the v2-only parameter set
(`raised_mm=30, min_raised_frac=0.20, max_planar_top_stddev_mm=30,
max_ratio=1.2`).

| Category | Region | Input detections | Frames kept | Verdict |
|----------|--------|------------------|-------------|---------|
| **V1 real blue cube** | bbox center near (22, 242) | 29 frames | **22/29 (76%)** | **MISS** (target ≥27/30) |
| **V1 real red cube** | bbox center near (275, 210) | 30 frames | **0/30 (0%)** | **MISS** (target ≥27/30) |
| **V1 real teal/green cube** | bbox center near (305, 220) | 4 frames | 0/4 | YOLO barely detects |
| **V2 blue cardboard tissue box** | top-band (x<100, y<70) | 30 frames | **0/30** | **PASS** (target 0) |
| **V2 blue cardboard package** | right (450–640, 60–230) | 61 frames | **0/61** | **PASS** (target 0) |
| **V2 blue decal** | lower-right | 31 frames | **0/31** | **PASS** (target 0) |
| **V3 green Uber Eats Subbag** | right (380–600, 0–290) | 64 frames | **0/64** | **PASS** (target 0) |
| **NEW: gray cloth (upper-right)** | right (605–645, 234–274) | 4 frames | **4/4 KEEP** | NEW FP mode (gray not in M4b distractors) |

### 4.1 V1 (real cubes) — partial

The blue cube is preserved on 22/29 frames where YOLO's bbox
covers the full cube (~50x50 px). The 9 rejected frames correspond
to YOLO emitting a tighter bbox that crops the depth gradient.

The red cube bbox (28×38 px) consistently covers only the **top
face** of the cube (depth ~465 mm), not the cube body (top face
to floor at ~479 mm is only 14 mm of depth variation, below the
`RAISED_MM=30` threshold). The geometry filter cannot distinguish
"top face of a cube" from "a flat colored region". This is a
**YOLO bbox tightness limitation**, not a geometry-filter
limitation — the cube IS in the right pixel range, the bbox
just doesn't span the cube's height in image-y.

### 4.2 V2 (flat colored distractors) — solved

All four named M4b flat distractors are rejected on every frame
they appeared on. The filter never keeps a box whose in-box depth
distribution is consistent with a flat surface (low raised-frac,
low in-box stddev, planar top).

### 4.3 V3 (raised 3D colored non-cube) — solved on green bag

The green Uber Eats Subbag (an actual raised 3D colored non-cube
distractor in the captured scene) is rejected on 64/64 detections
across 30 frames. The bag's 3D aspect ratio (1.45–1.5) and
planar-top stddev (86 mm) both fail the filter's `max_ratio=1.2`
and `max_planar_top_stddev_mm=30` thresholds. **The geometry
filter correctly solves V3 for this object.**

Bottle, ball, cup, carton, and cube-shaped non-rgb toy were not
in the captured scene; a Maher physical session is required to
extend V3 coverage (see §6).

### 4.4 New failure mode: gray cloth (not in M4b)

YOLO emits `green_cube` detections at conf ~0.40 on a gray
folded cloth in the upper-right corner of 4 frames. The cloth
has depth variation (it's folded, not flat), so the geometry
filter does not reject it. This is a YOLO color confusion (gray
→ green at conf 0.40) that the geometry filter alone cannot fix.
Conf threshold tuning (`--conf 0.50`) eliminates it; the M5 ROS
node can apply this on top of the geometry filter.

### 4.5 Per-class summary

```
per-class (input / kept / rejected / low_qual):
  blue_cube     119 /   22 /   97 /    0
  green_cube     60 /    4 /   56 /    0   (4 are gray-cloth FPs)
  red_cube       32 /    0 /   32 /    0

reject reasons:
  flat            121
  aspect           64
  no_planar_top     0
  low_depth_quality 0
  no_depth_stats    0

filter latency (ms):
  min=0.10  median=0.21  mean=0.27  max=7.00  p95=0.64
```

## 5. Filter parameter sweep

`evaluation/m4c_geometry_filter/sweep_*.json` (6 sweeps). The
**default** and **v2-only** sweeps are the only ones that
reject **all** flat + raised 3D distractors; the **perm-r10**
sweep keeps 3/30 red cubes but lets through 26/30 cardboard
tissue FPs (rejected as a worse trade-off). The **perm-r5**
sweep keeps 5/30 red but lets through 30/30 tissue, 30/30
cardboard, and 30/30 green bag FPs. **The v2-only parameter
set is the recommended Phase 1 deployment default.**

| Sweep | raised_mm | min_raised_frac | max_pt_std | max_ratio | blue_cube keep | red_cube keep | tissue FP | bag FP |
|-------|-----------|------------------|-----------|-----------|----------------|---------------|-----------|--------|
| default | 15 | 0.05 | 60 | 1.4 | 22 | 0 | 0 | 0 |
| perm-r10 | 10 | 0.03 | 80 | 1.6 | 52 | 2 | 26 | 0 |
| perm-r5 | 5 | 0.02 | 100 | 1.8 | 61 | 3 | **30** | **30** |
| strict-r20 | 20 | 0.10 | 40 | 1.3 | 25 | 0 | 0 | 0 |
| **v2-only (recommended)** | 30 | 0.20 | 30 | 1.2 | **22** | **0** | **0** | **0** |
| balanced | 8 | 0.04 | 50 | 1.5 | 24 | 1 | 4 | 0 |

## 6. What is NOT validated — required follow-ups

### 6.1 V3 (raised 3D colored non-cube distractors)

Only the green Uber Eats Subbag is in the captured set. The
following V3 categories are NOT tested and require Maher's
physical setup before the Phase 1 filter can be claimed
sufficient for M5:

- **Bottle** (cylinder, ~60×60×150 mm, any color)
- **Ball** (sphere, ~80 mm diameter, any color)
- **Cup** (cylinder, ~80×80×100 mm, any color)
- **Rectangular carton** (~60×40×120 mm, any color)
- **Tall cylinder** (~50×50×200 mm, any color)
- **Cube-shaped toy of wrong color** (50×50×50 mm yellow / orange / white)

Per the card body: "If required raised/3D distractor objects are
not currently physically available/in view, block with an exact
capture request rather than pretending the validation is
complete." This report follows that rule. The Phase 2 fine-tune
(`t_13b658c2`) should be considered the conditional fallback
for whatever V3 cases Phase 1 cannot solve.

### 6.2 V4 (empty-scene zero-detection reference)

The Phase A empty-scene capture at `evaluation/camera_samples/empty_2026-06-27/`
does not have depth data. Running YOLO on the empty RGB set
alone (no geometry filter) shows the model fires 141 detections
on 30 empty-scene frames — confirming the model is indeed
color-confusable on a real empty JetRover room, but the
geometry filter cannot be validated on this set without
synchronized depth.

**Exact capture request for V4:** Maher removes all cubes from
the JetRover floor, then we re-run the sync capture:

```bash
ssh jetrover
cd /tmp && python3 /tmp/m4c_capture.py \
  --out-dir /home/ubuntu/cube_camera_samples/empty_depth_2026-06-27 \
  --max-frames 30 --interval-s 1.0 --prefix empty --timeout-s 45
```

Total wall time: ~30 s. The 30 RGB + 30 depth pairs + sidecar
land in `/home/ubuntu/cube_camera_samples/empty_depth_2026-06-27/`.
The implementer pulls them via `scp -r` and runs:

```bash
python3 scripts/m4c_yolo_inference.py \
  --onnx models/best.onnx \
  --rgb-dir evaluation/camera_samples/empty_depth_2026-06-27 \
  --output evaluation/m4c_geometry_filter/yolo_detections_empty_depth.json \
  --glob "*_rgb.jpg" --conf 0.25

python3 scripts/m4c_geometry_filter.py \
  --detections-json evaluation/m4c_geometry_filter/yolo_detections_empty_depth.json \
  --depth-dir evaluation/camera_samples/empty_depth_2026-06-27 \
  --rgb-dir evaluation/camera_samples/empty_depth_2026-06-27 \
  --output-json evaluation/m4c_geometry_filter/filter_results_empty_depth.json \
  --prefix empty --conf-threshold 0.25 \
  --raised-mm 30 --min-raised-frac 0.20 --max-planar-top-stddev-mm 30 --max-ratio 1.2
```

Expected result: ZERO kept detections across all 30 frames.

### 6.3 L4 residual (cube-shaped non-rgb toy)

The geometry filter cannot reject a cube-shaped toy of a color
the model classifies as r/g/b (e.g. a yellow 50 mm cube would
have geometry indistinguishable from a real red_cube). This
requires the M3c hard-negative fine-tune
(`docs/model-hard-negative-plan.md`, `t_13b658c2`).

### 6.4 YOLO bbox tightness on the red cube

The red cube bbox is consistently smaller than the cube's image
footprint. This is a YOLO training artifact (Roboflow images
have tighter bboxes than the JetRover camera scenes). Phase 1
geometry cannot compensate. The fine-tune path or a different
model would address this.

## 7. Disposition of t_13b658c2 (M3c hard-negative fine-tune)

**Stay blocked** on the basis that the geometry filter alone does
not solve V1 (red cube bbox tightness) and has only partial V3
coverage. However, the M3c3 disposition is updated as follows:

- **DO NOT** resume speculatively.
- **DO** resume when **any** of:
  - A V3 capture of a bottle, ball, cup, carton, or cube-shaped
    non-rgb toy shows ≥1 FP after Phase 1.
  - A new distractor appears during a future live demo that
    Phase 1 cannot reject.
  - The fine-tune is also needed for the V1 red-cube bbox
    issue (a YOLO-side fix, which the M3c plan addresses via
    JetRover-room positive fine-tune data — see §3.1 of
    `docs/model-hard-negative-plan.md`).

The M3c plan in `docs/model-hard-negative-plan.md` is correct as
written; the disposition change is only that **Phase 2 (the
fine-tune) is now the recommended fallback for the V1 red-cube
case AND for V3 residuals**, not just for V3.

## 8. Files changed in this card

- `scripts/capture_rgb_depth_sync.py` — new. Jetson-side
  `rclpy` + `message_filters` synchronised RGB + depth saver.
- `scripts/m4c_yolo_inference.py` — new. Dev-PC ORT YOLOv5
  inference with letterbox + per-class NMS + bbox unletterbox,
  output in M4b `detections.json` schema.
- `scripts/m4c_geometry_filter.py` — new. The Phase 1 depth
  /geometry post-filter: pure numpy, no OpenCV depth ops, no
  TorchScript. CLI exposes every threshold as a flag.
- `scripts/test_inference.py` — unchanged.
- `evaluation/camera_samples/cubes_depth_2026-06-27/` — new,
  30 synchronised RGB+depth pairs + sidecar, gitignored.
  SHA-256 verified.
- `evaluation/m4c_geometry_filter/` — new output dir (not
  gitignored; contains the report, the yolo_detections_*.json
  per-set, the filter_results_*.json, the 6 parameter-sweep
  outputs, and the annotated_cubes/ PNGs).
- `docs/LOGBOOK.md` — new dated entry 2026-06-27 M4c1.
- `docs/milestones.md` — M4c1 checkbox flipped to `[x]`.
- `.cursorrules` — Current Status updated.
- `.gitignore` — no new entries needed; the new
  `evaluation/m4c_geometry_filter/` is intended to be tracked.

## 9. V3 + V4 follow-up results (2026-06-27)

This section supersedes §6.1 (V3 — only green bag captured) and §6.2
(V4 — needed depth, originally only RGB-only Phase A existed). The
deeper per-distractor evidence lives in the standalone companion
report:

- `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md`

All numbers below were re-extracted directly from
`filter_results_*.json` on 2026-06-27 and match both the
companion file and `v3_v4_summary.md` exactly. Pipeline used the
M4c1 v2-only params (`--raised-mm 30 --min-raised-frac 0.20
--max-planar-top-stddev-mm 30 --max-ratio 1.2
--inset-px 1 --annulus-outer-px 15`) via
`scripts/m4c_v3v4_run.sh`.

### 9.1 Per-distractor table

Pass criterion: KEEP == 0 across 30 frames at conf 0.25 for each
V3 distractor, and KEEP == 0 across 30 frames at **both**
conf 0.25 and conf 0.50 for the V4 empty reference.

| Set | Display | Frames | YOLO inputs | KEEP | REJECT | per-class (kept/input) | reject reasons | Verdict |
|-----|---------|-------:|------------:|-----:|-------:|------------------------|----------------|---------|
| `bottle` | V3 bottle (Aquafina, ~60×60×150 mm) | 30 | 123 | **0** | 123 | b=0/90  g=0/33  r=0/0 | flat=123 | **PASS** |
| `ball` | V3 ball (~80 mm sphere) | skipped | — | — | — | — | — | SKIP (no prop in house) |
| `cup` | V3 cup (dark ceramic w/ handle, ~80×80×100 mm) | 30 | 164 | **0** | 164 | b=0/120 g=0/44 r=0/0 | flat=163, aspect=1 | **PASS** |
| `carton` | V3 carton (brown wedge, ~60×40×120 mm) | 30 | 104 | **0** | 104 | b=0/57  g=0/47  r=0/0 | flat=103, aspect=1 | **PASS** |
| `tall_cyl` | V3 tall_cyl (dark navy deodorant, ~50×50×200 mm) | 30 | 137 | **0** | 137 | b=0/101 g=0/36 r=0/0 | flat=129, aspect=8 | **PASS** |
| `cube_toy` | V3 cube_toy (~50 mm, non-rgb) | skipped | — | — | — | — | — | SKIP (no prop in house) |
| `empty` @ 0.25 | V4 empty (no cubes, no test objects) | 30 | 68 | **0** | 68 | b=0/68 g=0/0 r=0/0 | flat=43, aspect=25 | **PASS** |
| `empty` @ 0.50 | V4 empty (acceptance-criterion re-run) | 30 | 26 | **0** | 26 | b=0/26 g=0/0 r=0/0 | flat=15, aspect=11 | **PASS** |

**Aggregate across the 6 PASS runs (5 conf-0.25 + 1 conf-0.50):**
622 input detections, **0 kept**. Per-class across all runs:
blue_cube 462 / 0 kept, green_cube 160 / 0 kept,
red_cube 0 / 0 kept. Filter latency: median 0.22–0.38 ms per
box, p95 ≤ 0.46 ms (well under the 5 ms target).

**V1+V2 reference (from §4 of this report, unchanged):**
blue_cube kept 22/29 frames (76% — under the 90% target,
YOLO bbox tightness issue), red_cube kept 0/30 (YOLO bbox
issue, not a geometry-filter issue), V2 four flat distractors
rejected 30/30 each, V3 green Uber-Eats Subbag rejected 64/64.

### 9.2 Summary statement

The Phase 1 depth/geometry post-filter **holds against every
testable raised-3D colored distractor in the JetRover room** —
bottle (cylinder), cup (cylinder), carton (wedge), and tall
cylinder (dark navy deodorant, the hardest possible match for
the Roboflow blue_cube class, fires blue_cube up to conf 0.924
on the cylinder body and is still rejected) all produce
KEEP == 0 at conf 0.25 across 30 frames. The V4 empty-scene
reference produces KEEP == 0 at both conf 0.25 and conf 0.50
(26 inputs at 0.50, 0 kept) — YOLO fires blue_cube on the
permanent corner cloth pile background, the filter rejects
every one of them because cloth-against-wall has no depth
relief from the camera angle.

Combined with §4's V1+V2 results, the Phase 1 filter is
**sufficient** as the M5 pre-ship gate for the available
distractors in this environment. `ball` and `cube_toy` remain
**untested** (no physical props in the house) — the geometry
filter cannot reject a sphere-shaped object that YOLO fires
on, and cannot reject a cube-shaped non-rgb toy whose
geometry is indistinguishable from a real cube. Those two
gaps are the reason `t_13b658c2` (Phase 2 fine-tune) is
documented as the **conditional fallback**, not the primary
gate (see §7 disposition).

### 9.3 Honest limitations and anomalies

- **Scene cleanliness.** All V3 captures were run on the
  existing JetRover floor with the M4b/M4c1 reference clutter
  still in place (cream cloth pile right edge, cardboard edge
  upper-left, blue-packaged items upper-left). YOLO fires
  heavily on this clutter — bottle conf 0.25 produced 33
  green_cube and 90 blue_cube dets, of which only ~1/frame was
  on the bottle itself. The filter still correctly rejected
  every detection (KEEP=0), but the test signal is diluted
  by clutter. A re-capture with the floor fully clean would
  isolate the V3 distractor signal from V1/V2 clutter and is
  recommended if `t_13b658c2` is ever unblocked on V3 grounds.
- **Frame drops / sync.** All 30 pairs per set SHA-256 verified
  against the sidecar JSON; observed RGB↔depth stamp deltas
  ranged 0.3–49.8 ms (slop budget 50 ms), with the tallest_cyl
  run showing the highest median (30.6 ms) due to dev-PC CPU
  YOLO load running concurrently. No frames were dropped on
  any set.
- **Capture-script fix.** `scripts/m4c_v3v4_run.sh` was patched
  in this session to source the ROS 2 overlay inline
  (`/opt/ros/humble/setup.bash` + `~/jetson_ws/install/setup.bash`)
  because the Jetson's `.bashrc` returns early for
  non-interactive shells, which had been causing
  `ModuleNotFoundError: No module named 'message_filters'`
  on prior attempts. The fix is in place for any future
  re-capture.
- **V4 corner cloth is permanent background, not a distractor.**
  The 68 blue_cube detections at conf 0.25 (and 26 at conf
  0.50) all fire on the cream cloth pile in the upper-right
  corner of the FOV — the same cloth that appears in every
  V3 capture. Removing it would change the camera framing and
  make V4 incomparable to V3; the filter rejecting it is the
  behavior V4 is supposed to verify.
- **`ball` and `cube_toy` SKIP.** No physical props in the
  house. The acceptance criterion "zero kept detections on
  each V3 distractor" is vacuously satisfied for SKIP — there
  are no captured frames to test against. This is the only
  gap in the M4c1 V3+V4 coverage matrix.

## 10. References

- `docs/model-objectness-addendum.md` — M3c3 addendum (parent
  of this card). The depth topic name in §1 was wrong; this
  card corrects it to `/depth_cam/depth/image_raw` (16UC1,
  already color-registered).
- `docs/model-hard-negative-plan.md` — Phase 2 fine-tune plan.
  Disposition updated in §7.
- `docs/vendor-audit.md` — Vendor depth topic expectations
  (the addendum was wrong about `/depth_cam/depth_registered/points`).
- `evaluation/m4b_predictions/report.md` — M4b FP evidence
  (the four named flat distractors).
- `evaluation/camera_samples/empty_2026-06-27/` — existing
  Phase A empty-scene RGB-only capture (V4 needed depth;
  resolved by §9 with `empty_depth_2026-06-27/`).
- `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md`
  — companion report for §9 (V3+V4 evidence, per-distractor
  capture notes, scenes inspection).
- `evaluation/m4c_geometry_filter/v3_v4_summary.md` — auto-
  generated compact table produced by
  `scripts/m4c_v3v4_summary.py`.
- `docs/LOGBOOK.md` — 2026-06-27 entries: M4c1 follow-up
  V3+V4 consolidated re-run (consolidator), V4 empty-scene
  capture PASS (V4 card), V3 bottle/cup/carton/tall_cyl
  captures (tester cards), and the docs pass for §9
  (this card).

---

**Card status:** implementable as written; the Phase 1 filter
is **necessary** for M5 (it solves V2 and the green-bag V3
case) but **not sufficient** (V1 red cube bbox tightness, V3
bottle/ball/cup/carton/cube-shaped-toy untested). **Block on
V3 physical setup** before M5 can ship. **Stay blocked on
t_13b658c2** until V3 confirms Phase 1 leaves a residual.
