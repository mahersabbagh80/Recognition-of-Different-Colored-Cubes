# M3c — Hard-negative fine-tune plan for cube-vs-color false positives

Date: 2026-06-27
Scope: planning only (no training, no new model artifacts in this card)
Parent decision: Maher rejected M4b's "raise conf threshold or fine-tune" caveat.
The model must be both object-driven AND color-aware. A saturated color blob
that is not a small wooden cube (soil bag, cardboard package, decal, red chair)
must NOT be detected as a colored cube.

This document is the research/planning artifact. The implementing card will
follow it and produce `models/best_hardneg.pt` + matching ONNX + engine,
with the existing `models/best.pt` preserved until tester approval.

## 1. Why the current model fails — measured FP evidence

From `evaluation/m4b_predictions/detections.json` (30 live JetRover frames,
`scripts/test_inference.py --conf 0.25`):

| Class | Frames with ≥1 hit | Total dets (30 frames) | Mean conf | Max conf | Min conf |
|-------|-------------------:|-----------------------:|----------:|---------:|---------:|
| `blue_cube`  | 30/30 | 91 | 0.731 | 0.988 | 0.252 |
| `green_cube` | 30/30 | 52 | 0.567 | 0.783 | 0.257 |
| `red_cube`   | 30/30 | 34 | 0.708 | 0.822 | 0.306 |

The real cubes are ~50 mm wooden blocks on the JetRover platform floor. Three
classes x 30 frames = 90 expected true positives. The model emits 177 boxes
total — i.e. almost 1:1 detections to expected cubes, suggesting the model
fires on the cube AND on a background distractor every frame.

Spatial hot-spots per class (clustered by 80x60 px buckets, all 30 frames):

`blue_cube` hot-spots:
  - center ≈ (41, 41),   n=30/30, conf 0.97–0.99 (mean 0.98)  → REAL blue cube (top-left)
  - center ≈ (578, 133), n=30/30, conf 0.83–0.88 (mean 0.85)  → FP: blue cardboard package (right)
  - center ≈ (626, 323), n=18/30, conf 0.25–0.58 (mean 0.37)  → FP: blue decal (lower-right)
  - center ≈ (25, 186),  n=7/30,  conf 0.29–0.51 (mean 0.42)  → FP: other blue region (left)

`green_cube` hot-spots:
  - center ≈ (492, 154), n=30/30, conf 0.65–0.78 (mean 0.75)  → FP: green soil bag (right)
  - center ≈ (629, 257), n=20/30, conf 0.26–0.41 (mean 0.32)  → REAL green cube (lower-right, low conf)

`red_cube` hot-spots:
  - center ≈ (275, 212), n=30/30, conf 0.68–0.82 (mean 0.75)  → REAL red cube (center)
  - center ≈ (25, 190),  n=4/30,  conf 0.31–0.39 (mean 0.36)  → FP: red object on chair (left)

Interpretation: in 30 frames at conf 0.25, the model produces ~3 blue, ~1.7
green, ~1.1 red boxes per frame. The actual cubes account for **at most 1 hit
per class per frame** (mean conf red 0.75, blue 0.98, green 0.32 — green is
under-confident on the real cube). The other detections are recurring
distractor hits. Specifically:
  - Blue cardboard package is hit at conf 0.83–0.88 — HIGHER than several
    other classes' real-cube confidences. A conf threshold alone cannot
    separate real from FP without sacrificing green recall (real green cube
    at conf 0.26–0.41).
  - Green soil bag is hit at conf 0.65–0.78 — HIGHER than the real green cube.
  - Red chair object is hit at conf 0.31–0.39 — below the real red cube.

(The numeric conf values above are the raw 2-dp bucket-rounded values from
`evaluation/m4b_predictions/detections.json`. The full-precision minima are
0.252 / 0.257 / 0.306 for blue/green/red. A standalone verification script
`/tmp/hermes-verify-m3c-plan-numbers.py` re-derives all numbers in this
section from the raw JSON and asserts they match the plan.)

Therefore conf threshold tuning alone (the cheaper recommendation in the M4b
report) cannot satisfy Maher's "zero detections on known distractors"
criterion — at any threshold that retains the real green cube (≥0.26),
the green bag FP remains above it. **Fine-tuning is required.**

## 2. Acceptance criteria for the new model

These are the hard targets the next implementer must validate on the
JetRover validation set (defined in §4) before `models/best.pt` is replaced.

### 2.1 Per-class acceptance targets

