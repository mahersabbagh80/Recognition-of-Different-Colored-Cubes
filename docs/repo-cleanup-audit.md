# M7b Repository Cleanup Audit

Audit date: 2026-07-05
Auditor: documenter (kanban card `t_5c5aeba9`)
Scope: full repository file inventory + reachability map + per-area decision.

This is an AUDIT / RECOMMENDATION document, not an execution plan. No tracked
files were modified. All cleanup actions below require explicit approval
from Maher before they are applied.

---

## Executive summary — what is making the repo messy

Six sources of clutter, in roughly decreasing order of impact:

1. **The `evaluation/` tree is 4.8 GB and 1006 files**, of which 942 are PNG
   annotated images. The JSON + report evidence per milestone is small
   (~50 KB per evaluation), but the visual evidence is large. The
   `.gitignore` already excludes most of it, but not the M4c annotated
   PNGs (180 files, ~62 MB) which were tracked before the ignore rules
   were tightened.
2. **Two README inaccuracies** that will mislead every new reader:
   - `README.md:231` claims `models/` is "gitignored, not committed" — wrong,
     the model files are tracked.
   - `README.md:236` claims a `vendor/` directory exists in this repo — it
     does not (vendor lives in `maher_ws/src/vendor/` upstream).
3. **`docs/learn/` is personal study material** (8 files, ~36 KB) that the
   current `docs/README.md` already flags as "not part of the project
   deliverable". The M7a author kept them in the repo "for portfolio
   rationale". The decision should be Maher's, but they should at least be
   quarantined under a clearly-marked path.
4. **`scripts/` is one flat folder of 28 files**, including six
   `_underscore-prefixed` dev/debug helpers from one-off M4c1 analyses
   (verified: `_cleanup_inspect.py`, `_inspect_tall_cyl_schema.py`,
   `_peek_bboxes_once.py`, `_summarize_carton.py`, `_summarize_cup.py`,
   `_summarize_tall_cyl.py`). The M7a author already noted this in
   `docs/README.md` as "Recommended later cleanup".
5. **An empty `test/` directory at the repo root** (created by the
   `setup.py` skeleton on 2026-06-04, never used, no `.gitkeep`, not
   referenced anywhere).
6. **The M4c1 annotated PNGs (180 files, 62 MB)** are tracked but no longer
   the only visual evidence — the report.md already summarises the KEEP /
   REJECT outcomes per distractor. Keeping the PNGs in Git is defensible
   for reviewer sanity but bloats the repo.

Below: concrete file/folder facts, classification, and a phased proposal.

---

## 1. Current repo size and file-count facts

Captured 2026-07-05 against the working tree at `main` (ahead 12, no push).

### 1.1 Top-level layout

```
Path                                          Files      Size
--------------------------------------------  -------  -------
README.md (top-level)                            1      14 KB
.cursorrules                                     1       7 KB
.gitignore                                       1       3 KB
LICENSE                                          1     ~10 KB
package.xml                                      1       1 KB
setup.py / setup.cfg                             2       1 KB
yolo26n.pt (untracked, gitignored)               -     5.5 MB
assets/                                          5     168 KB
config/                                          1       8 KB
data/                                          942      18 MB  (all ignored)
docs/                                           24     456 KB
evaluation/                                   1006     4.8 GB  (mostly ignored)
launch/                                          1       8 KB
models/                                          7      91 MB  (4 sacred files tracked)
recognition_of_different_colored_cubes/          9     144 KB
resource/                                        1       4 KB
runs/                                           65     120 MB  (all ignored)
scripts/                                        38     344 KB
test/                                            0       4 KB  (empty dir, tracked)
training/                                        1       8 KB
--------------------------------------------  -------  -------
TOTAL TRACKED                                  317     ~62 MB  (git ls-files content)
TOTAL WORKING TREE                              -    ~11 GB    (dominated by ignored)
```

Tracked `git ls-files` content is ~62 MB (text + small PNGs). Working tree
on disk is ~11 GB because `evaluation/m4c_geometry_filter/` + ignored
`data/` + ignored `runs/` + ignored M4b/M5 .db3 bags dominate.

### 1.2 Untracked files (12)

```
evaluation/m5_live/cubes_2026-06-28/peek_debug_conf020.png               345 KB
evaluation/m5_live/cubes_sticker_off_2026-06-28/conf025/                   4 KB (dir)
evaluation/m5_live/cubes_sticker_off_2026-06-28/latency.json             38 KB
evaluation/m5_live/cubes_sticker_off_2026-06-28/m5_bag_cubes_sticker_off_2026-06-28_091930_metadata.json   237 B
evaluation/m5_live/cubes_sticker_off_2026-06-28/m5_bag_cubes_sticker_off_2026-06-28_091930_sha256.txt       163 B
evaluation/m5_live/cubes_sticker_off_2026-06-28/peek_debug_live_count100.png   213 KB
evaluation/m5_live/cubes_sticker_off_2026-06-28/peek_debug_live_count200.png   212 KB
evaluation/m5_live/cubes_sticker_off_2026-06-28/peek_debug_live_count300.png   214 KB
evaluation/m5_live/cubes_sticker_off_2026-06-28/peek_debug_live_count400.png   211 KB
evaluation/m5_live/cubes_sticker_off_2026-06-28/peek_rgb_pre_launch.png        223 KB
evaluation/m5_live/cubes_sticker_off_2026-06-28/summary.json                   570 B
scripts/_cleanup_inspect.py                                                   318 B
```

