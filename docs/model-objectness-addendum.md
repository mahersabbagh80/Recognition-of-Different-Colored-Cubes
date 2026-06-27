# M3c3 — Cube-objectness addendum: does depth/geometry post-filter fix the real problem?

Date: 2026-06-27
Scope: research / decision only. No code, no training, no exports.
Parent: `t_becf3451`. Predecessor: `t_bfeee153` (`docs/model-alternative-research.md`).
Context that triggered this card: Maher and the orchestrator reviewed the
M3c2 recommendation (option F — YOLO + depth/geometry post-filter) and
flagged that the green-soil-bag framing was too narrow. The detector has
learned a color-to-class shortcut; the required behavior is "object first,
color second", validated against colored **raised 3D** non-cube distractors
as well as flat surfaces.

This addendum answers the seven questions in the card body honestly,
including the cases where the geometry filter is **insufficient** and
fine-tuning or a hybrid path is mandatory.

## 0. TL;DR

The M3c2 recommendation (option F: YOLO + depth/geometry post-filter) is
**partially correct but not sufficient as the primary path** under the
sharper requirement. Specifically:

- A height-above-floor test reliably rejects all four named M4b flat
  distractors (green soil bag, blue cardboard package, blue decal, red
  chair/object). It costs nothing new, runs in ~1-2 ms per box on Orin
  Nano, and reuses `/depth_cam/depth_registered/points` which is already
  live from the vendor launch. This part of the original recommendation
  stands.
- A height-above-floor test **does NOT** reject raised 3D colored
  non-cube distractors. A 150 mm green bottle, a 80 mm green ball, a
  120 mm red book, a 100 mm blue cup, or a cube-shaped toy all pass a
  height test if they sit on the floor at the same distance.
- Some of those 3D distractors can be rejected by **additional
  geometric tests** beyond height (3D bounding-box aspect ratio,
  planar-top / flat-face test, curvature statistic). I detail them in §3.
- Some distractors are **fundamentally indistinguishable from cubes by
  geometry alone**: a cube-shaped wooden toy, a cube-shaped cardboard
  box, or any object with 3D extents within ~20% of 50 mm × 50 mm × 50 mm
  and three orthogonal planar faces. For these, only a shape-aware
  detector (i.e. fine-tuning with cube vs other-shape negatives, or a
  3D shape classifier) can resolve the ambiguity.

**Updated recommendation (replaces the M3c2 primary):**

1. **Phase 1 — Hybrid fast path (recommended):** ship a depth/geometry
   post-filter that combines **height-above-floor + 3D aspect-ratio +
   planar-top test** as the first defense. This kills every named M4b
   flat distractor **plus most raised 3D distractors that are not
   cube-shaped** (bottles, cups, balls, cylinders, books, flat boxes).
   ~2 hours implementer work. **Required gate before M5.**
2. **Phase 2 — Conditional fine-tune:** execute the existing M3c hard-
   negative plan (`docs/model-hard-negative-plan.md`, option E) **only
   if** Phase 1 leaves residual FPs on a NEW cube-shaped or near-cube
   distractor. The Phase 1 filter cannot solve the cube-shaped-toy
   edge case, so the fine-tune remains the "general" fallback.
3. **Validation set must include raised 3D colored non-cube distractors**
   before M5 is allowed to ship. The 30-frame M4b set is no longer
   sufficient on its own.

The blocked card `t_13b658c2` stays blocked under this updated plan; it
is now the **explicitly planned** Phase 2 rather than the primary path.
See §7 for the full disposition of `t_13b658c2` and the existing
todo children.

## 1. Does depth/geometry solve the *actual* cube-objectness problem?

Honest answer: **no, not alone.** It solves a strict subset.

The actual cube-objectness requirement has two layers:

| Layer | Requirement | Can depth/geometry solve it? |
|------|-------------|-----------------------------|
| **L1 — Non-cube background** | Reject saturated colored regions that are not physical objects (soil bag, decal, cardboard package, painted chair). | **Yes — trivially.** All four are flush with the floor or a wall. A height-above-floor test on the points inside the YOLO box gives near-zero; a real cube gives ~50 mm. |
| **L2 — Raised non-cube object** | Reject saturated colored 3D objects that are not cubes (bottle, ball, cylinder, cup, rectangular box, toy). | **Partially.** Aspect ratio, planar-top, and curvature tests reject most. A cube-shaped toy passes everything. |
| **L3 — Cube-shaped object, wrong color** | A physical cube that is, say, yellow or orange. | **No.** The current 3-class head has no negative class for "cube but not red/green/blue"; this is a class-set problem, not a geometry problem. |
| **L4 — Cube-shaped object, right color, not a "cube"** | A red Rubik's-cube-shaped thing, a green wooden toy cube, etc. | **No — geometry alone cannot tell two cubes apart.** This is the residual failure mode the post-filter cannot fix. |

The M3c2 report framed the problem as L1 ("named flat distractors"). The
corrected problem statement adds L2 and L4. L1 is what depth/geometry
buys you for ~2 hours of work; L2 is what ~6 hours of geometry-plus-
fine-tune buys you; L4 is what ~3 hours of cube-shape fine-tune buys you.

The previously-named M4b distractors are all L1, which is why the M3c2
analysis (read narrowly) looks correct. The corrected analysis must
also consider L2 and L4. The hard-negative fine-tune (`docs/model-
hard-negative-plan.md`) addresses L4 by adding cube-shape supervision
in the model weights; it is the correct general fallback.

## 2. Validation matrix (rows: object, columns: detection behavior)

This is the §3 acceptance matrix the card body requires. Rows are
organized as "real cubes" (positives) and "colored non-cube distractors"
(negatives), with the negatives split flat vs raised/3D. Each cell
indicates whether the depth/geometry filter (Phase 1) and the existing
hard-negative fine-tune (Phase 2, option E) are sufficient.

**Cube-positive rows (must keep):**

| Object | Distance | YOLO conf (M4b) | Phase 1 (depth/geometry) verdict | Phase 2 (fine-tune) verdict |
|--------|---------:|----------------:|----------------------------------|------------------------------|
| Blue 50 mm wooden cube on floor | 20 cm | 0.97-0.99 (real) | **Pass** — height ≈50 mm, ratio ≈1:1:1, planar top | **Pass** |
| Blue 50 mm wooden cube on floor | 40 cm | 0.97-0.99 | **Pass** | **Pass** |
| Blue 50 mm wooden cube on floor | 60 cm | 0.97-0.99 | **Pass** | **Pass** |
| Blue 50 mm wooden cube on floor | 80 cm | 0.97-0.99 | **Pass** (point density thinner; need ≥30 inside-box points per §4) | **Pass** |
| Green 50 mm wooden cube on floor | 20-80 cm | 0.26-0.41 (low — current weak point) | **Pass — geometry independent of conf** | **Pass** (fine-tune improves conf too) |
| Red 50 mm wooden cube on floor | 20-80 cm | 0.68-0.82 | **Pass** | **Pass** |

**Cube-negative rows, FLAT (flush with floor or wall):**

| Object | Color | M4b conf | Phase 1 verdict | Phase 2 verdict |
|--------|-------|---------:|-----------------|-----------------|
| Cardboard package (right of frame) | blue | 0.83-0.88 | **Reject** — height ≈0 mm vs background annulus | **Reject** |
| Soil/sand bag (right) | green | 0.65-0.78 | **Reject** — height ≈0 mm | **Reject** |
| Decal (lower-right) | blue | 0.25-0.58 | **Reject** — height ≈0 mm | **Reject** |
| Red chair/object (left) | red | 0.31-0.39 | **Reject** — height ≈0 mm | **Reject** |

**Cube-negative rows, RAISED 3D (must be added to validation set):**