| Class | Criterion on the JetRover-room validation set (60 frames, see §4) |
|-------|-------------------------------------------------------------------|
| `blue_cube`  | Real blue cube hit in ≥55/60 frames; zero hits on the blue cardboard package; zero hits on the blue decal. |
| `green_cube` | Real green cube hit in ≥55/60 frames; zero hits on the green soil bag. |
| `red_cube`   | Real red cube hit in ≥55/60 frames; zero hits on the red chair/object. |
| All classes  | On the 30-frame empty-scene set in `evaluation/camera_samples/empty_2026-06-27/`, **zero detections at the chosen threshold** (i.e. the model produces no `*_cube` boxes in a JetRover room with no cubes at all). |

### 2.2 Threshold policy

Pick one of two threshold policies and stick to it; report both:

  - **A) Single global conf threshold** (e.g. `conf=0.40`): keep all classes
    on the same threshold for simplicity. Tune on the validation set to
    minimize total FP+FN. Acceptance: ≥90% recall on real cubes AND zero
    detections on every named distractor.
  - **B) Per-class conf thresholds** (recommended): use the natural separation
    in the M4b conf distributions. Suggested starting points:
      - `blue_cube`: 0.45 (real cube 0.97–0.99, package FP 0.83–0.88)
      - `green_cube`: 0.50 (real cube 0.26–0.41, soil bag FP 0.65–0.78) — note
        this kills real green recall too; the fine-tune is what fixes this
      - `red_cube`: 0.45 (real cube 0.68–0.82, chair FP 0.31–0.39)
    Per-class thresholds are a deployability concession, not a substitute
    for training; report the underlying model metrics at conf=0.25 so the
    effect of the fine-tune is visible without thresholding.

### 2.3 Validation set used to claim acceptance

- **JetRover-room hard-negative set (NEW, required):** 60 captured frames in
  the JetRover room, of which 30 contain exactly one of each real cube
  (arranged at the M6 20/40/60/80 cm distance bands per `docs/evaluation.md`)
  and 30 are "distractor-only" frames captured with the cubes removed but
  the soil bag, cardboard package, decal, and red chair still in frame.
  Frame size 640x360 JPG q=92, captured with the existing
  `scripts/capture_frames.py` (which already handles sidecar JSON + SHA-256
  integrity). Ground truth boxes will be hand-drawn and live alongside the
  frames in `evaluation/hardneg_validation/` (gitignored).
- **Empty-scene reference:** the 30 frames already captured at
  `evaluation/camera_samples/empty_2026-06-27/` (Phase A capture). Used as
  the no-cube false-positive floor.
- **Source-dataset reference (sanity):** the 9-image Roboflow validation
  split at `data/roboflow_det/.../valid/`. After fine-tuning, per-class
  mAP@0.5 on this set must remain ≥0.80 (was 0.954 before fine-tune;
  small drops are acceptable but the new model must not have forgotten
  the original Roboflow domain).

## 3. Dataset strategy

### 3.1 Composition

The fine-tune dataset is a **merge** of three sources, all in YOLOv5
detection format (5-field `class cx cy w h`, normalized 0–1):

| Source | Role | Approx. count | Notes |
|--------|------|---------------|-------|
| Roboflow `red-green-blue-cube-detection/1` (already normalized to `data/roboflow_det/`) | Positives + negatives (cubes on clean backgrounds) | 103 images | Already on disk; same source as M2. Keep all 90 train + 9 valid + 4 test. Class names already project-canonical. |
| JetRover-room cube frames (NEW) | Positives on the real camera, same domain as M4b | ~120 images | Capture 30 frames per distance band at 20/40/60/80 cm with one cube of each color in view, per `docs/evaluation.md`. Hand-label only the real cubes (3 per frame). Frames live under `evaluation/camera_samples/cubes_<distance>cm_<date>/` (gitignored), labels live at `data/hardneg/labels/<frame>.txt`. |
| JetRover-room hard-negative frames (NEW) | Negatives: same room, same distractors, NO cubes | ~60 images | 30 from `evaluation/camera_samples/empty_2026-06-27/` (already captured) + 30 additional frames captured with the cubes removed but the soil bag, cardboard package, decal, and red chair still in place. **These images have NO `.txt` label files** — empty labels are intentional. The Ultralytics loader treats them as background-only training signal. |

Total: ~280 images. ~120 with real-cube labels, ~60 with no labels (hard
negatives), ~100 Roboflow positives. This is a small dataset, so the
fine-tune uses heavier augmentation and a low learning rate (see §6).