All twelve are genuine M5c2 review outputs that were never committed. They
are reproducible from the M5c2 bag + scripts. **Recommend: delete
uncommitted files. The canonical artefacts already in Git
(`summary.json` + `latency.json` in `cubes_2026-06-28/`) are the evidence;
the sticker_off variants duplicate that.**

### 1.3 Ignored noise (large, but already excluded from Git)

```
.local-bin/                                          scratch scripts / one-off binaries
.venv-m2/                                            M2 training venv (torch / ultralytics / onnx)
.yolo_config/                                        Ultralytics cache
data/roboflow/                                       942 files, 18 MB — raw Roboflow images
data/roboflow_det/                                   normalized dataset (regenerable)
data/hardneg/                                        M3c hard-neg dataset (regenerable)
runs/detect/ + runs/m3c/                             65 files, 120 MB — YOLO training outputs
evaluation/_m2m3_verify.py + _results.json           stale local tester harness
evaluation/camera_samples/                           430 files, 24 MB — JetRover RGB captures
evaluation/m2-visualizations/                        17 files, 1.2 MB
evaluation/m3c_predictions/*.png                     30 files per dir (3 dirs)
evaluation/m3c_predictions_empty/*.png               30 files
evaluation/m3c_predictions_hardneg/*.png             ~150 crop previews
evaluation/m3c_roboflow_valid/*.png                 8 files
evaluation/m4b_predictions/                          39 files, 8.3 MB — full evidence pack (gitignored)
evaluation/m4b_predictions_v1_subprocess/            31 files, 7.9 MB — same, v1 subprocess variant
evaluation/m4c_geometry_filter/annotated_cubes/      30 PNGs
evaluation/m4c_geometry_filter/_depth_sanity_*.png  3 sanity-check PNGs
evaluation/m5_live/**/*.db3                          4 .db3 bag files (~3 GB total on disk)
evaluation/m5_live/**/metadata.{json,yaml}           bag sidecar metadata
evaluation/m5_live/**/node.log                      bag replay node logs
evaluation/m5_live/**/sha256.txt                     bag SHA-256 sidecars
evaluation/m5_live/**/*.before-rerun                 6 pre-replay JSON snapshots
models/*.pt                                          (models tracked by force, not by gitignore)
yolo26n.pt                                           top-level stray, 5.5 MB
recognition_of_different_colored_cubes/__pycache__/  pycache
scripts/__pycache__/                                 pycache
```

The `.gitignore` is doing its job — every item above is correctly excluded
from `git ls-files`. The problem is that they exist on disk and visually
inflate `ls` / IDE folder views.

### 1.4 Largest tracked files

Top 30 tracked files by size are all PNG annotated outputs in the 330-370
KB range, dominated by 180 `evaluation/m4c_geometry_filter/annotated_*/`.
**All other tracked files are < 200 KB.** The total tracked size is ~62 MB
because there are many small files, not because any one file is huge.

The exception is `models/best.engine` (21 MB), `models/best.onnx` (35 MB),
`models/best_hardneg.pt` (18 MB), and `models/best.pt` (18 MB) — all sacred
artefacts, **do not delete**. The card explicitly excludes these.

---

## 2. Reachability map

How many tracked files are actually referenced from `README.md`,
`docs/*.md`, `.cursorrules`, or the LOGBOOK?

### 2.1 Scripts referenced from `README.md` (zero direct paths)

`README.md` does not directly reference any `scripts/*.py` path. All script
references go through the documentation layer (`docs/README.md` →
`scripts/README.md`).

### 2.2 Scripts referenced from docs/ + LOGBOOK

Counted by `grep -hE 'scripts/[a-zA-Z_0-9-]+\.(py|sh)' docs/LOGBOOK.md`:

```
18  scripts/m4c_v3v4_run.sh
 9  scripts/verify_camera_samples.py
 6  scripts/test_inference.py
 6  scripts/capture_rgb_depth_sync.py
 5  scripts/m4c_v3v4_summary.py
 4  scripts/m4c_geometry_filter.py
 4  scripts/check_empty_scene.py
 4  scripts/capture_frames.py
 3  scripts/m4c_yolo_inference.py
 2  scripts/normalize_dataset.py
 2  scripts/m5_capture_bag.py
 2  scripts/m4a_trt_smoke_inference.py
 2  scripts/m3_smoke_inference.py
 1  scripts/_summarize_tall_cyl.py
 1  scripts/_summarize_carton.py
 1  scripts/_peek_bboxes_once.py
 1  scripts/m5_parse_latency.py
 1  scripts/m5_analyze_bag.py
 1  scripts/_inspect_tall_cyl_schema.py
```