| Object | Color | Expected behavior | Phase 1 (depth/geometry) verdict | Phase 2 (fine-tune) verdict |
|--------|-------|-------------------|----------------------------------|------------------------------|
| Bottle (cylinder, ~60 mm × 150 mm) | green/blue/red | Should NOT detect | **Reject** — 3D ratio 1:1:2.5 fails cube-ratio test | **Reject** |
| Cup (cylinder, ~80 mm × 100 mm) | blue/red | Should NOT detect | **Reject** — 3D ratio 1:1:1.2 + no planar top (cup is open/curved) | **Reject** |
| Ball (~80 mm diameter sphere) | green/blue/red | Should NOT detect | **Reject** — planar-top test fails (no flat upper face); curvature statistic fails | **Reject** (if ball is in training negatives) |
| Rectangular box (e.g. 60×40×120 mm carton) | any | Should NOT detect | **Reject** — 3D ratio 3:2:1 fails cube-ratio test | **Reject** (if carton in training negatives) |
| **Tall cylinder (~50 mm × 200 mm)** | any | Should NOT detect | **Reject** — 3D ratio 1:1:4; height test alone passes but ratio fails | **Reject** |
| **Cube-shaped toy (50×50×50 mm)** | yellow, orange, white | Should NOT detect (wrong class) | **FAIL** — passes every geometric test (it *is* a cube). Phase 1 cannot distinguish this from a red_cube/green_cube/blue_cube. | **Reject** (only with hard-negative cube-vs-non-cube-class training, OR with class-set extension to `cube_other`) |
| Book (200×150×30 mm flat) | red/blue | Should NOT detect | **Reject** — 3D ratio ~7:5:1 fails ratio test | **Reject** |
| Cube-shaped wooden block of wrong color (e.g. yellow 50 mm cube) | yellow | Should NOT detect (class set is r/g/b only) | **FAIL** — geometry says it is a cube. Class head has no `cube_other` to suppress it. | **Reject (conditional)** — requires adding yellow cubes as training negatives for r/g/b classes, OR extending class set |

**Empty-room rows (zero detections expected):**

| Object | Phase 1 verdict | Phase 2 verdict |
|--------|-----------------|-----------------|
| Empty JetRover room (30-frame Phase A set already exists) | **Zero** — no YOLO candidates at any reasonable conf on empty scene (per M4b the model produces ~6 dets/frame on this set; after Phase 1, those should all be rejected as height ≈0). | **Zero** — fine-tuned model should also produce zero |

The matrix above is the explicit "validation matrix with rows for red/
green/blue cubes and red/green/blue non-cube distractors, split into flat
vs raised/3D" the card body requires.

## 3. Geometric tests that distinguish a cube from raised non-cube objects

For a YOLO candidate box at pixel `(x1, y1, x2, y2)` on a 640×360 RGB
frame, subscribed alongside `/depth_cam/depth_registered/points`
(`sensor_msgs/PointCloud2` in `depth_cam_color_optical_frame`):

### 3.1 Height above floor (L1 — flat-distractor killer)

```
inside_box = points where u in (x1+inset, x2-inset), v in (y1+inset, y2-inset)
annulus    = points where u in (x1-2*inset, x1-inset) U (x2+inset, x2+2*inset)
                                    v in (y1-2*inset, y2+2*inset)
                or similar outer ring (configurable)

median_z_inside  = median(inside_box.z)
median_z_annulus = median(annulus.z)
height           = median_z_inside - median_z_annulus

Reject if height < MIN_HEIGHT (recommended 15 mm; one third of cube's 50 mm
nominal, with margin for Orbbec noise).
```

This is the test in the M3c2 §3 D option. It rejects all four named M4b
flat distractors. It does NOT reject raised 3D distractors.

### 3.2 3D bounding-box aspect ratio (L2 — non-cube-shape killer)

For each candidate, compute the axis-aligned 3D bounding box of the
filtered points (RANSAC plane fit to remove floor; cluster the rest).