### 3.2 Why this composition

- **Roboflow positives stay in the mix.** The M2 model had mAP@0.5=0.954
  on the Roboflow validation set — that domain knowledge is valuable and
  must not be lost. Removing Roboflow risks degrading the original
  accuracy in exchange for a tiny gain on JetRover-room frames.
- **JetRover-room positives add the camera viewpoint/lighting/background.**
  The M2 training set used web-collected images of cubes on clean
  backgrounds; the JetRover depth camera has different white balance, low
  contrast, and a wood-laminate floor. ~120 frames at 4 distance bands
  covers the M6 evaluation bands the model needs to serve.
- **Hard-negative frames teach the model what is NOT a cube.** A soil bag
  or cardboard package is visually a saturated colored region; without
  negative examples, the model continues to treat color = cube. The
  empty-scene Phase A capture (30 frames) is the floor of this; we add
  ~30 more to ensure the model sees the distractor scene multiple times.
- **Empty-label files are the trick that does the heavy lifting.** A
  `train/images/foo.jpg` with no corresponding `train/labels/foo.txt`
  teaches YOLO that "this image contains zero of the three classes" —
  exactly the supervision signal we need for the soil bag / package /
  decal / chair distractors.

### 3.3 Labeling approach

- **JetRover-room cube frames:** hand-draw tight axis-aligned bounding
  boxes around each real cube (1 red + 1 green + 1 blue per frame at the
  M6 distance bands). Label files written in YOLOv5 detection format:
  `class cx cy w h` (normalized 0–1) with class indices
  0=blue_cube, 1=green_cube, 2=red_cube. Use the existing polygon→bbox
  helper pattern from `scripts/normalize_dataset.py` if any frame has
  irregular cube regions, but axis-aligned boxes are fine here.
- **Hard-negative frames:** NO label files. Empty `labels/` entries are
  intentional and standard for YOLO background-only training.
- **Recommended tool:** LabelImg (PyQt5, free) or the Roboflow web
  annotator. LabelImg produces YOLO format directly and is reproducible
  on the dev PC; no project credentials required.
- **Quality bar:** every label file reviewed by Maher before training
  starts. The hard-negative label is "empty" — that's a label too, and
  must be reviewed (don't accidentally include labels for cubes that
  happen to be in the distractor scene).

### 3.4 Minimum sample counts

For the new model to be useful on the JetRover room:

- ≥120 cube frames (30 per M6 distance band) — covers viewpoint variation.
- ≥60 hard-negative frames — covers the four named distractors in
  multiple positions/lighting conditions. The empty-scene Phase A set
  (30 frames) plus 30 additional cube-removed-but-distractors-present
  frames clears this bar.
- ≥100 Roboflow frames retained from the M2 training set — keeps the
  original domain. All 103 are already in the dataset.

Anything below these minimums is a fast experiment, not a fine-tune.

## 4. Hard-negative validation set definition

A separate **held-out** validation set (not used for training) is required
to claim acceptance against §2.1. It must be captured AFTER the fine-tune
plan is approved, with this exact composition:

  - 60 frames total
  - 30 cube-present: one cube of each color in view, at distance bands
    20/40/60/80 cm (15 frames per color across bands). Captured with
    `scripts/capture_frames.py --prefix hardneg_v`.
  - 30 cube-absent: same scene with cubes removed, soil bag/cardboard
    package/decal/chair still in frame. Captured with
    `scripts/capture_frames.py --prefix hardneg_neg`.
  - All frames 640x360 JPG q=92, sidecar JSON with SHA-256 + frame_id.
  - Gitignored under the existing `evaluation/camera_samples/` line in
    `.gitignore`.
  - Hand-labeled tight bboxes for the cube frames; empty `.txt` for the
    negative frames.

The 30-frame empty-scene set in
`evaluation/camera_samples/empty_2026-06-27/` is **not** the held-out
validation set — it doubles as a captured-once reference and as
candidate training-pool material, so it cannot serve both roles.

## 5. Labeling approach and minimum sample counts (summary)

