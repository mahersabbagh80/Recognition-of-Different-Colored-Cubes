# M3d-revived — Minimum positive-detection fine-tune plan for M5 PARTIAL

Date: 2026-06-28
Card: `t_afcaa4a5` (M3d-revived planner; implementation goes to a new
implementer card, not this one)
Parent: `t_a2a113b6` (M4c1 review approval) + `t_4fcd206e` (M4c1 geometry filter)
Predecessor docs: `docs/archive/model-hard-negative-plan.md` (M3c — hard-negative
plan), `docs/archive/model-alternative-research.md` (M3c2 — alternatives research),
`docs/archive/model-objectness-addendum.md` (M3c3 — cube-objectness addendum).
Scope: research/planning only. No training, no exports, no model artifacts.

---

## 0. TL;DR

The M5 acceptance gate is **PARTIAL** because the M2 `best.engine`
(Roboflow v1 fine-tune, 103 close-up images) does not fire on real
JetRover-room cubes at conf≥0.50 — see `evaluation/m5_live/report.md`
§3 and §12.7. The geometry post-filter (M4c1) is doing its job and
correctly rejects floor texture; it cannot fix a model that doesn't
fire on the target class in the first place. The M5c2 diagnostic at
conf=0.25 confirms this is a model issue (KEEP=2/439, only `green_cube`,
red and blue still zero). This card's scope is therefore **positive
detection on real JetRover-room cubes at the JetRover distance / angle /
scale**, not hard-negative rejection (which M4c1 already solves) and not
classical CV (out of scope per `.cursorrules`).

**Recommendation: minimum fine-tune = add 80 Maher-captured JetRover-room
RGB frames (1R+1G+1B in view, at the M6 20/40/60/80 cm distance bands
plus some scene-variation shots) to the existing Roboflow positives, and
continue training `models/best.pt` for 30 epochs at lr0=0.0005.** No
hard-negative capture needed (M4c1 handles it); no class-set extension
needed (the spec is r/g/b only); no architecture swap (the M3c2
alternatives research already rejected open-vocab and other backbones on
Orin Nano latency grounds).

Expected outcome after this fine-tune:
- M5 cubes-in-frame KEEP goes from 0/460 (M5c2 conf=0.50) to ≥3 with
  3 classes at conf=0.50, on the same JetRower-room physical scene.
- M4c1 V3+V4 regressions remain green (KEEP=0 on bottle/cup/carton/
  tall_cyl/empty) because the geometry filter is unchanged.
- Roboflow val mAP@0.5 stays ≥0.80 (no forgetting).

If even this minimum fails, the next step is dataset expansion (not a
hyperparameter sweep) — see §6 decision tree.

---

## 1. Why the M2 model fails — what M3d-revived is and is not

### 1.1 What's actually wrong

From `evaluation/m5_live/report.md` §11 and §12:

- **M5c sticker-on** (1R+1G+1B cubes, ~60-80 cm, downward camera, q=92
  JPG, 26.67 s bag): KEEP=0/414 at conf=0.50, all 41,700 rejects are
  `flat` (YOLO bbox depth ≈ floor depth → not raised → rejected by
  geometry filter).
- **M5c2 sticker-off** (same scene, dimming sticker removed, brightness
  delta +0.82/255 within noise — falsifies the "sticker was dimming"
  hypothesis): KEEP=0/460 at conf=0.50, identical pattern. 514,364 `flat`
  + 17,815 `aspect` rejects over 29 s.
- **M5c2 conf=0.25 diagnostic**: KEEP=2/439, only `green_cube` fires
  (2 frames), red and blue still at zero. Same scene, same filter, lower
  conf.

The geometry filter is correctly identifying that YOLO candidate bboxes
land on the floor texture rather than on the cubes — the model genuinely
does not fire on the real JetRover-room cubes at conf=0.50. This is a
**model-accuracy** issue, not a pipeline issue.

### 1.2 Why the source dataset doesn't cover this view

The M2 training data is `jakub-slof/red-green-blue-cube-detection` v1
(Roboflow Universe, 103 images, CC BY 4.0). Per `models/README.md` and
the M2 LOGBOOK entry, it is **web-collected close-up cube photography**
(top-down, ~10-30 cm distance, controlled lighting, clean backgrounds,
40-60 mm wooden cubes). The per-class mAP@0.5 on Roboflow valid is
0.954, but the JetRover capture is a **downward camera at ~60-80 cm
distance**, producing:

- A much smaller cube face in the 640×360 frame (face ~50-80 px instead
  of ~300 px). YOLOv5s anchors were sized for the original training
  scale; small faces yield lower confidence scores.
- Wood-laminate floor + natural room lighting + auto-exposure from the
  Orbbec driver (not the studio lighting the Roboflow images had).
- A 3D-raised object on a textured background — the Roboflow images
  used isolated cubes on neutral backgrounds.

The transfer gap is real and quantifiable: the model fires on the
JetRover-room images, but at confidences that put them below the 0.50
acceptance threshold. The conf=0.25 diagnostic (green only) tells us
the **gap is per-class non-uniform**: green gets the highest scores
(probably because the M2 training set had the strongest green signal),
red is borderline, blue's highest scores in this scene are below 0.25.
The new fine-tune must teach all three classes to fire above 0.50 on
real JetRover-room images.

### 1.3 What M3d-revived is NOT

- **Not a hard-negative plan.** M4c1 (the depth/geometry post-filter)
  already eliminates the four named M4b flat distractors
  (soil bag, cardboard package, decal, chair) at 0/30/30/30 KEEP on the
  V3+V4 validation set. The M3c hard-negative plan
  (`docs/archive/model-hard-negative-plan.md`) is therefore obsolete as the
  primary path; it remains the fallback if M3d-revived leaves residual
  FPs that the geometry filter cannot handle.
- **Not a class-set extension.** No `cube_other`, no yellow/orange
  class. The project spec is r/g/b only.
- **Not an architecture swap.** The YOLOv5s + TensorRT FP16 + ROS 2
  pipeline is the vendor-aligned, validated artifact path
  (see `docs/architecture.md`, `docs/technical-stack.md`,
  `docs/archive/model-alternative-research.md` §3 option C — open-vocab
  detectors are 5-25× slower on Orin Nano and rejected).
- **Not a conf-threshold lowering.** The §11.7 diagnostic already
  confirmed that conf=0.25 unlocks only one of three classes.
  Lowering further would push false positives up while leaving two
  classes dead.

---

## 2. Image capture specification (Maher's session)

### 2.1 How many images and why

**80 new JetRover-room RGB frames** (1R+1G+1B in view, varied
conditions). This is the minimum that gives the fine-tune enough
viewpoint variation to teach all three classes to fire at conf≥0.50.