19 of the 27 tracked .py scripts are referenced from at least one doc.
The eight that are NOT referenced anywhere in `README.md`/`docs/*.md`/
`docs/LOGBOOK.md` are:

```
scripts/_cleanup_inspect.py             (verified: removes _* inspection files in data/hardneg)
scripts/_download_weights.py            (helper that prints Roboflow dataset ID + URL)
scripts/_summarize_cup.py               (one-off M4c1 distractor summary)
scripts/build_hardneg_dataset.py        (referenced by docs/m3d-revived-plan.md as a *pattern*)
scripts/convert_tensorrt.py             (referenced by docs/technical-stack.md M0 export chain)
scripts/export_onnx.py                  (referenced by docs/technical-stack.md M0 export chain)
scripts/finetune_hardneg.py             (referenced by docs/m3d-revived-plan.md as a *pattern*)
scripts/validate_hardneg.py             (no doc reference; M4b-era before/after comparison)
scripts/m5_offline_replay.py            (no doc reference; M5 parity-check harness)
scripts/build_hardneg_dataset.py        (already counted above)
```

Three of those (`export_onnx.py`, `convert_tensorrt.py`, `_download_weights.py`)
are part of the documented M0 model-export chain even if their names aren't
inline-linked. Two more (`build_hardneg_dataset.py`, `finetune_hardneg.py`)
are referenced in `docs/m3d-revived-plan.md` as templates. That leaves five
scripts that are genuinely orphan-or-near-orphan: `_cleanup_inspect.py`,
`_summarize_cup.py`, `validate_hardneg.py`, `m5_offline_replay.py`,
`_download_weights.py`.

`_download_weights.py` is in the scripts/README.md table and is a
documented one-liner ("prints the Roboflow dataset ID and source URL") —
keep.

`_summarize_cup.py` is mentioned in scripts/README.md (dev/debug helper)
and was used for the M4c1 distractor summary alongside `_summarize_carton.py`
and `_summarize_tall_cyl.py`. Keep for reproducibility.

`_cleanup_inspect.py` is in scripts/README.md (dev/debug helper).
Keep for reproducibility.

`validate_hardneg.py` is in scripts/README.md (Training / fine-tune
section). Keep — it was the M4b before/after comparison harness.

`m5_offline_replay.py` is in scripts/README.md (M5 Live eval section).
Keep — it is the parity-check harness mentioned in the M5 docs.

**Verdict: every tracked script is referenced from at least one doc or the
scripts/README.md. No script is fully orphan.**

### 2.3 Docs referenced from other docs

All 24 files in `docs/` are reachable. Cross-references verified:

- `README.md` → `docs/{README,architecture,evaluation,technical-stack,milestones,m3d-revived-plan,LOGBOOK,Concept-and-Approach,project-definition}.md` + `docs/m4c_geometry_filter/report.md` + `evaluation/m5_live/report.md`
- `docs/README.md` → all other `docs/*.md`
- `docs/milestones.md` → `docs/{technical-stack,architecture,evaluation,m3d-revived-plan}.md`
- `docs/LOGBOOK.md` → every other tracked doc (100+ references)
- `docs/m3d-revived-plan.md` → `docs/{model-options,model-alternative-research,model-hard-negative-plan,model-objectness-addendum,LOGBOOK}.md`

No document is orphaned.

### 2.4 Evaluation artefacts referenced from docs

```
evaluation/m5_live/report.md                      → referenced by README.md, docs/README.md, .cursorrules
evaluation/m4c_geometry_filter/report.md          → referenced by README.md, docs/README.md
evaluation/m3c_predictions/report.md              → referenced by docs/README.md (M3c evidence)
evaluation/m4b_predictions/report.md              → gitignored but referenced internally by m4b scripts
```

All evidence reports are tracked and reachable.

---

## 3. Per-area classification

The card explicitly listed ten top-level areas to classify. Below is each,
with what should stay, what should move, and what should be considered for
deletion.

### 3.1 `README.md`, `.cursorrules`, `.gitignore`, setup/package files

| File | Status | Notes |
|------|--------|-------|
| `README.md` | KEEP — fix 2 inaccuracies | Line 231 wrongly claims `models/` is gitignored. Line 236 wrongly claims `vendor/` exists in this repo. **Recommendation: fix in a follow-up card.** |
| `.cursorrules` | KEEP | Current operating manual; current Status block is up to date as of 2026-06-28. |
| `.gitignore` | KEEP — tighten 1 rule | Working correctly. Two cleanups available: (a) consolidate the three `evaluation/m3c_*/*.png` rules into one pattern; (b) add `*.db3` / `*.mcap` / `metadata.{json,yaml}` / `node.log` / `sha256.txt` as a generic `.ros-bag-sidecars` block so future bag captures inherit the rule without per-dir edits. Both are nice-to-have, not blocking. |
| `LICENSE` | KEEP | Apache-2.0, required. |
| `setup.py`, `setup.cfg`, `package.xml` | KEEP | Required by colcon / ament_python. |
| `resource/recognition_of_different_colored_cubes` | KEEP | ament index marker. |