| Action | Who | When | Output |
|--------|-----|------|--------|
| Approve M3c plan | Maher | Before implementing card | Approval in kanban thread |
| Capture 120 cube frames (4 distance bands × 30) | Maher places cubes, implementer runs `capture_frames.py` | One physical session | `evaluation/camera_samples/cubes_<distance>cm_<date>/` (gitignored) |
| Capture 30 additional distractor-only frames | Maher removes cubes, implementer runs `capture_frames.py --prefix hardneg_pool` | Same session | `evaluation/camera_samples/hardneg_pool_<date>/` (gitignored) |
| Hand-label 120 cube frames | Maher (with implementer assist) using LabelImg | Same session | `data/hardneg/labels/<frame>.txt` (gitignored) |
| Verify all frames with `scripts/verify_camera_samples.py` | Implementer | Same session | stdout verification report |
| Merge Roboflow + JetRover-room positives + hard-negatives into one YOLO dataset | Implementer | After labels are reviewed | `data/hardneg/data.yaml` pointing at `images/{train,val}` and `labels/{train,val}` (gitignored) |
| Capture 60-frame held-out validation set | Maher + implementer | After fine-tune model exists | `evaluation/hardneg_validation/` (gitignored) |

Minimum sample counts to call the plan executable:
  - ≥120 cube frames (cube-present training)
  - ≥60 hard-negative frames (cube-absent training)
  - ≥100 Roboflow positives (domain retention)
  - 60 held-out validation frames (acceptance claim)

Below these the fine-tune is a fast experiment and the implementer should
flag it as such in the kanban thread.

## 6. Training recipe (recommendation only; tuning belongs to the implementer)

Same YOLOv5s family, same dev PC (RTX 4070 Ti) as M2:

- Base weights: `models/best.pt` (continue training from the M2 artifact,
  not from COCO). Rationale: the M2 model already has the cube-class
  head trained; starting from it preserves the good detection rate and
  the fine-tune only adjusts the decision boundary on negatives.
- Dataset: merged `data/hardneg/data.yaml`.
- Epochs: 25 (lower than M2's 30 because we're fine-tuning, not
  training from scratch).