Why 80:
- The M4b 30-frame set showed per-class confidence on real cubes
  was already weak (green mean 0.567, blue mean 0.731, red mean 0.708);
  the M5c2 conf=0.25 diagnostic showed the model *partially* responds
  on green only. Each class needs ≥20 in-view examples at the target
  distance/angle to nudge the per-class confidence up by ~0.10-0.20
  (the empirical gap from current conf to the 0.50 bar). 80 frames ×
  3 cubes per frame = 240 class-instances, ≥20 effective examples per
  class per distance band × 4 bands.
- The M3c hard-negative plan called for 120 cube frames; we are
  cutting that to 80 because (a) the geometry filter already handles
  the named distractors, so we don't need the hard-negative mass, and
  (b) the Roboflow positives still give the model the domain retention
  it needs (see §3).
- 80 frames in one Maher physical session is ~30 min of placement +
  capture (4 distance bands × ~15 min, or one ~30 min varied session);
  much more would exceed the project's 1-week time budget for what is
  still a learning robotics project.

### 2.2 Frame composition (Maher places cubes; implementer runs the capture script)

For each captured frame, **exactly 1 red, 1 green, and 1 blue cube** must
be in view. Place them anywhere in the bottom half of the frame so they
are visible from the downward camera; do not stack. Avoid overlaps of
more than 10% of bbox area between the three cubes. Empty `.txt` label
files (no labels) are NOT allowed for these frames — every frame has
three labeled cubes.

Distribution:

| Bucket | Count | What changes |
|---|---:|---|
| Distance 20 cm (M6 band) | 12 | 3 cubes close, large face |
| Distance 40 cm (M6 band) | 12 | 3 cubes mid, typical demo view |
| Distance 60 cm (M6 band) | 12 | 3 cubes, similar to M5c/M5c2 scene |
| Distance 80 cm (M6 band) | 12 | 3 cubes, M5 acceptance-band edge |
| Lighting variation (4 frames) | 4 | Same 20-40 cm scene with room light on / off |
| Single-cube-in-view (9 frames) | 9 | One cube color at a time at 40 cm (3 red, 3 green, 3 blue) |
| Single-class partial occlusions (6 frames) | 6 | 1 cube fully + 1 cube half out-of-frame, mixed colors, 40 cm |
| Single-frame out-of-FOV distractors (4 frames) | 4 | Add 1-2 JetRover-room background objects already in the scene (e.g. paper, decal) WITHOUT cubes; **no cube labels but the file IS included with a partial-label** (see §2.3 below) |
| Edge angles (3 frames) | 3 | Move a cube to the corner of the frame (extreme pixel coords) at 40 cm |
| Replicates of M5c2 scene (8 frames) | 8 | Repeat the M5c/M5c2 layout (1R+1G+1B at ~60-80 cm, downward camera) — these become the direct acceptance regression set |

Total: 12+12+12+12+4+9+6+4+3+8 = **82 frames.** Round to 80 by trimming
the single-class partial occlusion bucket to 4 (still gives 12
occlusion instances across classes — enough to teach partial-view
robustness). Save them to:

- `evaluation/camera_samples/jetrover_positives_<DATE>/` (gitignored,
  reproducible from `scripts/capture_frames.py`)

### 2.3 The "with distractors but no cubes" frames

The 4 "out-of-FOV distractors" frames (§2.2 row 8) include the existing
JetRover-room background (gray cloth pile, papers, decal) but no cubes.
These are **half-labeled**: they get a single empty `.txt` file in the
training set (background-only signal) — same pattern as the M3c hard-
neg plan §3.1. The reason: keeping the model from forgetting what the
JetRover room looks like (the floor texture, the lighting) is part of
the transfer learning. 4 frames is enough for that signal without
becoming a hard-negative minefield.

### 2.4 Capture procedure (Jetson, 1 physical session)

```bash
# On the Jetson, with vendor bringup running (per .cursorrules):
ssh jetrover
source /opt/ros/humble/setup.bash
source ~/jetson_ws/install/setup.bash

# Pre-flight: verify camera is alive
ros2 topic hz /depth_cam/rgb/image_raw          # expect ~25-30 Hz

# Place the 3 cubes in the desired arrangement (Maher does this)
# Capture one prefix per bucket so the labels can be split cleanly:
mkdir -p /home/ubuntu/cube_camera_samples/jetrover_positives_2026-MM-DD
python3 ~/jetson_ws/src/Recognition-of-Different-Colored-Cubes/scripts/capture_frames.py \
    --topic /depth_cam/rgb/image_raw \
    --out-dir /home/ubuntu/cube_camera_samples/jetrover_positives_2026-MM-DD \
    --max-frames 12 --interval-s 1.0 --prefix dist20cm
# Maher rearranges cubes; repeat for dist40cm / dist60cm / dist80cm /
# lighting / singlecolor_R / singlecolor_G / singlecolor_B /
# occluded / nodistractors / edgeangle / replicates

# Then SHA-256 + sidecar JSON are written automatically by the script
# (the existing scripts/capture_frames.py is the right tool — it
# already handles JPG q=92 + per-frame SHA-256 + JSON sidecar).
```

Pull the directory back to the dev PC:

```bash
# On the dev PC
scp -r jetrover:/home/ubuntu/cube_camera_samples/jetrover_positives_2026-MM-DD \
        ~/maher_ws/src/Recognition-of-Different-Colored-Cubes/evaluation/camera_samples/
cd ~/maher_ws/src/Recognition-of-Different-Colored-Cubes
python3 scripts/verify_camera_samples.py \
        --input-dir evaluation/camera_samples/jetrover_positives_2026-MM-DD
# All 80 frames must pass SHA-256 + per-frame metadata consistency.
```

### 2.5 What NOT to include (and why)

- **No sticker-on variation.** The M5c2 brightness diagnostic
  (delta +0.82/255 within noise) falsifies the "sticker was dimming"
  hypothesis. Whether the sticker is on or off is irrelevant to the
  model output. Keep one configuration only.