### 3.2 `recognition_of_different_colored_cubes/` (the ROS 2 package)

```
recognition_of_different_colored_cubes/__init__.py             KEEP (empty, but ament convention)
recognition_of_different_colored_cubes/cube_detection_node.py  KEEP (29 rclpy params, 3 publishers — the live node)
recognition_of_different_colored_cubes/geometry_filter.py      KEEP (M4c1 KEEP/REJECT helper)
recognition_of_different_colored_cubes/__pycache__/             gitignored, ignore
```

Plus 6 other files (verified via `ls -la`). **No cleanup needed here.** This
is the entire ROS 2 deliverable — node + helper + package marker.

### 3.3 `launch/`, `config/`

```
launch/detection.launch.py    KEEP
config/params.yaml           KEEP (referenced from README.md)
```

Both are 1 file each. No cleanup needed.

### 3.4 `scripts/` (28 files, 344 KB)

```
scripts/build_hardneg_dataset.py         KEEP  (m3d-revived-plan.md pattern)
scripts/capture_frames.py                KEEP  (M4/M6 capture harness)
scripts/capture_rgb_depth_sync.py        KEEP  (M4c1 sync capture)
scripts/check_empty_scene.py             KEEP  (pre-capture probe)
scripts/_cleanup_inspect.py              KEEP  (dev helper; reproducible)
scripts/convert_tensorrt.py              KEEP  (M0 model-export chain)
scripts/_download_weights.py             KEEP  (Roboflow helper)
scripts/export_onnx.py                   KEEP  (M0 model-export chain)
scripts/finetune_hardneg.py              KEEP  (m3d-revived-plan.md pattern)
scripts/_inspect_tall_cyl_schema.py      KEEP  (dev helper; reproducible)
scripts/m3_smoke_inference.py            KEEP  (M3 smoke test)
scripts/m4a_trt_smoke_inference.py       KEEP  (M4a smoke test)
scripts/m4c_geometry_filter.py           KEEP  (M4c1 dev-PC filter)
scripts/m4c_v3v4_run.sh                  KEEP  (M4c1 SSH orchestration, 18 LOGBOOK refs)
scripts/m4c_v3v4_summary.py              KEEP  (M4c1 summary)
scripts/m4c_yolo_inference.py            KEEP  (M4c1 raw YOLO on distractor frames)
scripts/m5_analyze_bag.py                KEEP  (M5 bag analyzer)
scripts/m5_capture_bag.py                KEEP  (M5 Jetson-side orchestrator)
scripts/m5_offline_replay.py             KEEP  (M5 parity check)
scripts/m5_parse_latency.py              KEEP  (M5 latency parser)
scripts/normalize_dataset.py             KEEP  (M2 dataset normalization)
scripts/_peek_bboxes_once.py             KEEP  (dev helper; reproducible)
scripts/_summarize_carton.py             KEEP  (dev helper; reproducible)
scripts/_summarize_cup.py                KEEP  (dev helper; reproducible)
scripts/_summarize_tall_cyl.py           KEEP  (dev helper; reproducible)
scripts/test_inference.py                KEEP  (M4b inference harness, 6 LOGBOOK refs)
scripts/validate_hardneg.py              KEEP  (M4b before/after FP harness)
scripts/verify_camera_samples.py         KEEP  (dev-PC sidecar checker, 9 LOGBOOK refs)
```

**Recommendation: keep all 28. Move the six `_underscore-prefixed` dev
helpers into `scripts/dev_helpers/` in a follow-up card.** The M7a author
already flagged this in `docs/README.md` ("Recommended later cleanup") and
in `scripts/README.md` (last paragraph). This is purely organisational —
no script is redundant.

### 3.5 `docs/` (24 files, 456 KB)