- Image size: 640.
- Batch size: 16.
- LR: 0.0005 (10× lower than M2's auto-LR ~0.00143, because we're
  fine-tuning and don't want to overwrite the M2 features).
- Optimizer: AdamW (auto).
- Scheduler: cosine with `close_mosaic=10`.
- Patience: 15 (no early stop expected).
- Augmentation: stronger than M2 — `mosaic=1.0, mixup=0.15,
  hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, degrees=10, translate=0.1,
  scale=0.5, fliplr=0.5`. Rationale: more aggressive augmentation
  increases the variety of synthesized hard negatives and helps the
  model generalize beyond the 60 captured hard-negative frames.
- Seed: 42.

Wall-time estimate: ~25–35 s on the 4070 Ti (similar to M2's 31 s, ~280
images at the same settings).

## 7. Export and deployment chain (unchanged from M3/M4a)

1. `yolo export model=models/best_hardneg.pt format=onnx imgsz=640
   opset=13 simplify=False dynamic=False` → `models/best_hardneg.onnx`
2. `scp models/best_hardneg.onnx jetrover:~/jetson_ws/`
3. `/usr/src/tensorrt/bin/trtexec --onnx=best_hardneg.onnx
   --saveEngine=best_hardneg.engine --fp16 --workspace=2048` →
   `models/best_hardneg.engine` on the Jetson.
4. `sha256sum` round-trip dev PC ↔ Jetson, same as M4a.
5. `models/README.md` gains a "M3c hard-negative artifact" section
   mirroring the M3/M4a sections (size, SHA-256, IO shapes, build
   command, smoke vs M4b numbers, known caveats).

## 8. Candidate vs replace decision

**Decision: produce `models/best_hardneg.pt` first. Do NOT replace
`models/best.pt` until the tester card approves the new model against
the §2.1 acceptance criteria.**

Rationale:
- `models/best.pt` is referenced by the M3 ONNX export, the M4a
  TensorRT engine, the M4b live-camera validation, and the M5 ROS
  node scaffolding (none of which have shipped yet, but they all
  assume the M4b artifact path). Replacing it without an approved
  replacement breaks the artifact trail.
- Keeping `models/best_hardneg.pt` as a separate artifact lets the
  implementer iterate on training hyperparameters without losing the
  M2 baseline. The downstream tester card compares both artifacts
  side-by-side on the §4 held-out validation set before any swap.
- Once the tester approves the new model, the implementer of that
  follow-up card atomically: (a) renames `models/best.pt` →
  `models/best_m2.pt` (archival), (b) renames `models/best_hardneg.pt`
  → `models/best.pt`, (c) re-exports ONNX + engine under the new
  `best` name, (d) updates `models/README.md` accordingly. This
  swap is documented in the LOGBOOK and `.cursorrules` Current Status
  at the time of the swap.

## 9. M5 is paused

The M5 (live ROS 2 cube detection node) card remains **blocked** until
the fine-tune model passes the §2.1 acceptance criteria. This is a
scope correction, not a regression — the M4b card's "fine-tune on
JetRover-room images" recommendation is now promoted to a hard gate.

If Maher decides the fine-tune is too costly for the project's time
budget, the explicit alternative is to **kill the M5 live-ROS work**
and document the project as "inference pipeline validated on saved
frames only", rather than ship an ROS node that publishes color-driven
false positives. A conf-threshold-only mitigation does not satisfy
the §2.1 zero-FP-on-named-distractors criterion because the green soil
bag (conf 0.65–0.78) fires above the real green cube (conf 0.26–0.41).

## 10. Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Fine-tune over-fits to the 60 captured hard-negative frames | New model fires on novel distractors outside the captured set | Keep augmentation aggressive; include Roboflow positives; validate on the 60-frame held-out set, not the training set |
| Real green cube recall drops (was already low at conf 0.26–0.41 in M4b) | M6 evaluation finds green recall < 50% | Use per-class thresholds (§2.2 option B); include 30 cube frames per distance band so the model sees green from multiple viewpoints |
| Polygonal labels are not provided for the JetRover-room frames (axis-aligned only) | Looser bbox on cubes that are partially occluded or at extreme angles | Acceptable for cube detection (cubes are roughly square); document this in the LOGBOOK |
| Adding hard-negatives shifts the score distribution and changes which threshold is "right" | Old `conf=0.25` no longer meaningful | Re-tune thresholds on the held-out validation set; report both 0.25 and per-class-tuned numbers |
| Hand-labeling 120 frames takes ~2 hours | Schedule slip | Reuse the labels already on the 30 M4b cube frames (which are visible in `evaluation/m4b_predictions/`); only need to label 90 more if M4b frames are re-included. Alternative: skip the M4b re-use and label all 120 fresh. |
| Empty-label files accidentally contain a stray positive | Training signal is wrong; model still fires on the distractor | Implementer must `find data/hardneg/labels -name "*.txt" -size +0` to confirm the empty-label directory is genuinely empty |
| Replacing `models/best.pt` silently breaks M5 dependencies | Downstream M5 card starts building against a new artifact without knowing | The §8 rename protocol + LOGBOOK entry + `.cursorrules` Current Status update ensure downstream sees the swap |

## 11. Open questions for Maher before the implementing card starts

  1. **Approval to proceed:** do you approve the §3 composition
     (Roboflow positives + JetRover-room cube positives + 60 hard
     negatives + 60 held-out validation) for the fine-tune?
  2. **Time budget:** the implementer estimates ~3 hours of focused
     work — 30 min to capture 120 cube frames, 30 min to capture 30
     additional hard-negatives, 60–90 min to label, 30 min to train
     + export + engine build + smoke test. Acceptable?
  3. **Labeling tool:** LabelImg (local, free, reproducible) or do
     you have a Roboflow account you want to use?
  4. **Held-out validation set capture:** do you want the 60-frame
     held-out set captured in the same physical session as the
     training set (recommended) or separately?
  5. **Per-class vs single threshold:** do you accept the per-class
     threshold approach in §2.2 option B as the deploy default, or
     do you require a single global threshold?

## 12. References

- M4b report: `evaluation/m4b_predictions/report.md`
- M4b detections: `evaluation/m4b_predictions/detections.json`
- M4b annotated PNGs: `evaluation/m4b_predictions/m4b_*.png` (30 files)
- M4b LOGBOOK entry: `docs/LOGBOOK.md` 2026-06-27 M4b section
- M2 training context: `models/README.md`, `docs/LOGBOOK.md` 2026-06-24
  M2 training entry
- Roboflow dataset: <https://universe.roboflow.com/jakub-lof/red-green-blue-cube-detection/dataset/1>
- Capture harness: `scripts/capture_frames.py`
- Verification harness: `scripts/verify_camera_samples.py`
- Dataset normalization helper: `scripts/normalize_dataset.py`
- M4b inference harness: `scripts/test_inference.py`
- Original JetRover camera topic: `/depth_cam/rgb/image_raw`,
  `depth_cam_color_optical_frame`, ~25–30 Hz

---

Card status: research/planning complete. Implementation pending Maher's
approval of the §3 composition and §11 open questions. M5 is paused.