- **No cube-shaped non-rgb toys.** The M3c3 addendum flagged cube-shaped
  wrong-color objects as the L4 residual (geometry cannot distinguish
  two cubes). That is out of scope for M3d-revived; it remains an open
  question for the project's larger scope (see `docs/archive/model-objectness-
  addendum.md` §5 step C4). If Maher happens to have such a toy in the
  scene, the frame can be included with the cube bboxes only — don't
  label the toy.
- **No synthetic flips / crops / rotations of the captured frames.**
  Augmentation belongs to the training pipeline (§4), not the data
  capture. Synthesizing "more data" from 30 frames would not add the
  viewpoint diversity the model is missing.
- **No unlabeled cube-present frames.** Every cube-present frame must
  carry three labels. Empty-label files are reserved for the
  background-only signal frames (§2.3, 4 of them).

---

## 3. Labeling and dataset construction

### 3.1 Tool: Roboflow web UI (Maher uses the free tier)

Maher signs in to <https://app.roboflow.com> with his account, creates a
new project, uploads the 80 frames (the existing 4 background-only
frames do NOT go to Roboflow — they go straight into the dataset as
empty-label files via `scripts/build_jetrover_positive_dataset.py`,
see §3.4), and labels each cube.

Per-image workflow in the Roboflow annotator:

1. Upload the 80 JPGs as a single batch to a new project.
2. For each image, draw a tight axis-aligned bbox around each of the
   three cubes. Use Roboflow's polygon tool with axis-aligned snaps or
   the rectangle tool — the output is identical. Hand-drawn is fine.
3. Set the class label on each box. Use the project-canonical names
   `blue_cube`, `green_cube`, `red_cube` exactly (Roboflow does NOT
   auto-rename). Do NOT use the source Roboflow names `bluecube`,
   `green cube`, `red cube` — they were specific to the Jakub-Slof
   dataset and the project policy is to keep the new dataset aligned
   with the existing `models/best.pt` class order.
4. Verify all 80 images are labeled and saved.
5. Generate a YOLOv5 PyTorch export (Roboflow's standard format). Pick
   "Pascal VOC" or "YOLOv5" format; **do NOT pick YOLOv8 segmentation**
   or any segmentation format — YOLOv5s detection cannot consume
   polygons directly. Roboflow writes a `data.yaml` with the names
   `blue_cube`, `green_cube`, `red_cube`; verify those names are
   unchanged.

Download the resulting zip to `data/roboflow/jetrover_positives_<DATE>/
` (gitignored, like the existing `data/roboflow/`).

### 3.2 Merge with the original Roboflow dataset

The existing normalized Roboflow positives at
`data/roboflow_det/red-green-blue-cube-detection-1-yolov5pytorch/` MUST
be retained. Per `docs/archive/model-hard-negative-plan.md` §3.2, the M2
model's 0.954 mAP@0.5 on Roboflow valid is valuable domain knowledge;
removing the original positives to "clean" the dataset risks losing
that knowledge for a tiny gain on JetRover-room frames.

The merged dataset lives at `data/jetrover_v2/` (new; gitignored like
the existing `data/hardneg/`). Composition:

| Source | Role | Count | Train / Val / Test |
|---|---|---:|---|
| Roboflow `data/roboflow_det/.../train/` | Domain retention | 90 | train |
| Roboflow `data/roboflow_det/.../valid/` | Audit + per-class mAP | 9 | **val (do not lose)** |
| Roboflow `data/roboflow_det/.../test/` | Audit + per-class mAP | 4 | **test (do not lose)** |
| New JetRover positives (this card) | Camera domain | 76 | train |
| New JetRover replicates of M5c2 scene | Direct regression | 8 | **val** (held out from training) |
| Background-only JetRover frames | Background signal | 4 | train (empty labels) |

Total: 90+76+4 = **170 train images, 9+8 = 17 val images, 4 test
images.** Train/val/test ratio ≈ 90/9/2%. The val/test imbalance is
deliberate: we want the 9-image Roboflow val set to remain untouched
as the domain-retention gate, and we add 8 JetRover-room held-out
frames as the M5 regression set. This is intentionally NOT 70/20/10 —
we are fine-tuning a small dataset, not training from scratch, and
the M4c/M5c2 evidence shows the failure mode is on a single scene.

**Do not lose the 9 Roboflow valid images.** They are the only one with
bbox accuracy data we have audit on from M2, and dropping them would
silently destroy the per-class mAP baseline. They are kept untouched
in the merged val split.

### 3.3 Class name normalization

The new Roboflow export must use the project-canonical class names
`blue_cube`, `green_cube`, `red_cube`. If Maher's web UI defaults to
the Roboflow-imported names, fix them in the annotator before
generating the export. If the export comes back with the wrong names
(Roboflow preserves user-set labels verbatim), re-run
`scripts/normalize_dataset.py` against the new export with the same
NAME_MAP (`bluecube → blue_cube`, `green cube → green_cube`, `red cube
→ red_cube`) — the existing script handles this with `--force`.

The final `data/jetrover_v2/data.yaml` MUST have:

```yaml
train: ../images/train
val: ../images/val
test: ../images/test
nc: 3
names: ['blue_cube', 'green_cube', 'red_cube']
```

### 3.4 Build script (`scripts/build_jetrover_positive_dataset.py`)

The existing `scripts/build_hardneg_dataset.py` is the right pattern
but it crops hard-negatives from a single static scene and uses the
old `cubes_2026-06-27_m4b` source. Write a new script
`scripts/build_jetrover_positive_dataset.py` that:

1. Walks `evaluation/camera_samples/jetrover_positives_<DATE>/` and
   matches each `dist{NN}cm_NNNN.jpg` / `singlecolor_*.jpg` /
   `occluded_*.jpg` / `edgeangle_*.jpg` / `replicates_NNNN.jpg` to the
   matching Roboflow-exported label file at
   `data/roboflow/jetrover_positives_<DATE>/train/labels/`. Copies both
   into `data/jetrover_v2/images/train/` and `data/jetrover_v2/labels/train/`
   (with prefix `jetrover_` to avoid filename collisions).
2. Walks the same directory for `nodistractors_*.jpg` files, writes
   empty `.txt` files, copies them into `data/jetrover_v2/images/train/`
   with prefix `nodistractors_`.
3. Walks the 8 `replicates_*.jpg` files specifically and copies them
   to `data/jetrover_v2/images/val/` and their labels to
   `data/jetrover_v2/labels/val/` — this is the M5 acceptance
   regression set.
4. Walks `data/roboflow_det/.../train/` and copies (with prefix
   `rf_`) into `data/jetrover_v2/images/train/` and matching labels
   into `data/jetrover_v2/labels/train/`.
5. Walks `data/roboflow_det/.../valid/` and copies (with prefix
   `rf_`) into `data/jetrover_v2/images/val/` and labels into
   `data/jetrover_v2/labels/val/`. **Do not skip.**
6. Walks `data/roboflow_det/.../test/` and copies (with prefix
   `rf_`) into `data/jetrover_v2/images/test/` and labels into
   `data/jetrover_v2/labels/test/`. **Do not skip.**
7. Writes `data/jetrover_v2/data.yaml` with the snippet above and a
   header comment listing the per-bucket counts.
8. Verifies: every `.jpg` in `images/train/` has a matching `.txt`
   in `labels/train/` (empty or non-empty). Same for val and test.
   A train image without a label is a bug; a val image without a
   label would also be a bug; raise an exception and abort.

The script must be re-runnable with `--force`. It should NOT modify
`models/best.pt`, `models/best_hardneg.pt`, or any vendor package.

### 3.5 Gitignore

The new dataset is large (170 train + 17 val + 4 test JPGs at q=92,
roughly 1-3 MB per frame → ~400 MB) and reproducible from the source
captures + the Roboflow export. Add to `.gitignore`:

```
# M3d-revived positive-detection dataset (regenerable from
# evaluation/camera_samples/jetrover_positives_<DATE>/ + Roboflow export)
data/jetrover_v2/
# Raw Roboflow export of the new captures (regenerable from Roboflow web UI)
data/roboflow/jetrover_positives_*/
```

---

## 4. Fine-tuning recipe

### 4.1 Base weights

Start from `models/best.pt` (M2 artifact, SHA-256
`bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04`),
NOT from `yolov5s.pt` (COCO) or `models/best_hardneg.pt` (M3c, which
was built against a same-scene training set and is biased to that one
view). Reasoning:

- `models/best.pt` is the M2 checkpoint already validated end-to-end
  through ONNX → TensorRT FP16 on the Jetson, with documented M2 val
  mAP@0.5 = 0.954 and M4b live-camera per-class behavior
  (blue 0.731 / green 0.567 / red 0.708 mean conf). The fine-tune is
  continuing that trajectory.
- `yolov5s.pt` (COCO) is a 30-epoch re-train from a 80-class pretrain
  that does not contain r/g/b cubes. We would lose the M2 features
  we already paid for.
- `models/best_hardneg.pt` (M3c) was a hard-negative corrective trained
  on `cubes_2026-06-27_m4b` + same-scene distractors — its training set
  had **the exact same transfer gap we are now trying to fix**. It is
  a frozen view of the failure mode, not a better starting point.

### 4.2 Output artifact

The new artifact is `models/best_v2.pt` — kept separate from
`models/best.pt` (preserved per the `.cursorrules` rollback discipline,
mirroring the M3c protocol in `docs/archive/model-hard-negative-plan.md` §8).
Promotion to `models/best.pt` happens only after a tester card confirms
the M5 acceptance bar (see §5.3).

### 4.3 Hyperparameters

| Hyperparameter | Value | Rationale |
|---|---:|---|
| Epochs | 30 | Lower than M2's 30-from-scratch; same count is appropriate for a fine-tune on a small dataset because the M2 features are already trained. The M3c plan used 25 — 30 gives one more pass on the val signal without risk of overfit (the dataset is still <200 imgs). |
| Image size | 640 | Match M2, M3, M4a — anchor/stride math is identical. |
| Batch size | 16 | Same as M2; RTX 4070 Ti has 12 GB. If VRAM is tight at 640 imgsz with full augmentation, drop to 12. |
| Optimizer | AdamW (auto) | Same as M2 / M3c. |
| lr0 | 0.0005 | 10× lower than M2's auto-LR (~0.00143). Fine-tuning standard. Avoids catastrophic forgetting of Roboflow features. Same as M3c. |
| lrf | 0.01 (cosine) | Default. Cosine annealing with `close_mosaic=10`. |
| Patience | 20 | No early stop expected at 30 epochs on this small dataset; the patience gives Ultralytics a chance to find the best checkpoint by val mAP. |
| Seed | 42 | Same as M2 / M3c; reproducibility. |
| Device | 0 (RTX 4070 Ti) | Per `.cursorrules`. |
| Workers | 8 | Same as M2 / M3c. |
| AMP | enabled | Same as M2 / M3c. |
| Mosaic | 1.0 | Default for YOLOv5 detection. |
| Mixup | 0.10 | Lower than M3c's 0.15 because we are fine-tuning, not teaching hard-negatives. |
| hsv_h | 0.015 | Same as M2 / M3c — YOLOv5 default. |
| hsv_s | 0.7 | Same as M2 / M3c. |
| hsv_v | 0.4 | Same as M2 / M3c. |
| degrees | 5 | Lower than M3c's 10 — the JetRover cubes are on a horizontal plane; aggressive rotation would synthesize unrealistic orientations. |
| translate | 0.1 | Same as M2 / M3c. |
| scale | 0.5 | Same as M2 / M3c — this is the augmentation that most directly addresses the "small face at 60-80 cm" gap. |
| fliplr | 0.5 | Same as M2 / M3c. |
| freeze | None | Do NOT freeze the backbone. The YOLOv5s backbone is small (9.1M params per `models/README.md`); freezing would prevent the fine-tune from adapting the lower-level features to the JetRover-room distance/lighting. The full-network fine-tune is what the M3c plan also used. |
| close_mosaic | 10 | Same as M2 / M3c. |
| plots | True | Same as M2 / M3c; per-class curves and confusion matrix are diagnostic. |
| save_period | -1 | Same as M2 / M3c; only save best + last. |
| cache | False | Same as M2 / M3c — cache=False keeps memory free for the augmentation. |

### 4.4 Exact training command

```bash
# On the dev PC, with the .venv-m2 venv active (torch 2.6.0+cu124 +
# ultralytics 8.4.75, per models/README.md "Known caveats" §6):
cd ~/maher_ws/src/Recognition-of-Different-Colored-Cubes
source .venv-m2/bin/activate
python scripts/finetune_jetrover_positives.py \
    --data data/jetrover_v2/data.yaml \
    --base models/best.pt \
    --out  models/best_v2.pt \
    --epochs 30 --batch 16 --imgsz 640 --lr0 0.0005 \
    --device 0 --name jetrover_v2_30ep \
    --patience 20