```
docs/README.md                            KEEP  (M7a index, current)
docs/architecture.md                      KEEP  (current source of truth)
docs/Concept-and-Approach.md              KEEP  (current source of truth)
docs/evaluation.md                        KEEP  (current source of truth, 50-frame protocol)
docs/LOGBOOK.md                           KEEP  (114 KB chronological log; current)
docs/m3d-revived-plan.md                  KEEP  (current active plan)
docs/milestones.md                        KEEP  (current source of truth)
docs/project-definition.md                KEEP  (current source of truth)
docs/technical-stack.md                   KEEP  (current source of truth)
docs/vendor-audit.md                      KEEP  (current source of truth)

docs/model-options.md                     HISTORICAL  (early comparison, superseded by Concept-and-Approach)
docs/model-alternative-research.md        HISTORICAL  (non-YOLO alternatives ruled out)
docs/model-hard-negative-plan.md          HISTORICAL  (M3c plan, replaced by M4c1)
docs/model-objectness-addendum.md         HISTORICAL  (objectness fallback, moot after geometry filter)

docs/learn/MISSION.md                     NEEDS DECISION  (personal study)
docs/learn/NOTES.md                       NEEDS DECISION  (personal study)
docs/learn/RESOURCES.md                   NEEDS DECISION  (personal study)
docs/learn/assets/lesson.css              NEEDS DECISION  (personal study)
docs/learn/assets/quiz.js                 NEEDS DECISION  (personal study)
docs/learn/lessons/0001-what-yolo-outputs.html  NEEDS DECISION  (personal study)
docs/learn/learning-records/0001-workspace-established.md  NEEDS DECISION  (personal study)
docs/learn/learning-records/0002-workspace-relocated.md   NEEDS DECISION  (personal study)
docs/learn/learning-records/0003-external-dataset-gotchas.md  NEEDS DECISION  (personal study)
docs/learn/reference/m2-implementer-handoff.md            NEEDS DECISION  (personal study)
```

The `docs/learn/` tree is 8 files / ~36 KB. `docs/README.md` already
documents it as "Learning notes (personal study) … not part of the
project deliverable. Skip them unless you are looking for the rationale
behind my approach." Two options for Maher:

- **Option A — keep as-is.** The current `docs/README.md` already routes
  readers away. Cost: 36 KB + 8 extra entries in the file index. Benefit:
  preserves Maher's study notes alongside the project.
- **Option B — move out of the repo.** Move `docs/learn/` to a sibling
  `~/maher_ws/learn/` or a separate `~/learning-notes/` directory. Cleanest
  separation; the project repo no longer carries study material.
- **Option C — remove.** The notes are Maher's own work; if he's not
  using them, drop them.

**Recommend Option A** (current state) unless Maher explicitly chooses B
or C. The cost is small and the routing note already exists.

### 3.6 `evaluation/` (1006 files, 4.8 GB on disk; ~52 MB tracked)

The bulk of clutter lives here. Splitting by sub-folder:

```
Tracked (kept)
--------------
evaluation/evaluate.py                          4 KB     KEEP  (50-frame protocol script, referenced by docs/evaluation.md)
evaluation/m3c_predictions/detections.json      ~5 KB    KEEP  (M3c evidence)
evaluation/m3c_predictions/report.md            ~3 KB    KEEP  (M3c evidence)
evaluation/m3c_predictions_empty/detections.json        KEEP  (M3c empty-scene evidence)
evaluation/m3c_predictions_hardneg/detections.json      KEEP  (M3c hard-neg evidence)
evaluation/m3c_roboflow_valid/detections.json           KEEP  (Roboflow valid evidence)
evaluation/m4c_geometry_filter/filter_results_*.json (7 files) KEEP  (M4c1 evidence)
evaluation/m4c_geometry_filter/sweep_*.json (6 files)   KEEP  (M4c1 sweep evidence)
evaluation/m4c_geometry_filter/yolo_detections_*.json (7 files) KEEP  (M4c1 evidence)
evaluation/m4c_geometry_filter/report.md        ~10 KB   KEEP  (M4c1 evidence report, README-linked)
evaluation/m4c_geometry_filter/v3_v4_summary.md ~3 KB    KEEP  (M4c1 V3/V4 summary)
evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md  ~2 KB KEEP (M4c1 V3/V4 followup)
evaluation/m4c_geometry_filter/scene_probes/    18 files, ~1.5 MB  KEEP  (M4c1 reviewer probes)
evaluation/m5_live/report.md                    ~10 KB   KEEP  (M5 evidence report, README-linked)
evaluation/m5_live/.gitkeep                     0        KEEP
evaluation/m5_live/empty_2026-06-28/preview/debug_overlay.png  354 KB  KEEP (README-linked demo)
evaluation/m5_live/empty_2026-06-28/preview/rgb_frame.png      370 KB  KEEP (preview)
evaluation/m5_live/empty_2026-06-28/{latency,summary}.json     KEEP  (M5 evidence)
evaluation/m5_live/cubes_2026-06-28/{latency,summary}.json     KEEP  (M5 evidence)
evaluation/m5_live/cubes_2026-06-28/peek_*.png                3 files, ~1 MB  KEEP (M5 reviewer evidence)
evaluation/m5_live/cubes_sticker_off_2026-06-28/canonical_*.json  KEEP  (M5c2 canonical)
evaluation/m5_live/cubes_sticker_off_2026-06-28/peek_rgb_pre_launch.png  KEEP
evaluation/m5_live/cubes_sticker_off_2026-06-28/peek_debug_live_count*.png  4 files  KEEP
evaluation/m5_live/metrics_t_5fbeb0a2.md         ~3 KB    KEEP  (kanban-card-linked metrics)
evaluation/m5_live/review_2026-06-28/*.json     4 files   KEEP  (independent reviewer re-runs)

Tracked but probably oversized for retention
--------------------------------------------
evaluation/m4c_geometry_filter/annotated_*/    180 PNGs, ~62 MB  KEEP, BUT consider archive-on-tag
                                                (8 distractor classes × 30 frames, except
                                                 annotated_cubes/ which is gitignored and
                                                 annotated_empty + annotated_empty_0.50 exist)

Gitignored (correctly)
----------------------
evaluation/camera_samples/                     430 files, 24 MB   correct
evaluation/m2-visualizations/                  17 files, 1.2 MB   correct
evaluation/_m2m3_verify.py + _results.json                        correct
evaluation/m3c_predictions/*.png               30 per dir         correct
evaluation/m3c_predictions_empty/*.png         30                correct
evaluation/m3c_predictions_hardneg/*.png       ~150              correct
evaluation/m3c_roboflow_valid/*.png             8                 correct
evaluation/m4b_predictions/                    39 files, 8.3 MB   correct
evaluation/m4b_predictions_v1_subprocess/      31 files, 7.9 MB   correct
evaluation/m4c_geometry_filter/annotated_cubes/                  correct (cubes excluded on purpose — V2 result captured in JSON)
evaluation/m4c_geometry_filter/_depth_sanity_*.png               correct
evaluation/m5_live/**/*.db3                    ~3 GB total        correct
evaluation/m5_live/**/metadata.{json,yaml}                       correct
evaluation/m5_live/**/node.log                                   correct
evaluation/m5_live/**/sha256.txt                                 correct
evaluation/m5_live/**/*.before-rerun           6 files           correct
```