```
dims = (extent_x, extent_y, extent_z)
sorted_dims = sorted(dims)
ratio_check = (sorted_dims[2] / sorted_dims[0]) < MAX_RATIO
```

For a real cube at any orientation, `extent_x ≈ extent_y ≈ extent_z`
and `ratio_check` passes (recommended threshold `MAX_RATIO = 1.4`).
A bottle (60 × 60 × 150 mm) gives `ratio = 2.5`, fails. A rectangular
carton (60 × 40 × 120 mm) gives `ratio = 3.0`, fails. A book
(200 × 150 × 30 mm) gives `ratio ≈ 7`, fails. A cup (80 × 80 × 100 mm)
gives `ratio = 1.25`, passes — needs §3.3.

### 3.3 Planar-top / flat-face test (L2 — sphere/cylinder killer)

For each candidate, find the largest coplanar patch on the upper face
of the point cluster:

```
# Estimate normals (e.g. PCA over k-NN, or Open3D estimate_normals)
# Find the top 20% of points by z
# Cluster normals; count points with normal.z > 0.7 (pointing up)
planar_top_fraction = count(normal.z > 0.7 in top 20%) / count(top 20%)
```

A real cube's top face has ~100% upward-pointing normals in the upper
plane. A sphere has continuous normals, fraction ≈ 0.5 (only the topmost
point is "up"). A cup has open/curved top, fraction ≈ 0.3. A bottle cap
might pass for a small bottle but the aspect-ratio test catches it.

Reject if `planar_top_fraction < MIN_PLANAR_FRAC` (recommended 0.6).

### 3.4 Curvature / sharp-edge statistic (L2 supplement)

Cubes have **sharp depth discontinuities** at edges (90° corners in the
depth map). Cylinders and spheres have smooth depth gradients. Compute
the standard deviation of the local depth gradient magnitude inside the
box; cubes are high variance, smooth shapes are low.

```
# For each point, compute depth(z) gradient to neighbors
grad_z = gradient(points.z)  # via grid or neighbor lookup
grad_var = variance(grad_z)
```

Reject if `grad_var < MIN_GRAD_VAR` (calibrate on the real cube vs a
green ball on the validation set). Less reliable than §3.3 on sparse
Orbbec pointclouds at 50 mm scale.

### 3.5 What geometry cannot do

The L4 case — a cube-shaped object of a color the model classifies as
red/green/blue — is fundamentally a **class-head** problem. Geometry
says "this is a cube"; the model class head says "and I will call it
red_cube if it's red." The only fixes are:

- Extend the class set to include `cube_other` / `yellow_cube` /
  `orange_cube` and treat them as suppress-classes (more training data,
  bigger model, more inference time).
- Add hard-negative examples of cube-shaped non-rgb objects to the
  training set (the existing M3c plan covers this implicitly if such
  frames are in the capture set).
- Add a post-classification "is this the only r/g/b cube-shaped thing
  in the frame" sanity check (helps in single-target mode, fails in
  multi-target).

None of these are 2-hour fixes. They are the "if Phase 1 leaves residual
FPs" trigger for Phase 2 (the M3c fine-tune).

### 3.6 Combined Phase 1 filter (decision logic)

```
candidate_box: YOLO detection (class, conf, x1, y1, x2, y2)
on /depth_cam/depth_registered/points with timestamp >= candidate timestamp:
  if no depth data:           KEEP (mark low_confidence_depth=true)
  elif in_box_points < N_MIN: KEEP (mark low_confidence_depth=true)
  else:
    height = median(z in box) - median(z in annulus)
    dims   = 3D bounding box extents of in-box points after floor removal
    planar = fraction of top-face points with normal.z > 0.7
    if height < 15 mm:        REJECT (flat)
    elif ratio(dims) > 1.4:   REJECT (non-cube aspect)
    elif planar < 0.6:        REJECT (non-planar top)
    else:                     KEEP
```