```

The new `scripts/finetune_jetrover_positives.py` mirrors
`scripts/finetune_hardneg.py` (already exists, 107 lines), with:

- Default `--data data/jetrover_v2/data.yaml`, `--base models/best.pt`,
  `--out models/best_v2.pt`, `--name jetrover_v2_30ep`.
- The hyperparameters from §4.3 passed explicitly to `model.train(...)`.
- Post-training: copy `runs/jetrover_v2/jetrover_v2_30ep/weights/best.pt`
  to `models/best_v2.pt`, print size + SHA-256, leave the existing
  `models/best.pt` untouched (rollback discipline).

Wall-time estimate on the RTX 4070 Ti: **~40-60 s** (170 train + 17 val
images at 640, batch 16, 30 epochs — slightly more than the M3c 49.8 s
because we have more train images; the Ultralytics loader overhead
dominates).

### 4.5 Expected per-class behavior after fine-tune

Predictions from the M5c2 diagnostic, with the M2 model baseline:

| Class | M2 mean conf (M4b, 30-frame live) | M5c2 conf=0.25 result | Expected post-M3d-revived |
|---|---:|---|---|
| `blue_cube` | 0.731 (range 0.252-0.988) | KEEP=0 at conf=0.25 (0 detections) | mean conf on JetRover scene ≥0.55; ≥1 detection per 60-80 cm frame at conf≥0.50 |
| `green_cube` | 0.567 (range 0.257-0.783) | KEEP=2/439 at conf=0.25 (the partial response) | mean conf on JetRover scene ≥0.65; ≥1 detection per 60-80 cm frame at conf≥0.50 |
| `red_cube` | 0.708 (range 0.306-0.822) | KEEP=0 at conf=0.25 (0 detections) | mean conf on JetRover scene ≥0.55; ≥1 detection per 60-80 cm frame at conf≥0.50 |

The class-by-class expected behavior is:
- **green_cube** is the easiest. The M5c2 conf=0.25 diagnostic already
  shows the model partially responds; the new JetRover frames will push
  the conf above 0.50 reliably. Expected mAP@0.5 on Roboflow valid
  stays ≥0.80 (M2 was 0.885 — fine-tuning generally shifts the curve
  by ≤5 pp).
- **red_cube** and **blue_cube** are the gaps. The M5c2 conf=0.25
  diagnostic shows the model does NOT fire on them at conf=0.25 — they
  are below the model's existing decision boundary at this scene. The
  new frames directly target this gap. Expected per-class mAP@0.5 on
  the M5c2-replicates validation split: ≥0.70 each (the val split is
  tiny at 8 frames, so the bar is forgiving).
- **WHY this class pattern:** the Roboflow training set was dominated
  by one cube class's pose variation per image; the M2 model learned
  per-class features unevenly. The M3d-revived training set adds ~20
  examples per class at the JetRover distance/angle, which is the
  empirical minimum for fine-tuning to nudge the per-class decision
  boundary above the 0.50 threshold.

---

## 5. Re-export and re-validate path

### 5.1 Re-export chain (PyTorch → ONNX → TensorRT FP16)

Same recipes as the M3 / M4a cards; no flags change.

```bash
# 1. ONNX export (dev PC, .venv-m2 active):
cd ~/maher_ws/src/Recognition-of-Different-Colored-Cubes
source .venv-m2/bin/activate
yolo export model=models/best_v2.pt format=onnx imgsz=640 opset=13 \
    simplify=False dynamic=False