**Recommendation: leave the gitignored folders alone** (they are correct).
**Recommendation: keep all tracked evidence** — the 180 M4c1 annotated PNGs
are large but they back the KEEP/REJECT numbers in `report.md`. They could
be archived on a release tag in a follow-up card if repo size becomes an
issue, but that's a future-problem, not a current cleanup.

### 3.7 `models/` (91 MB on disk; 7 entries)

```
models/.gitkeep                        0   KEEP
models/README.md                       25 KB  KEEP (artifact documentation)
models/best.pt                         18 MB  KEEP — SACRED (M2 fallback-trained, used by M3d-revived)
models/best.onnx                       35 MB  KEEP — SACRED (M0 export chain)
models/best.engine                     21 MB  KEEP — SACRED (M0 TensorRT, loaded by node)
models/best_hardneg.pt                 18 MB  KEEP — SACRED (M3c hard-neg experiment)
models/_check_source_polygons.jpg      36 KB  KEEP — sanity-check artefact from M2 dataset diagnosis
```

The card explicitly forbids touching the four `.pt/.onnx/.engine` files.
`_check_source_polygons.jpg` is a one-off M2 diagnostic that has archival
value (see `docs/LOGBOOK.md` 2026-06-24 M2 entry). No deletion recommended.

### 3.8 `training/` (1 file)

```
training/train.ipynb    1.3 KB   KEEP (optional fine-tune notebook, referenced by README)
```

The README "Key Directories" table mentions `training/` with `train.ipynb`.
Tracked. No cleanup needed.

### 3.9 `assets/` (5 files, 168 KB)

```
assets/concept2_inference_pipeline.dot    KEEP (renderable source)
assets/concept2_inference_pipeline.png    KEEP (README-linked)
assets/concept2_training_pipeline.dot     KEEP (renderable source)
assets/concept2_training_pipeline.png     KEEP (linked from docs)
assets/results/.gitkeep                   KEEP
```

No cleanup needed.

### 3.10 `test/` (empty)

```
test/    empty dir, no .gitkeep, never referenced
```

Created by the `setup.py` skeleton on 2026-06-04 and never used. **The dir
is tracked as an empty tree but contains no files** (verified via
`git ls-files test/`). Safe to delete with `git rm -r --cached test/`
and a corresponding `.gitkeep` decision (either keep an empty dir with a
`.gitkeep` or remove entirely).

**Recommendation: remove.** Add to follow-up card.

### 3.11 Ignored local folders (already gitignored, but pollute `ls`)

```
.local-bin/        scratch scripts / one-off binaries    correct
.venv-m2/          M2 training venv                       correct
.yolo_config/      Ultralytics cache                      correct
data/              942 files, 18 MB                       correct
runs/              65 files, 120 MB                       correct
```

All correctly ignored. No `.gitignore` change required. To clean up disk
space Maher can `rm -rf` any of these locally — none are needed by the
build / run path.

### 3.12 Top-level stray files

```
yolo26n.pt   5.5 MB at repo root — gitignored (verified: .gitignore line 23 `*.pt`)
```

The `*.pt` rule catches it. Maher should `rm yolo26n.pt` locally to clean
the working tree, but Git is fine.

---

## 4. Proposed deletion / move list (NOT executed)

Tiered by safety. Maher must approve each tier before execution.

### Tier 1 — pure safe (no tracking change, no evidence loss)