Recommended defaults (tune on the validation set in §4):

- `MIN_HEIGHT = 0.015 m` (15 mm)
- `MAX_RATIO = 1.4`
- `MIN_PLANAR_FRAC = 0.6`
- `N_MIN = 30` (inside-box points; below this the height/ratio stats
  are unreliable and we fall back to "trust YOLO" with a depth-quality
  flag for debugging)
- `INSET_PX = 4` (avoid YOLO box edge bleed)

## 4. Minimum validation set before M5 is allowed

The M4b 30-frame set is no longer sufficient. The new validation set
must include **flat distractors** (already covered by M4b) AND
**raised 3D colored non-cube distractors** (NOT covered by M4b). The
acceptance criteria for M5 to ship are:

| Set | Count | Composition | Source | Acceptance criterion |
|-----|------:|-------------|--------|----------------------|
| **V1 — Real cubes (positives)** | 30 | 10 frames × 3 colors at distance bands 20/40/60/80 cm (one cube of each color in view per frame) | New capture, `evaluation/camera_samples/cubes_2026-MM-DD_v1/` | ≥27/30 per-class hit rate (90%) after Phase 1 filter, conf ≥0.25 (or per-class thresholds). No false rejects on real cubes. |
| **V2 — Flat distractors (negatives)** | 30 | Same scene, all cubes removed, soil bag / cardboard package / decal / chair still in frame | Reuse the M4b 30-frame set OR re-capture | **Zero** `*_cube` detections after Phase 1 filter |
| **V3 — Raised 3D colored non-cube distractors (NEW)** | 30 | 10 frames each of: bottle/cup, ball/sphere, rectangular box, cube-shaped non-rgb toy (if available). Each frame also includes one real r/g/b cube to test that the filter does not over-reject positives. | **Maher physical session required.** Cube, ball, bottle, carton must be sourced. | Zero `*_cube` detections on the distractor objects. Per-class recall on the real cube in the same frame ≥27/30. |
| **V4 — Empty-scene (negatives)** | 30 | Reuse `evaluation/camera_samples/empty_2026-06-27/` | Already exists | **Zero** detections |
| **V5 — Phase 2 regression (only if Phase 2 runs)** | 60 | The §4 hardneg_validation set from `docs/model-hard-negative-plan.md` | New capture per M3c plan | ≥55/60 hit rate on real cubes, zero hits on V2/V3 distractors, empty-scene set still zero |

**Total new capture (above the M4b set): ~60 frames.** Maher physical
session required. The 30-frame empty-scene set is reused; the 30-frame
M4b set is reused as V2; the V1+V3 set is new and gated on Maher placing
cubes + sourcing 3D distractors.

**Hard gate for M5:** V1 ≥27/30 per-class recall AND V2 zero AND V3 zero
AND V4 zero, all measured against the Phase 1 filter at the recommended
thresholds. If V3 has any FP, Phase 1 is insufficient and Phase 2 (the
M3c fine-tune) is unblocked and runs against V3 as additional training
material.

## 5. Recommendation: which next implementation step?

The four options in the card body reduce to:

- **A) Depth/geometry spike only** — fast (2 hours), but explicitly
  incomplete because of L4 (cube-shaped toy). Reject.
- **B) Hard-negative fine-tune only** — correct general fix, but
  expensive (~3 hours + Maher session) and discards the geometry signal
  we already have. Overkill as the first step.
- **C) Hybrid: depth/geometry first, fine-tune if needed.** — *this is
  the recommendation.* Geometry fixes ~90% of the named failure modes
  for 30% of the effort. Fine-tune is the explicit fallback if V3 has
  any residual FP.
- **D) Architecture review first.** — no new architecture is needed;
  the YOLOv5s + TensorRT + post-filter stack is correct. Doing another
  architecture pass would burn a week without changing the answer.

**Recommended: option C (hybrid).** Implementation order:

1. **C1 — Depth/geometry post-filter implementer card** (Phase 1, this
   addendum's main output). Implementer builds the §3.6 combined filter,
   wires `/depth_cam/depth_registered/points` into `cube_detection_node`
   in addition to the existing RGB subscription, and exposes the
   thresholds (`min_height`, `max_ratio`, `min_planar_frac`,
   `min_in_box_points`) as ROS params so they can be tuned without
   rebuilding. Effort: ~2 hours focused work + Jetson build + smoke
   test on the M4b set + V4 empty-scene set. **Acceptance: V2+V4
   zero, V1 ≥27/30.** This card alone is sufficient if V3 has zero FP.
2. **C2 — V3 (raised 3D distractor) capture card.** Maher places cubes
   + sources a bottle, a ball, a cup, a rectangular carton, and a
   cube-shaped non-rgb toy (if available). Implementer runs
   `scripts/capture_frames.py` for ~60 frames. Hand-labels only the
   real cubes (the distractors are empty-label). Effort: ~1 hour
   capture + ~30 min label. **Acceptance: V3 zero dets on distractors,
   V1 ≥27/30 on real cubes.**
3. **C3 — Conditional Phase 2 unblock.** If C1 + C2 leave any residual
   FP on V3, execute the existing `docs/model-hard-negative-plan.md`
   (`t_13b658c2`). The V3 frames become part of the M3c training pool
   as additional hard-negatives. Effort: ~3 hours (the existing plan
   estimates). **Acceptance: V3 zero dets, V1 ≥27/30, V2+V4 zero,
   V5 ≥55/60.**
4. **C4 — Optional V3 cube-shaped-toy extension.** If even Phase 2
   cannot reject a cube-shaped non-rgb object (the L4 residual), the
   only honest answer is to extend the class set (add `cube_other`)
   or accept the residual. This is an open question for Maher and is
   NOT in scope of C1-C3.

### 5.1 Pass/fail criteria for the Phase 1 (C1) filter

These are the explicit criteria the card body requires:

**Pass criteria (the filter is good enough):**

- On V1 (real cubes, 30 frames): ≥27/30 per-class hit rate (90%).
  The geometry filter must NOT increase the false-reject rate vs raw
  YOLO. If real-cube recall drops below 90%, the `min_height` or
  `max_ratio` threshold is too tight; retune.
- On V2 (flat distractors): zero `*_cube` boxes in any of the 30
  M4b distractor frames. The four named M4b distractors (green soil
  bag, blue package, blue decal, red chair) must each show zero
  detections on every frame they appeared in.
- On V4 (empty scene, 30 frames): zero `*_cube` boxes. The model
  produced ~6 dets/frame on this set in M4b; Phase 1 must kill all.
- Per-box latency: median ≤5 ms on Jetson Orin Nano (after the
  14.66 ms YOLO engine latency, well under the 33 ms 30 Hz budget).
- Inside-box pointcount: at conf ≥0.25, ≥90% of YOLO boxes must have
  ≥N_MIN=30 inside-box points. If not, the Orbbec pointcloud is too
  sparse at the operating distance and Phase 1 needs a different
  signal (e.g. depth-image median inside the box rather than
  pointcloud-derived height).

**Fail criteria (Phase 1 is insufficient; trigger Phase 2):**

- Any of the four named M4b flat distractors still fires after
  Phase 1 (height test broken; probably `min_height` too low or
  annulus definition wrong).
- V1 recall drops below 90% (filter too aggressive; loosen).
- V3 (raised 3D distractors) shows any FP (Phase 1 fundamentally
  cannot solve L2 for cube-shaped objects → unblock Phase 2).
- Per-box latency exceeds 10 ms (pointcloud crop too expensive;
  reduce inset or skip the curvature/planar-top test).

## 6. If recommending fine-tuning, what hard-negative data is needed

This is for completeness; the primary path is C1 (depth/geometry),
not B (fine-tune alone). If Phase 2 (`docs/model-hard-negative-plan.md`)
is unblocked, it needs in addition to its §3 composition:

**Additional data over the M3c plan:**

- **V3 raised 3D colored non-cube distractor frames (~30 new).**
  These are NOT in the M3c plan's empty-label pool. They should be
  empty-label (the bottle/ball/carton are not r/g/b cubes) and added
  to the hard-negative training set. Color: at least one matching
  color per r/g/b to teach the model that "saturated colored 3D thing"
  is not a cube. Example: a green bottle, a green ball, a green
  rectangular carton.
- **Cube-shaped non-rgb toy (1-5 frames if available).** Yellow,
  orange, or white cube-shaped toy at the M6 distance bands. These
  are the L4 residual. Without them, fine-tuning cannot teach the
  class head that "cube shape + wrong color" is a negative.
- **Source-dataset augmentation with `AnnTarek/ShapeDetection`** is a
  *B-style* augmentation candidate. Its classes are
  `triangle, red_cube, yellow_cube, green_cube, blue_cube, rectangle,
  circle, ball, Cube_silicone` (~1319 train / 355 valid / 163 test).
  The `yellow_cube`, `rectangle`, `circle`, `ball`, `Cube_silicone`
  classes are exactly the shape-vs-color supervision the model needs.
  License is not visible on the page extract; verify before use. If
  license allows, merge the AnnTarek `valid/` split into the Phase 2
  training pool. This is the strongest external augmentation for the
  M3c plan and should be attempted as part of Phase 2, not as a
  separate experiment.

**Acceptance for the Phase 2 fine-tune:**

- V3 zero dets (raised 3D distractors; the new requirement).
- V1 ≥27/30 per-class hit rate (real cubes not over-rejected).
- V2 zero dets (flat distractors; the original M3c requirement).
- V4 zero dets (empty scene; the original M3c requirement).
- Roboflow validation mAP@0.5 ≥0.80 (M3c §2.1 requirement; ensure
  no forgetting).
- V5 (M3c's held-out 60-frame set) ≥55/60 hit rate on real cubes.

## 7. Disposition of blocked card `t_13b658c2` and todo children

This card body asks for explicit dispositions. Here they are:

### 7.1 `t_13b658c2` (M3c implementer: hard-negative fine-tune)

**Updated disposition:** keep as **explicitly planned Phase 2** of the
hybrid path, not as the primary path. Resume **only** when one of:

- The Phase 1 (C1) filter ships and a Phase 2 (C2) V3 capture shows
  ≥1 residual FP on a raised 3D colored non-cube distractor.
- A NEW distractor appears during the M5 live demo that Phase 1
  cannot reject.

Do NOT resume speculatively. Do NOT silently cancel. The M3c plan in
`docs/model-hard-negative-plan.md` is correct as written; the only
change is its priority (now second, not first) and its trigger
condition (V3 FPs, not generic FP cleanup).

### 7.2 `t_78cbe2ee`, `t_ee8a65d8`, `t_da0f7feb` (existing todo children)

Without the actual card bodies on hand I cannot disposition each
individually. The general rule for the orchestrator:

- Any card whose body depends on the M3c fine-tune path → keep in
  `todo`, parent it to the new C1 implementer card instead of
  `t_13b658c2`. When C1+C2 pass, re-evaluate.
- Any card whose body is M5 (live ROS node) → keep blocked until C1
  ships AND V2+V4 are zero AND V1 ≥27/30. C2 capture is a parallel
  track; V3 results gate whether Phase 2 (and therefore `t_13b658c2`)
  is needed for M5 to ship.
- If a child card is about capture or labeling that overlaps with the
  C2 capture session, fold it into C2 and cancel the child.

The orchestrator should fan out the new C1 + C2 cards and re-parent
existing children accordingly. I do not have the bodies of those three
children in this addendum; the orchestrator must verify each one
against the updated plan.

## 8. Open questions for Maher

1. **Approve the updated hybrid plan (C1 + C2 + conditional C3)?**
   C1 (depth/geometry post-filter) is the primary. C2 (V3 raised 3D
   distractor capture) is the gate that decides whether C3 (Phase 2
   fine-tune) is needed. Y/N.
2. **Source for V3 raised 3D distractors:** do you have, or can you
   source within the project's environment, a colored bottle, ball,
   cup, rectangular carton, and (ideally) a cube-shaped non-rgb toy?
   The Maher physical session for V1+V3 capture needs these objects
   in frame alongside the real r/g/b cubes.
3. **Cube-shaped toy (L4) policy:** if a cube-shaped yellow/orange/white
   object is placed in the scene, do you want it suppressed
   (requires extending the class set or adding L4 hard-negatives to
   Phase 2) or accepted as a known limitation (document and move on)?
   The current project definition does not specify this.
4. **Per-class vs single conf threshold:** the M3c plan §2.2
   recommended per-class thresholds. The Phase 1 filter is independent
   of conf thresholds; the YOLO conf is still the first gate. Confirm
   the per-class threshold approach is acceptable as the M5 deploy
   default.
5. **Validate the M4b 30-frame set can be reused as V2** (the flat
   distractor set). The M4b frames are gitignored; the orchestrator
   may need to re-capture if they are no longer on disk. Cost is the
   same Maher physical session.

## 9. References

Internal:

- `docs/model-alternative-research.md` — M3c2 primary report (option F
  recommendation). Superseded for primary path by this addendum;
  remains correct as the option F fallback analysis.
- `docs/model-hard-negative-plan.md` — M3c hard-negative fine-tune plan
  (option E); unchanged. Now Phase 2 / fallback rather than primary.
- `docs/vendor-audit.md` §1 — `/depth_cam/depth_registered/points`
  published by `peripherals/depth_camera.launch.py` /
  `dabai_dcw.launch.py` remap.
- `docs/architecture.md` — output topics (`/cube_detections`,
  `/cube_detections/vendor_objects`, `/cube_detections/debug_image`).
- `docs/evaluation.md` — 50-frame evaluation protocol; cube
  arrangement at 20/40/60/80 cm distance bands.
- `evaluation/m4b_predictions/report.md` and `detections.json` — the
  30-frame FP evidence; the four named M4b distractors.
- `docs/LOGBOOK.md` 2026-06-27 M4b entry.
- `models/README.md` — M2 artifact context.

External (unchanged from M3c2, plus new):

- depth_image_proc / PointCloudXyz (ROS 2): if a registered XYZ
  pointcloud is not directly available, the
  `depth_image_proc/point_cloud_xyz` node converts the depth image
  to a `PointCloud2`. For this project, `/depth_cam/depth_registered/
  points` is already published as a registered pointcloud by the
  vendor launch, so the conversion node is not needed.
  https://docs.ros.org/en/rolling/p/depth_image_proc/doc/components.html
  http://wiki.ros.org/depth_image_proc
- AnnTarek/ShapeDetection (GitHub): external shape-vs-color detection
  dataset; recommended B-style augmentation for Phase 2 if license
  checks out. https://github.com/AnnTarek/ShapeDetection
- Orbbec depth-accuracy reference (used to set realistic `MIN_HEIGHT`
  and `N_MIN` defaults): https://www.orbbec.com/blog/decoding-depth-
  camera-performance-quantitative-evaluation-of-accuracy-and-precision/
- Orbbec Dabai series overview: https://deepwiki.com/orbbec/ros_astra_
  camera/6.3-dabai-series

---

Card status: research/decision complete. **Updated primary path:**
hybrid (depth/geometry filter + V3 capture + conditional fine-tune).
**M3c2 primary (option F only) is downgraded to Phase 1 of the hybrid.**
`docs/model-alternative-research.md` should be cross-linked from
§0 / §6 with a "superseded by `docs/model-objectness-addendum.md` for
the primary-path question" note in a future maintainer pass.