# produces models/best_v2.onnx (35.0 MB; matches M3 §3 layout)

# 2. ONNX sanity check:
.venv-m2/bin/python - <<'PY'
import onnx
m = onnx.load("models/best_v2.onnx")
onnx.checker.check_model(m)
print("checker OK")
print("ir_version:", m.ir_version)
PY

# 3. Copy ONNX to Jetson and build TensorRT FP16 engine:
scp models/best_v2.onnx jetrover:~/jetson_ws/best_v2.onnx
ssh jetrover "/usr/src/tensorrt/bin/trtexec \
    --onnx=best_v2.onnx --saveEngine=best_v2.engine \
    --fp16 --workspace=2048"
# ~14 min build (Orin Nano, TensorRT 8.6.2, same as M4a)

# 4. Pull engine back to dev PC + SHA-256 round-trip:
scp jetrover:~/jetson_ws/best_v2.engine models/best_v2.engine
sha256sum models/best_v2.engine   # record for the LOGBOOK
```

### 5.2 Smoke inference (the ORT parity check, dev PC)

```bash
source .venv-m2/bin/activate
python scripts/m3_smoke_inference.py \
    --model models/best_v2.onnx \
    --image data/roboflow_det/red-green-blue-cube-detection-1-yolov5pytorch/valid/images/<smoke>.jpg \
    --imgsz 640 --conf 0.25 --iou 0.45 --topk 5