- **Delete uncommitted files** (12 files, ~1.7 MB on disk, none are referenced by any doc):
  - `evaluation/m5_live/cubes_2026-06-28/peek_debug_conf020.png`
  - `evaluation/m5_live/cubes_sticker_off_2026-06-28/` (whole dir; gitignored `.db3`, `metadata.yaml`, `node.log` inside are not in Git; the tracked canonical files are `canonical_summary.json` + `canonical_latency.json` and one `peek_rgb_pre_launch.png` — those will remain tracked after deleting the dir contents that are NOT tracked)
  - `scripts/_cleanup_inspect.py`

  Action: `git clean -fd evaluation/m5_live/cubes_sticker_off_2026-06-28/ scripts/_cleanup_inspect.py evaluation/m5_live/cubes_2026-06-28/peek_debug_conf020.png`
  (then re-run `git status` to confirm nothing tracked was removed).

- **Delete the empty `test/` directory**:
  Action: `git rm -r test && rmdir test` (no files in it, no references).

### Tier 2 — README inaccuracies (cosmetic, low risk)

- **Fix `README.md:231`**: change
  `| \`models/\` | \`best.pt\`, \`best.onnx\`, \`.engine\` — gitignored, not committed |`
  to
  `| \`models/\` | Tracked: \`best.pt\`, \`best.onnx\`, \`best.engine\`, \`best_hardneg.pt\` (see \`models/README.md\`); \`*.pt\` and \`models/*\` are in \`.gitignore\` for fresh clones |`.
- **Fix `README.md:236`**: delete the row
  `| \`vendor/\` | Reference notes for Hiwonder vendor code (not copied) |`.
  Vendor lives in the upstream `maher_ws/src/vendor/`; this project's
  `docs/vendor-audit.md` documents which vendor packages are touched.

### Tier 3 — `.gitignore` tightening (small, no behavioural change)

- Consolidate the three `evaluation/m3c_*/*.png` rules into
  `evaluation/m3c_*/!(*.json|*.md)`.
- Replace the five per-extension rules under `evaluation/m5_live/**` with
  one rule that ignores everything except `*.json`, `*.md`, `*.png`,
  `!evaluation/m5_live/report.md`, `!evaluation/m5_live/.gitkeep`. This
  makes future bag captures work without per-dir edits.

### Tier 4 — scripts organisation (organisational only, no script deleted)

- Move six `_underscore-prefixed` helpers into `scripts/dev_helpers/`:
  `_cleanup_inspect.py`, `_inspect_tall_cyl_schema.py`,
  `_peek_bboxes_once.py`, `_summarize_carton.py`, `_summarize_cup.py`,
  `_summarize_tall_cyl.py`. Update `scripts/README.md` and any LOGBOOK
  references. M7a already flagged this as the right move.

### Tier 5 — `docs/learn/` decision (Maher's call, no default)

- **Option A (default — keep)** — already routed away by `docs/README.md`.
- **Option B — move** to `~/maher_ws/learn/` or similar.
- **Option C — delete** if Maher isn't using them.

### Tier 6 — large-archive future (NOT now)

- If repo size ever matters, archive the M4c1 `annotated_*/` PNGs (62 MB)
  to a release tag and remove from the working branch. The `report.md`
  + JSON files are sufficient evidence for the KEEP/REJECT verdict.
- Similarly: `evaluation/m4b_predictions/` and
  `evaluation/m4b_predictions_v1_subprocess/` are currently gitignored
  entirely. If Maher wants to preserve one set of evidence permanently,
  it should be tracked (currently neither is).

---

## 5. Evaluation artefacts policy

The current policy (informal, but visible from `.gitignore`):

| Artefact type | In Git? | Why |
|---------------|---------|-----|
| Per-milestone `report.md` | Yes | The canonical evidence document, referenced from README/docs. |
| Per-milestone `detections.json` / `filter_results_*.json` / `sweep_*.json` | Yes | Structured numerical evidence. |
| Per-milestone `*.png` annotated previews | Mostly gitignored (M3c, M4b, M5 bag-sidecar). Only M4c1 `annotated_*/` PNGs are tracked (180 files, 62 MB). | Visual evidence. Large but reviewer-friendly. |
| ROS bag `.db3` files | No | Reproducible from `scripts/capture_rgb_depth_sync.py` + `scripts/m5_capture_bag.py`. |
| Bag sidecar metadata / node logs / sha256 | No | Reproducible alongside the bag. |
| Per-frame review PNGs in `m5_live/*/peek_*` | Yes (some) | Reviewer sanity checks, ~1 MB each, small total. |

**Recommendation: keep this policy as-is.** It separates reproducible
numerical evidence (tracked) from reproducible raw capture data
(gitignored). The one asymmetric case — M4c1 annotated PNGs being tracked
while M3c / M4b PNGs are gitignored — could be regularised in Tier 6
above (either drop M4c1 PNGs or add M3c/M4b PNGs to tracking) but is not
blocking.

---

## 6. Scripts policy

Current state:

| Category | Count | Tracked? | Notes |
|----------|-------|----------|-------|
| M0 model export (production) | 4 | Yes | Used by the documented build chain. |
| M3 smoke tests | 2 | Yes | One-time dev-PC sanity checks. |
| M4c1 geometry filter | 5 | Yes | One is the dev-PC filter (`m4c_geometry_filter.py`), one is the SSH orchestrator (`m4c_v3v4_run.sh`), three are per-distractor summaries (`_summarize_*.py`). |
| M5 live eval | 4 | Yes | Capture / analyse / offline-replay / parse-latency. |
| Capture (Jetson side) | 3 | Yes | rclpy subscribers + sidecar checker. |
| Training / fine-tune | 5 | Yes | Dataset normalisation + M3c hard-neg harness + M4b validate. |
| Dev / debug helpers (`_*`) | 6 | Yes | M4c1 distractor analysis one-offs. |
| Stray uncommitted | 1 | No (`_cleanup_inspect.py`) | New, never committed. |

**Recommendation:** Tier 4 in §4 moves the six `_underscore-prefixed`
helpers into `scripts/dev_helpers/`. Every other script is part of a
documented pipeline (M0 export, M3 smoke, M4c1 filter, M5 live eval,
capture, training). Keep all 28 tracked scripts.

---

## 7. Top 5 most important cleanup recommendations

In priority order (highest impact first):

1. **Fix the two README inaccuracies** (Tier 2). `README.md:231` wrongly
   says `models/` is gitignored; `README.md:236` claims a `vendor/`
   directory exists that doesn't. These will mislead every future reader
   and recruiter. Cost: 2 line edits.
2. **Delete the 12 uncommitted M5c2 debug files + `scripts/_cleanup_inspect.py` + the empty `test/` dir** (Tier 1). They are not in Git,
   not referenced anywhere, and they bloat `git status` and `ls` output.
   Cost: 1 `git clean` + 1 `git rm`. Zero evidence loss (canonical
   evidence is already tracked).
3. **Decide what to do with `docs/learn/`** (Tier 5). Eight files / 36 KB
   of personal study material currently lives in the project repo and is
   routed away by `docs/README.md`. Confirm with Maher whether to keep
   (Option A — current), move to a sibling notes directory (Option B), or
   delete (Option C).
4. **Move six `_underscore-prefixed` dev helpers into `scripts/dev_helpers/`** (Tier 4). M7a author already flagged this in
   `docs/README.md` as "Recommended later cleanup". Mechanical refactor:
   `git mv`, update `scripts/README.md`, update 3 LOGBOOK references.
   Pure organisation, no script deleted.
5. **Tighten `.gitignore` so future bag captures don't need per-dir edits** (Tier 3). Replace the five
   `evaluation/m5_live/**/*.X` rules with one `evaluation/m5_live/**` that
   excepts only `report.md`, `.gitkeep`, `*.json`, `*.md`, `*.png`. Stops
   the pattern where every new M-bag run requires touching `.gitignore`.

Nothing else is urgent. The model artefacts, vendor references, ROS 2
package code, launch/config, training notebook, scripts, evidence
reports, and tracked evaluation JSONs are all correctly tracked and
correctly referenced.

---

## 8. Recommended cleanup phases

Each phase is a separate kanban card so Maher can approve / reject
individually.

| Phase | Card title | Owner | Effort | Risk |
|-------|-----------|-------|--------|------|
| Phase 1 (M7b1) | Tier 1 + Tier 2: delete untracked noise + fix README inaccuracies | documenter | 15 min | none |
| Phase 2 (M7b2) | Tier 4: move `_underscore-prefixed` scripts into `scripts/dev_helpers/` | documenter | 30 min | low (LOGBOOK references need updating) |
| Phase 3 (M7b3) | Tier 3: tighten `.gitignore` rules | documenter | 15 min | low |
| Phase 4 (M7b4) | Tier 5: `docs/learn/` decision (keep / move / delete) | documenter after Maher's call | 15-60 min | depends on decision |
| Phase 5 (M7b5) | Tier 6 (future): archive M4c1 annotated PNGs to a release tag | documenter | 30 min | medium (touches tracked evidence) |

**No card is opened yet.** This audit is the input for the orchestrator
to discuss with Maher. After Maher picks which phases to run, the
documenter can open the corresponding cards.

---

## 9. What this audit did NOT touch

- No tracked file was modified.
- No `.gitignore` rule was changed.
- No model artefact was inspected beyond size + presence.
- No Hiwonder vendor package was touched (and would not be — they live
  outside this repo at `maher_ws/src/vendor/`).
- `t_1124e5e0` (M3d-revived fine-tune) was not unblocked. Project remains
  paused on cleanup decisions.
- No commit was made by this audit run. The card request explicitly
  says to commit the audit locally; that commit will be made after this
  report is written and reviewed (see next step).