```

Expected: 3-7 detections, classes {blue_cube, green_cube, red_cube},
confidences matching the M2 smoke check ±0.05 (small shifts are
expected from the fine-tune).

### 5.3 M4c1 regression (must pass before M5 acceptance)

Re-run the M4c1 V3+V4 protocol with `models/best_v2.engine` substituted
for `models/best.engine`. The geometry filter parameters stay unchanged
(M4c1 v2-only: `raised_mm=30`, `min_raised_frac=0.20`,
`max_planar_top_stddev_mm=30`, `max_ratio=1.2`, `inset_px=1`,
`annulus_outer_px=15`, `n_min=30`).

Expected outcomes:

| Test set | Expected KEEP | Source |
|---|---:|---|
| Bottle (M4c1 V3) | 0 | `evaluation/m4c_geometry_filter/yolo_detections_bottle.json` |
| Cup (M4c1 V3) | 0 | `evaluation/m4c_geometry_filter/yolo_detections_cup.json` |
| Carton (M4c1 V3) | 0 | `evaluation/m4c_geometry_filter/yolo_detections_carton.json` |
| Tall cylinder (M4c1 V3) | 0 | `evaluation/m4c_geometry_filter/yolo_detections_tall_cyl.json` |
| Empty scene (M4c1 V4) | 0 | `evaluation/m4c_geometry_filter/yolo_detections_empty.json` |
| Cubes V1 — blue cube (M4c1 V1, ~25 frames) | ≥18/25 KEEP | `evaluation/m4c_geometry_filter/yolo_detections_cubes.json` (the M4c1 V1 was 22/29 blue; should not regress) |

The V1 (real cubes) acceptance is the one to watch — if the geometry
filter over-rejects after the fine-tune, that's a regression. The
existing cubes-depth-2026-06-27 30-pair sync set is the regression
benchmark (see `evaluation/m4c_geometry_filter/filter_results_cubes.json`).

### 5.4 M5 acceptance (the live evidence bar)

After the M4c1 regression passes, run the M5 acceptance flow on the
Jetson with `models/best_v2.engine` substituted into
`config/params.yaml`'s `model_path`. Exact same recipe as
`evaluation/m5_live/report.md` §4.3, just pointing at the new engine.

Acceptance bar for M5 PARTIAL → PASS:

| Bag | Acceptance criterion | Source |
|---|---|---|
| Empty scene (≥25 s, same scene as M5b) | **KEEP=0** at conf≥0.50 | mirrors M5b |
| Cubes-in-frame (≥25 s, same scene as M5c/M5c2 — 1R+1G+1B at ~60-80 cm, downward camera) | **KEEP ≥3 with 3 classes** (≥1 each red, green, blue) at conf≥0.50 | mirrors M5c/M5c2; this is the bar the new fine-tune must clear |

The "3 classes" sub-criterion is per `docs/architecture.md` §1 + the
project spec (`docs/project-definition.md` §Classes). Each class having
≥1 KEEP in the bag proves the model fires on all three at the JetRover
scene. M5c2 had 0/0/0/2 at conf=0.25 — green only — and M3d-revived
is expected to flip this to 3-class / ≥1 each.

### 5.5 Acceptance gate (M5 PARTIAL → PASS requires ALL of)

1. M5c2-style empty scene: KEEP=0 at conf≥0.50. ✅ already passed by
   M4c1 — must remain true.
2. M4c1 V3 (bottle/cup/carton/tall_cyl) live re-run: KEEP=0 on each.
   The geometry filter is unchanged, but the new YOLO might shift
   scores on edge cases.
3. M4c1 V4 (empty scene) live re-run: KEEP=0.
4. M5c2-style cubes-in-frame: KEEP ≥3 with 3 classes at conf≥0.50.
   This is the criterion M5 PARTIAL fails today; this is the criterion
   M3d-revived flips.
5. Roboflow val mAP@0.5 ≥0.80 (no catastrophic forgetting on the
   original 9-image val set).
6. Per-class mean conf on the 8-frame JetRover-room held-out val
   split (`replicates_*.jpg`): blue ≥0.55, green ≥0.65, red ≥0.55.

If any of (1)-(4) fails, the new model is REJECTED and
`models/best.pt` stays as the production engine (the M5 PARTIAL
verdict remains, but the geometry filter still prevents colored
non-cube FPs).

---

## 6. Risk assessment and decision tree

### 6.1 Risk register

| Risk | Probability | Impact | Detection | Mitigation |
|---|---|---|---|---|
| Fine-tune over-fits to the 80 captured frames; loses M2 features on out-of-distribution views | Medium | High | Roboflow val mAP@0.5 drops below 0.80 | Lower lr0 (0.0003); keep Roboflow positives in train split; consider freezing backbone for first 10 epochs in a follow-up experiment |
| Per-class imbalance: red and blue still at zero because the new frames don't shift the decision boundary enough | Medium | High | M5 acceptance KEEP still has 0 red or 0 blue at conf≥0.50 | Add another 40 JetRover frames focused on red+blue; use stronger augmentation (`scale=0.7`); consider training with `mosaic=0` after epoch 15 to focus on individual cube views |
| Class name normalization error (Roboflow preserves old `bluecube`/`green cube`/`red cube` names) | Low | Medium (silent at training, crash at inference if class IDs shift) | `data/jetrover_v2/data.yaml` shows wrong names; model.names would be different | Re-run `scripts/normalize_dataset.py` against the new export with `--force`; verify `data.yaml` after build script runs |
| Catastrophic forgetting on Roboflow positives (per-class P/R drop) | Low | High | Roboflow val mAP@0.5 < 0.80; the 9-image val is small so the noise is real | Keep lr0 at 0.0005 (not higher); keep Roboflow positives in train split; verify per-class mAP after training |
| Empty-label file accidentally contains cube labels | Low | High (model learns to KEEP distractors as cubes) | Hash check: `find data/jetrover_v2/labels -size +0` should show 0 results in the background-only paths | The build script (`build_jetrover_positive_dataset.py`) explicitly writes empty `.txt` for the 4 background-only frames and asserts that all train images have labels |
| V1 (real cube V1 in M4c1) regression — the geometry filter over-rejects after fine-tune because YOLO bboxes shift | Low | Medium | V1 KEEP count drops below 18/25 blue | Re-run `m4c_geometry_filter.py` against the same `cubes_depth_2026-06-27` frames; if KEEP drops, raise `max_ratio` from 1.2 to 1.3 or widen `annulus_outer_px` (these are M4c1 parameters — defer to the tester card before changing) |
| Sticker-removal hypothesis re-emerges (model still doesn't fire because of a real optical issue) | Very low (M5c2 falsified the hypothesis with brightness delta +0.82/255) | Medium | M5 acceptance fails with same zero-KEEP pattern | Verify the M5c2 brightness diagnostic on the new captures (`peek_rgb_pre_launch.png` mean luminance comparable to M5c2's 133.31 ± 2) |
| Maher capture session produces fewer than 80 frames (capture stalls mid-session) | Low | Medium | `verify_camera_samples.py` reports <80 frames | Re-run capture script with the remaining buckets; ≥60 frames is still usable (the recipe assumes 80 as the target but does not hard-require it — minimum 60 to keep the per-class ≥20 example target) |

### 6.2 Rollback

`models/best.pt` SHA-256 `bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04`
is preserved unchanged throughout. The new model goes to
`models/best_v2.pt`. If the M5 acceptance gate fails after promotion,
the implementer:

1. Re-points `config/params.yaml` `model_path` back to `models/best.pt`.
2. Re-runs the M5 acceptance flow as a regression check (it should
   return to the M5 PARTIAL state — empty KEEP=0, cubes KEEP=0 at
   conf=0.50 — same as today).
3. Logs the rollback to `docs/LOGBOOK.md`.

Promotion to `models/best.pt` happens ONLY after the tester card
approves the M5 PARTIAL → PASS flip. The rename protocol is the same
as the M3c plan §8: (a) `best.pt` → `best_m2_v1.pt` (archive), (b)
`best_v2.pt` → `best.pt`, (c) re-export ONNX + engine under the new
`best` name, (d) update `models/README.md` accordingly. This swap is
logged to the LOGBOOK and `.cursorrules` Current Status at the time
of the swap.

### 6.3 Time budget (calendar estimate)

| Step | Who | Duration | Blocking on |
|---|---|---:|---|
| Plan approval (`t_afcaa4a5` → tester + Maher) | Maher + reviewer | 1 day | — |
| `scripts/build_jetrover_positive_dataset.py` written + tested | Implementer | 1-2 h | Plan approval |
| Maher physical capture session (80 frames) | Maher | ~30 min | Plan approval + script |
| Roboflow upload + label + export | Maher | 1-2 h | Capture session |
| Build merged dataset | Implementer | 5 min | Roboflow export |
| Fine-tune run (RTX 4070 Ti) | Implementer | ~1 min wall time | Merged dataset |
| ONNX export + checker | Implementer | 2 min | Fine-tune |
| scp ONNX + trtexec engine build on Jetson | Implementer | 15 min wall time | ONNX export |
| M4c1 regression on Jetson | Implementer | 30 min | Engine build |
| M5 acceptance bags (empty + cubes) | Implementer + Maher | 30 min (physical) | Engine build + Maher availability |
| Analyze + report + LOGBOOK entry | Implementer | 30 min | M5 bags |

Calendar estimate from approval: **3-4 working days** with one Maher
physical session at the start and one at the end. Most of the
calendar is human latency, not compute.

### 6.4 Decision tree for Maher

The card body requires explicit decision branches. Each is honest
about what it costs and what it gains:

**Branch A — Skip new data capture; lower conf to 0.25 in production.**

Cost:
- More false positives on colored non-cubes that the geometry filter
  still rejects. From the M5c2 conf=0.25 bag: 974,170 `flat` rejects
  + 178,973 `aspect` rejects + 49 other — 99.99% of conf=0.25
  candidates get rejected by the geometry filter anyway. Per-class
  recall on the real cubes still 0 red / 2 green / 0 blue (from
  M5c2 conf=0.25 result). The bar "≥1 of each class at conf=0.50" is
  not met.
- Latency: same (the geometry filter runs after YOLO regardless of
  conf). Negligible difference.
- Two classes still dead: red and blue still emit zero candidates at
  conf=0.25. This is the empirical answer from M5c2 — the model
  genuinely does not fire on them in this scene.

Verdict: **Reject.** This branch does not satisfy the M5 acceptance
criterion (3 classes at conf=0.50). The M5 PARTIAL verdict stays
PARTIAL, with the additional cost that we're shipping a system that
emits boxes only on green cubes at one out of three classes.

**Branch B — Minimum fine-tune (80 positives, this card).**

Cost:
- ~3-4 calendar days of work + one Maher physical session.
- Risk of per-class imbalance (see §6.1 risk register) — red and blue
  may need a second capture round if the first 80 frames don't shift
  the per-class decision boundary enough.
- New model artifact (`best_v2.pt`) sits as a candidate until tester
  approves.

Gain:
- Expected: M5 PARTIAL → PASS with KEEP ≥3 (3 classes) at conf≥0.50
  on the JetRover-room scene.
- Roboflow val mAP@0.5 stays ≥0.80 (no forgetting).
- M4c1 regression preserved (the geometry filter is unchanged).

Verdict: **Recommended.** This is the cheapest path that actually
solves M5 PARTIAL within the project's 1-week time budget.

**Branch C — Proper fine-tune (80 positives + 50 hard-negatives from
JetRover room).**

Cost: Branch B + the M3c plan's hard-negative capture
(`docs/archive/model-hard-negative-plan.md` §4) — another Maher session for
60 frames (30 cube-absent + 30 cube-present with distractors), ~1 hour
of Maher time, and ~3 hours of implementer time. Total ~5-6 calendar
days.

Gain:
- Branch B's outcome plus explicit hard-negative training on the
  colored non-cube distractors that the geometry filter currently
  handles implicitly. The fine-tune would learn to reject the green
  soil bag / blue cardboard package / blue decal / red chair as
  negative features in the model itself, not just in the geometry
  filter.

Verdict: **Conditional fallback.** The geometry filter already handles
these distractors at 0/30/30/30 on the V3+V4 set, so explicit
hard-negative training buys a redundant safety net at the cost of
extra Maher time. Take this branch if Branch B fails the M5
acceptance — specifically, if the V3 distractor KEEP counts go above
zero with the new YOLO.

**Branch D — Do nothing; document M5 PARTIAL as the project end-state.**

Cost: 0 (no new work).

Gain: 0 (M5 remains PARTIAL; the project ships a recognition pipeline
that publishes correct empty-scene results but cannot detect cubes in
the actual demo scene).

Verdict: **Reject for the project's portfolio story.** M5 PARTIAL is a
degraded demo state — the pipeline detects colored non-cubes (via
geometry filter) but cannot detect cubes (via model). Documenting
that as the project end-state would mis-represent what was built.

### 6.5 Researcher's recommendation

**Branch B (this card).** The minimum fine-tune is the cheapest path
that actually solves M5 PARTIAL within the project's time budget, and
the M3c3 addendum's hybrid recommendation (geometry filter + conditional
fine-tune) explicitly anticipates this as the Phase 2 fallback. The
hard-negative work (Branch C) is no longer needed because the geometry
filter already handles the named M4b distractors.

If Branch B fails the M5 acceptance bar, escalate to Branch C (add the
hard-negatives) before considering Branch D. The Baranch D end-state
would mean the project portfolio documents a system that doesn't
deliver on its primary spec ("Recognize cubes on JetRover"), which is
not the project story this team is building.

---

## 7. Implementation handoff (for the implementer card)

This card is the planner. The implementer card receives the following
artifacts and actions in order:

### 7.1 Input artifacts (must exist before the implementer card starts)

- `docs/m3d-revived-plan.md` (this file).
- `evaluation/camera_samples/jetrover_positives_<DATE>/` with 80 RGB
  JPGs + matching `*_metadata.json` sidecar, SHA-256 verified.
- `data/roboflow/jetrover_positives_<DATE>/` with Roboflow export
  (80 frames labeled, YOLOv5 format, project-canonical class names).

### 7.2 Implementer actions (sequential)

1. Write `scripts/build_jetrover_positive_dataset.py` (per §3.4).
2. Run it with `--force` against the Roboflow export and the captured
   frames. Verify the train/val/test counts match §3.2 (170/17/4).
3. Add `data/jetrover_v2/` and `data/roboflow/jetrover_positives_*/`
   to `.gitignore`.
4. Write `scripts/finetune_jetrover_positives.py` (per §4.4).
5. Run the fine-tune with the §4.3 hyperparameters. Confirm
   `models/best_v2.pt` is created with size + SHA-256 logged.
6. Export ONNX (per §5.1 step 1-2). Verify `onnx.checker.check_model`
   passes.
7. scp ONNX to Jetson, run trtexec (per §5.1 step 3). Pull engine
   back. SHA-256 verify.
8. Run `scripts/m3_smoke_inference.py` against the new ONNX (per
   §5.2). Confirm the M2 smoke baseline is reproduced.
9. Run M4c1 regression on Jetson (per §5.3). Confirm V3+V4 KEEP=0
   and V1 cubes KEEP≥18/25.
10. Capture M5 acceptance bags (per §5.4). Confirm M5 PARTIAL → PASS
    (KEEP≥3 with 3 classes on cubes bag).
11. Do NOT rename `best.pt` yet — leave the swap for the tester card.
12. Log to `docs/LOGBOOK.md` (date, per-step outcomes, accept/reject
    rationale).

### 7.3 Implementer artifacts (must exist when the implementer card completes)

- `scripts/build_jetrover_positive_dataset.py` (new).
- `scripts/finetune_jetrover_positives.py` (new).
- `models/best_v2.pt`, `models/best_v2.onnx`, `models/best_v2.engine`
  (gitignored; size + SHA-256 in the LOGBOOK).
- `evaluation/m3d_predictions/` — per-frame JSON + annotated PNGs
  on the held-out 8-frame replicates set + on a sample of the
  M5c2 scene replayed with the new engine.
- `docs/LOGBOOK.md` entry with the per-step outcomes.

### 7.4 Out of scope for the implementer card

- Renaming `best_v2.pt` → `best.pt` (tester card only).
- Modifying any M4c1 geometry filter parameter.
- Modifying `models/best.pt`, `models/best_hardneg.pt`, vendor packages,
  or `start_app_node.service`.
- Lowering the production conf threshold as a substitute for the
  fine-tune (Branch A from §6.4 — rejected).
- Adding hard-negative frames (Branch C — only if Branch B fails the
  M5 acceptance).
- Architecture swap, open-vocab detector, or any deviation from the
  vendor-aligned YOLOv5s + TensorRT FP16 pipeline.

---

## 8. References

### 8.1 Internal

- `docs/archive/model-hard-negative-plan.md` — predecessor hard-negative plan
  (M3c); now obsolete as primary path, remains the fallback if M3d
  leaves residual FPs.
- `docs/archive/model-alternative-research.md` — M3c2 alternatives research;
  recommends depth/geometry filter as primary, M3c as fallback. M3d-
  revived is the M3c fallback, now scoped to positive detection.
- `docs/archive/model-objectness-addendum.md` — M3c3 cube-objectness addendum;
  the hybrid Phase 1 (geometry filter) + Phase 2 (conditional
  fine-tune) architecture M3d-revived executes.
- `docs/milestones.md` — M5 status (PARTIAL 2026-06-28), M4b/M4c1
  results.
- `docs/evaluation.md` — 50-frame test protocol (placeholder; M6 not
  yet executed).
- `docs/architecture.md` — vendor-aligned pipeline; the TensorRT
  engine path M3d-revived does not change.
- `docs/project-definition.md` — success criteria (≥80% color
  classification on 50 frames, ≥5 fps, 20-80 cm distance); M3d-revived
  directly addresses the color classification criterion.
- `docs/LOGBOOK.md` — M2 training entry (2026-06-24), M3 export entry
  (2026-06-27), M4a/M4b/M4c/M4c1 entries (2026-06-27), M5 PARTIAL
  entries (2026-06-28).
- `models/README.md` — `models/best.pt` SHA-256, training recipe,
  known caveats (CUDA / TensorRT / trtexec path).
- `evaluation/m4b_predictions/report.md` and `detections.json` —
  30-frame FP evidence (the original hard-negative trigger).
- `evaluation/m4c_geometry_filter/report.md` — geometry filter
  validation; V3+V4 KEEP=0 evidence.
- `evaluation/m5_live/report.md` §3, §11, §12 — M5 PARTIAL evidence,
  M5c2 brightness diagnostic, decision tree resolved per §12.7.
- `scripts/capture_frames.py` — Jetson-side rclpy RGB frame saver
  with sidecar JSON + SHA-256 (existing; reuse for §2.4).
- `scripts/capture_rgb_depth_sync.py` — Jetson-side rclpy RGB+depth
  sync saver (existing; reuse if M5 acceptance needs depth frames).
- `scripts/build_hardneg_dataset.py` — pattern for the new
  `scripts/build_jetrover_positive_dataset.py` (existing; same
  shape, new contents).
- `scripts/finetune_hardneg.py` — pattern for the new
  `scripts/finetune_jetrover_positives.py` (existing; same shape, new
  defaults).
- `scripts/normalize_dataset.py` — class-name normalization for the
  new Roboflow export if needed (existing).
- `scripts/m3_smoke_inference.py` — ONNX smoke inference check
  (existing; reuse for §5.2).
- `scripts/m4c_geometry_filter.py` — M4c1 regression harness
  (existing; reuse for §5.3).
- `scripts/m5_capture_bag.py`, `scripts/m5_analyze_bag.py`,
  `scripts/m5_parse_latency.py` — M5 acceptance harness (existing;
  reuse for §5.4).

### 8.2 External

- Roboflow Universe (Jakub Slof red-green-blue-cube-detection v1):
  <https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1>
- Roboflow free-tier web annotator:
  <https://app.roboflow.com>
- Ultralytics YOLOv5 export to ONNX:
  <https://docs.ultralytics.com/modes/export/>
- Ultralytics YOLOv5 training hyperparameters (cosine LR, mosaic,
  mixup, hsv_*):
  <https://docs.ultralytics.com/usage/cfg/>
- TensorRT 8.6.2 trtexec reference (FP16, workspace):
  <https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-86/developer-guide/index.html#trtexec>
- Hiwonder JetRover depth camera topic reference
  (`/depth_cam/rgb/image_raw`):
  <https://docs.hiwonder.com/projects/JetRover/en/jetson-orin-nano/docs/7.Robot_Arm_Control_Course.html>

---

## 9. Open questions for Maher

1. **Approval to execute Branch B.** Confirm the §2 capture spec (80
   frames, 1R+1G+1B per frame, distance/angle/lighting distribution)
   and the §3.2 merged dataset composition (170 train + 17 val + 4
   test; 8 of the JetRover-room frames held out as the M5 acceptance
   regression set). Y/N.
2. **Roboflow project for the new captures.** Create a new Roboflow
   project (free tier is enough for 80 images) and label in there, or
   reuse an existing one. The class names MUST be `blue_cube`,
   `green_cube`, `red_cube` regardless. Y/N.
3. **Held-out validation set composition.** Confirm that 8 of the 80
   JetRover-room frames will be held out as the M5 acceptance
   regression set (replicates of the M5c2 scene), and that the 9
   Roboflow val images stay untouched in the val split. Y/N.
4. **Time budget.** Confirm the §6.3 calendar estimate (3-4 working
   days, one Maher physical session at the start, one at the end).
   Within the project's 1-week time budget? Y/N.
5. **If Branch B fails the M5 acceptance,** confirm Branch C (add the
   M3c hard-negatives — ~5-6 calendar days total) is the next step
   before Branch D (document M5 PARTIAL as the project end-state).
   Y/N.

---

Card status: research/planning complete. Implementation pending Maher's
approval of §2 capture spec + §3.2 dataset composition + §6.4 Branch B.
`models/best.pt` unchanged. `t_13b658c2` superseded by this card
for the positive-detection scope (the hard-negative scope remains the
conditional fallback if Branch B fails).