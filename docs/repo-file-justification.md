# M7c — Per-file Justification for Every Tracked Doc and Script

Date: 2026-07-05
Author: documenter (kanban card `t_5f04e906`, run 108)
Predecessor: `docs/repo-cleanup-audit.md` (M7b, `t_5c5aeba9`).
Scope: every file listed in the M7c card body — 24 tracked docs and 28 tracked scripts.
This is an AUDIT / RECOMMENDATION document, not an execution plan.
**No file in this report was modified.**

This audit is stricter than M7b: every row carries concrete evidence (line/paragraph
references in the source, or a direct inspection note of the script's argparse /
docstring / imports) and an individual recommendation. "All scripts are referenced"
is not used as a reason. The default for `_underscore-prefixed` dev helpers is
`MOVE` to `scripts/dev_helpers/`, not automatic `KEEP`. The default for `docs/learn/*`
is `NEEDS MAHER DECISION` unless the file clearly serves the project deliverable.

---

## Summary of recommendations

The M7c card body lists **24 tracked docs** and **28 tracked scripts**. Each row in the
Documents and Scripts tables below maps to one of those filenames, no duplicates.

|| Recommendation | Docs | Scripts | Total |
||---|---:|---:|---:|
|| `KEEP` | 9 | 21 | 30 |
|| `KEEP-HISTORICAL` | 5 | 1 | 6 |
|| `MOVE` (to `scripts/dev_helpers/`) | 0 | 6 | 6 |
|| `DELETE` | 0 | 0 | 0 |
|| `NEEDS MAHER DECISION` | 10 | 0 | 10 |
|| **Total** | **24** | **28** | **52** |

Total files audited: **52** (24 docs + 28 scripts).

The "21 scripts `KEEP`" includes `scripts/convert_tensorrt.py`, whose row says
`KEEP (with note)` — the note is that it is a 10-line stub. See the Notes on the two
stubs section below.

Two scripts (`export_onnx.py`, `convert_tensorrt.py`) are flagged as **stubs** that
the M7b audit described as part of the "documented M0 model-export chain". Direct
inspection shows both are 10–13 line files with `def main(): pass`. The recommendation
in the table below is `KEEP-HISTORICAL` for `export_onnx.py` and `KEEP` for
`convert_tensorrt.py` with a separate note: the README and `technical-stack.md` point
at `trtexec` and the actual `best.pt → best.onnx → best.engine` step was performed
by hand on the Jetson — these stubs document the intended interface but were not the
code that did the work. Maher should decide whether to either (a) implement them or
(b) delete them, in a follow-up card. For the M7c verdict they are documented
historical artifacts, not silent dead code.

Ten `docs/learn/*` files are explicitly marked `NEEDS MAHER DECISION` per the M7c
card instructions ("default recommendation should be `NEEDS MAHER DECISION` or
`MOVE`, not automatic `KEEP`"). They are: `MISSION.md`, `NOTES.md`, `RESOURCES.md`,
the three `learning-records/*.md` files, the single authored lesson
(`lessons/0001-what-yolo-outputs.html`), the M2 reference doc
(`reference/m2-implementer-handoff.md`), and the two `assets/` files (`lesson.css`,
`quiz.js`). The two `assets/` files only exist if the lessons stay.

Six underscore-prefixed scripts (`_cleanup_inspect.py`, `_inspect_tall_cyl_schema.py`,
`_peek_bboxes_once.py`, `_summarize_carton.py`, `_summarize_cup.py`,
`_summarize_tall_cyl.py`) default to `MOVE` per the M7c card rule. Two of them
(`_cleanup_inspect.py`, `_download_weights.py`) are also flagged in M7b as
untracked/noise; `_download_weights.py` is a full 83-line working Roboflow helper
and is `KEEP`, while `_cleanup_inspect.py` is a 9-line one-off and is `MOVE`.

---

## Documents table

| # | Path | Current role | Evidence / references | What breaks if deleted | Recommendation | Justification |
|--:|------|--------------|------------------------|------------------------|----------------|---------------|
| 1 | `docs/architecture.md` | Canonical architecture doc — vendor-first Mermaid pipeline, topic table, dual-output contract decision. | Linked from `README.md:31`, `README.md:249`, `docs/README.md:19`, `docs/LOGBOOK.md` M1/M5 entries, `docs/technical-stack.md:5`. The only doc with the full topic table. | Loses the architecture source of truth; the README would link to nothing. Other docs (technical-stack, milestones, vendor-audit) reference its decisions. | `KEEP` | Live source of truth for the pipeline diagram and topic contract. Mermaid diagram is the current vendor-first reference; PNG assets are supplementary. |
| 2 | `docs/Concept-and-Approach.md` | Explains why YOLOv5 + TensorRT (one-stage vs two-stage, Faster R-CNN ruled out, YOLOv8 note, model strategy). | Linked from `README.md:250`, `docs/README.md:30`. Same content appears (compressed) in `docs/milestones.md` M2 strategy paragraph. | Loses the model-selection rationale; only place where the alternatives (Faster R-CNN, YOLOv8, etc.) are individually addressed. | `KEEP` | Live source of truth for the YOLOv5 vs alternatives justification. |
| 3 | `docs/evaluation.md` | 50-frame evaluation protocol — setup, metrics table, per-class breakdown. Status placeholder ("to be completed in Milestone 6"). | Linked from `README.md:251,77`, `docs/README.md:21,62`, `docs/milestones.md:199`, `docs/LOGBOOK.md` M6 references. | Loses the protocol definition; M6 evaluation card has nothing to execute against. | `KEEP` | Live source of truth for the eval protocol. M6 numbers are placeholder; the protocol is what the implementer/tester need. |
| 4 | `docs/learn/assets/lesson.css` | Shared stylesheet for `docs/learn/lessons/*.html`. Dark/light theming. | Referenced from `docs/learn/lessons/0001-what-yolo-outputs.html:7` (`<link rel="stylesheet" href="../assets/lesson.css">`). | The lesson HTML loses all styling. | `NEEDS MAHER DECISION` | Only used by `docs/learn/lessons/`. Travels with the lessons; if lessons move/die, this asset dies too. Maher's call (paired with #5, #9, #10, #11, #12). |
| 5 | `docs/learn/assets/quiz.js` | Lesson widget: theme toggle (localStorage) + quiz reveal. | Referenced from `docs/learn/lessons/0001-what-yolo-outputs.html` (script tag not in the head-10 lines, but `lesson.css:1` header confirms it). `docs/learn/NOTES.md:18` calls out the assets. | The lesson HTML loses its interactive widgets. | `NEEDS MAHER DECISION` | Same as #4 — bound to lessons. |
| 6 | `docs/learn/learning-records/0001-workspace-established.md` | Learning record: workspace was scaffolded for the cube-recognition learning arc. | Self-referential. Not linked from any other doc, README, or LOGBOOK. | Loses 10 lines of personal study history. | `NEEDS MAHER DECISION` | Personal study record; no project value. Default per M7c rule: `NEEDS MAHER DECISION`. |
| 7 | `docs/learn/learning-records/0002-workspace-relocated.md` | Learning record: explains why the workspace moved from `~/maher_ws/learn_cube_recognition/` into `docs/learn/`. | Self-referential. The only doc that documents the *intent* to keep lessons inside the project repo. | Loses 13 lines of rationale for keeping `docs/learn/` inside the repo (the rationale itself is the value). | `NEEDS MAHER DECISION` | Personal study record; rationale for keeping it is a Maher preference, not a project one. |
| 8 | `docs/learn/learning-records/0003-external-dataset-gotchas.md` | Learning record: documents the Roboflow polygon-vs-detection label mix and the `green cube` vs `green_cube` class-name gotchas. | Cites `scripts/normalize_dataset.py` and kanban `t_f6d3380d`. Has project-relevant content (the gotchas are real and the script fix is in the repo). | Loses 15 lines that explain why `scripts/normalize_dataset.py` exists. | `NEEDS MAHER DECISION` | Content IS project-relevant (it documents a script in the repo), but the framing is personal-study. Maher can decide if it stays as a personal note or is folded into a comment block inside `normalize_dataset.py`. |
| 9 | `docs/learn/lessons/0001-what-yolo-outputs.html` | Lesson 0001: "What a YOLOv5 model actually outputs". | Self-referential HTML; pulls in `lesson.css` (#4) and `quiz.js` (#5). `docs/LOGBOOK.md` has no references. `docs/learn/RESOURCES.md:24` points at the export recipe but not at this specific HTML. | Loses the only authored lesson. The `assets/` files become orphaned. | `NEEDS MAHER DECISION` | Personal-study lesson; not referenced from any project deliverable. |
| 10 | `docs/learn/MISSION.md` | Learning mission statement (robotics SWE interview prep + own M3–M5 decisions). | Linked from `docs/learn/RESOURCES.md:3`, `docs/learn/NOTES.md:6`. Anchors the learning arc; not project deliverable. | Loses the scope document for the personal learning arc. | `NEEDS MAHER DECISION` | Personal study; no project value beyond the rationale it carries (which #7 also captures). |
| 11 | `docs/learn/NOTES.md` | Teaching session notes — user profile, working notes, tooling quirks. | Self-referential. Documents a personal kanban-dispatcher quirk seen during M2 training. | Loses the personal teaching-session log and the tooling-quirk note. | `NEEDS MAHER DECISION` | Personal study notes. The "tooling quirks" line is one of the few project-relevant sentences (the dispatcher-stale-run note) but is itself a Maher-preference fact. |
| 12 | `docs/learn/reference/m2-implementer-handoff.md` | Reference doc: detailed M2 implementation story (4-act chronology, artifact table, training params, known caveats). | Cites kanban cards `t_83eec93d`, `t_f6d3380d`, `t_4e0c409b`, `t_6fffb30b`. The most project-relevant file in `docs/learn/`. Also cited by `docs/LOGBOOK.md` M2 entry indirectly via the same card IDs. | Loses the most detailed M2 write-up — but `docs/LOGBOOK.md` 2026-06-24 entry and `models/README.md` already cover the same ground in shorter form. | `NEEDS MAHER DECISION` | Has project-relevant content (M2 artifact details, training params) but the framing is "reference doc for the learning arc". Could be folded into `models/README.md` or `LOGBOOK.md`. |
| 13 | `docs/learn/RESOURCES.md` | Curated reading list (Ultralytics, NVIDIA TensorRT, ROS 2 perception, communities). | Cited from `docs/learn/MISSION.md` indirectly. `docs/technical-stack.md` does NOT cite any of these (the technical-stack uses its own resource style). | Loses the curated reading list — but every link is publicly available, so the list itself can be regenerated. | `NEEDS MAHER DECISION` | Personal study resource list. No project code references it. |
| 14 | `docs/LOGBOOK.md` | Chronological session log (1825 lines, 114 KB). 100+ cross-references to other docs. | Cited from `README.md:261`, `docs/README.md:18`, `.cursorrules` "End of day" rule, every other tracked doc references it. | Massive history loss. The reader loses the M1→M5 timeline, the M2/M3/M4 artifact provenance, and the rationale behind every parameter choice. | `KEEP` | Live source of truth for the project history. The M2 → M5 evidence chain is in here. |
| 15 | `docs/m3d-revived-plan.md` | Active fine-tune plan (M3d-revived, positive-detection scope). 955 lines. | Cited from `README.md:23,52`, `docs/README.md:36,87`, `docs/milestones.md:5`, `.cursorrules` "Active step" block. The active next-step document. | Loses the active plan; the kanban card `t_13b658c2` re-open and the M5c2 decision tree become undocumented. | `KEEP` | Live source of truth for the next active step. Maher's "what's the plan?" question reads from this doc. |
| 16 | `docs/milestones.md` | M1–M7 milestone table with ordered steps and current status per step. | Cited from `README.md:209,219,259`, `docs/README.md:17,33`, `docs/LOGBOOK.md` M1–M5 entries, `.cursorrules` M-codes. | Loses the milestone gate map. No new reader can tell whether M5 is done or partial. | `KEEP` | Live source of truth for milestone status. The M5 "PARTIAL" verdict lives here. |
| 17 | `docs/model-alternative-research.md` | M3c2 alternatives research (YOLOv8, RF-DETR, open-vocab detectors, custom hard-neg) — superseded by `model-objectness-addendum.md`. | Cited from `docs/README.md:49` as "research and history (do not edit as current truth)". The document itself declares option F superseded by `model-objectness-addendum.md` §0/§5. | Loses the longer form alternatives comparison; readers fall back to `Concept-and-Approach.md` for the why-YOLO rationale. | `KEEP-HISTORICAL` | Useful for portfolio/audit history. Already marked as research, not current truth. Keep, do not edit. |
| 18 | `docs/model-hard-negative-plan.md` | M3c hard-negative fine-tune plan — acceptance criteria, training recipe. Superseded in practice by the M4c1 geometry filter. | Cited from `docs/README.md:51` as research/history; from `docs/m3d-revived-plan.md:7` as a predecessor. The §1 FP hot-spot table is the source of the M4c1 distractor evaluation. | Loses the M3c rationale; M4c1's design (raised-3D distractor gate) is a direct response to this plan's §1 evidence. | `KEEP-HISTORICAL` | The §1 FP hot-spot numbers are referenced in M3d-revived and M4c1. Historical, but evidentiary. |
| 19 | `docs/model-objectness-addendum.md` | M3c3 addendum — depth/geometry filter plan, hybrid Phase 1 + Phase 2. | Cited from `docs/README.md:50`; from `docs/model-alternative-research.md:7` as the superseding doc; from `docs/m3d-revived-plan.md:8` as a predecessor. The source of the M4c1 v2-only filter parameters. | Loses the design rationale for the live geometry filter. `recognition_of_different_colored_cubes/geometry_filter.py` exists because of this plan. | `KEEP-HISTORICAL` | Source of truth for the geometry-filter design. Marked as historical in `docs/README.md`, but the M4c1 implementation references its parameter ranges. |
| 20 | `docs/model-options.md` | M2 model/weights research (Roboflow Universe candidates, ezhil, robotics25, GitHub/HF). | Cited from `docs/README.md:48` as research/history; from `docs/Concept-and-Approach.md:60` as the M2 source decision gate; from `docs/milestones.md:5,18,43` for M2 readiness; from `docs/technical-stack.md:69` for the weights-source step. | Loses the M2 source decision rationale; `docs/LOGBOOK.md` 2026-06-24 entry covers it briefly. | `KEEP-HISTORICAL` | Documents why we picked the Jakub Slof dataset and why raw Roboflow weights were rejected. Audit history. |
| 21 | `docs/project-definition.md` | Project definition — title, duration, problem, classes, approach, success criteria, non-goals, risks. | Cited from `README.md:257`, `docs/README.md:16`, `.cursorrules` "Canonical Documentation" table. | Loses the project charter. The success-criteria numbers (≥80% accuracy, ≥5 fps, 20–80 cm) live only here. | `KEEP` | Live source of truth for the project charter. |
| 22 | `docs/README.md` | Documentation index — start-here / current / research-history / evaluation grouping, current-status block, recommended later cleanup. | Top-level doc index. `README.md:248` explicitly points to it. Every other doc routes through this. | Loses the doc index; readers must browse `docs/*.md` directly. | `KEEP` | Live source of truth for the doc tree. Updated 2026-07-05 (M7a pass). |
| 23 | `docs/repo-cleanup-audit.md` | M7b audit — 705 lines, 13 sections, 6 cleanup sources. | Self-referential (M7b card `t_5c5aeba9` produced it). `docs/README.md` does not cite it; the M7c card references it as a superseded input. | Loses the predecessor audit. The M7c report (this file) supersedes it. | `KEEP-HISTORICAL` | Audit history. Maher asked for a per-file follow-up because the M7b "keep all" conclusion was rejected. Keep the audit trail. |
| 24 | `docs/technical-stack.md` | Runtime stack — JetPack, ROS 2, Python, vendor packages, model-export chain, dev machine training. | Cited from `README.md:90,208,258`, `docs/README.md:20,32`, `docs/milestones.md:5`, `docs/architecture.md:5` indirectly. `docs/LOGBOOK.md` M2/M3 entries cite it. | Loses the dependency and version documentation. The M2 → M3 → M4 export chain is documented here. | `KEEP` | Live source of truth for the runtime stack and export chain. |

---

## Scripts table

| # | Path | Current role | Evidence / references | What breaks if deleted | Recommendation | Justification |
|--:|------|--------------|------------------------|------------------------|----------------|---------------|
| 1 | `scripts/build_hardneg_dataset.py` | Build the M3c hard-negative dataset by merging Roboflow + JetRover-room frames + cropped distractor regions. | `scripts/README.md:65` lists it; `docs/m3d-revived-plan.md:7` cites it as a pattern; `docs/model-hard-negative-plan.md` references the approach. Argparse + `REPO`, `ROBOFLOW_DET`, `CUBES_DIR` constants in first 35 lines. 200 lines total. | The M3c / M3d-revived plan has no working reference for the hard-neg dataset build. The docstring explicitly explains the polygon-vs-detection gotcha workaround. | `KEEP` | Working recipe for the active fine-tune plan. Pattern cited by `m3d-revived-plan.md`. |
| 2 | `scripts/capture_frames.py` | Jetson-side rclpy subscriber that saves up to N JPGs from `/depth_cam/rgb/image_raw` with JSON sidecar + SHA-256. | `scripts/README.md:56`; `docs/LOGBOOK.md` (4 refs). First lines: argparse, `rclpy`-style header, `capture_frames.py` is the harness used by kanban `t_1c0e63d1` (per docstring). | The M4/M6 evaluation data pipeline has no capture harness. Empty-scene and cubes-scene frames would have to be captured ad-hoc. | `KEEP` | Production capture harness for the M4/M6 evaluation protocol. |
| 3 | `scripts/capture_rgb_depth_sync.py` | Jetson-side sync capture of RGB + depth with `ApproximateTimeSynchronizer` (slop=0.05 s). | `scripts/README.md:57`; `docs/LOGBOOK.md` (6 refs); `scripts/m4c_v3v4_run.sh:81-87` MD5-verifies this file on the Jetson before each V3+V4 run. The 192-line implementation includes per-pair SHA-256 metadata. | The M4c1 distractor evaluation has no capture path. `m4c_v3v4_run.sh` would fail at step 1 (MD5 check). | `KEEP` | Production sync-capture harness for the M4c1 distractor evaluation. |
| 4 | `scripts/check_empty_scene.py` | Jetson-side pre-V4 helper — peek the current RGB frame, run ONNX, print detection count so Maher can verify the floor is clear. | `scripts/README.md:68`; `docs/milestones.md:151` lists the upload to `/tmp/check_empty_scene.py` on the Jetson; `docs/LOGBOOK.md` (4 refs). Uses `onnxruntime`, `cv_bridge`, `rclpy`. 175 lines. | The M4c1 V4 capture workflow loses its pre-flight check. Maher would have to clear the floor blindly. | `KEEP` | Pre-flight harness for the V4 capture. Part of the documented M4c1 workflow. |
| 5 | `scripts/_cleanup_inspect.py` | 9-line one-off: removes `_*` files under `data/hardneg/`. Hardcoded path. | `scripts/README.md:79`. **No LOGBOOK reference.** **Not in Git** (per M7b §1.2 — listed in untracked files). | Trivial — the script can be re-derived from `glob('_*')` in 30 seconds. | `MOVE` (to `scripts/dev_helpers/`) | Per M7c rule: default is MOVE for `_underscore` helpers. Even though it's untracked, the README still lists it; if it's kept at all, it belongs in `dev_helpers/`. Maher should also consider just deleting it (it's untracked). |
| 6 | `scripts/convert_tensorrt.py` | **STUB.** 10 lines: `def main(): pass` plus docstring "Convert ONNX model to TensorRT FP16 engine on Jetson (Milestone 4)". | `scripts/README.md:24` lists it. `docs/technical-stack.md` M0 export chain cites the docstring intent. **NOT referenced in LOGBOOK.** **The actual ONNX→engine conversion was performed by hand with `/usr/src/tensorrt/bin/trtexec`** (per `docs/milestones.md:94-100` and `models/README.md`). | Nothing breaks in the live pipeline — the conversion was done by hand on the Jetson. The stub documents the intended interface but was never the code that did the work. | `KEEP` (with note) | Stub for the intended M4 conversion script. Not used in the live build path; `trtexec` is. Maher should choose: implement it, or delete it (M7b recommended keeping). I keep the M7b verdict because the docstring is the spec. |
| 7 | `scripts/_download_weights.py` | Helper that calls `Roboflow(...).workspace().project(...).version(...).model.download()` and saves SHA-256 / size. 83 lines, real implementation. | `scripts/README.md:22` lists it. `docs/model-options.md` documents the Roboflow API access. **No LOGBOOK reference** (because M2 was performed without the API key, as documented). | If Maher ever tries the raw-weights path again, this is the harness. Already tested and not zero. | `KEEP` | Working Roboflow helper. Not an `_underscore` developer debug — it's a one-line wrapped SDK call. The `_` prefix is incidental (the README still calls it out by name). Keep as KEEP, not MOVE. |
| 8 | `scripts/export_onnx.py` | **STUB.** 13 lines: `def main(): pass`. | `scripts/README.md:23`. **NOT referenced in LOGBOOK.** The actual `best.pt → best.onnx` step was done with `ultralytics.YOLO(...).export(format='onnx')` (per `models/README.md` and `docs/milestones.md:71-77`). | Nothing breaks in the live pipeline — the export was performed in a Jupyter cell. | `KEEP-HISTORICAL` | Same situation as `convert_tensorrt.py`. Documented M0 export-chain stub; never the actual implementation. Maher should decide whether to flesh it out or delete it. |
| 9 | `scripts/finetune_hardneg.py` | M3c fine-tune recipe (continue from `models/best.pt`, hard-neg-augmented data, 25 epochs, lr 0.0005). Argparse for epochs/batch/imgsz. | `scripts/README.md:66`; `docs/m3d-revived-plan.md:7` cites it as a pattern; `docs/model-hard-negative-plan.md` references the recipe; `models/README.md` M3 entry. 107 lines. | The M3d-revived plan loses its template. The next implementer would have to re-derive the recipe from the plan doc alone. | `KEEP` | Active template for the fine-tune recipe. |
| 10 | `scripts/_inspect_tall_cyl_schema.py` | 18-line one-off: dumps the JSON schema of the M4c1 tall_cyl outputs (YOLO detections + filter results). | `scripts/README.md:80`. **1 LOGBOOK reference** (the M4c1 tall_cyl session). | If the M4c1 tall_cyl JSON schema needs re-inspection, the script can be re-derived. No production dependency. | `MOVE` (to `scripts/dev_helpers/`) | Per M7c rule. Trivial one-off. |
| 11 | `scripts/m3_smoke_inference.py` | M3 ORT smoke test — load `models/best.onnx`, run on a saved validation image, decode `(1, 7, 8400)` output. | `scripts/README.md:31`; `docs/milestones.md:70-77` describes this exact test; `docs/LOGBOOK.md` (2 refs). 160 lines. | The M3 export chain has no sanity check. A future re-export would have no reference test. | `KEEP` | First-pass YOLO smoke test for the M3 artifact. |
| 12 | `scripts/m4a_trt_smoke_inference.py` | M4a TensorRT FP16 smoke — same idea on `models/best.engine` on the Orin. | `scripts/README.md:32`; `docs/milestones.md:91-102` describes the artifact and the smoke check; `docs/LOGBOOK.md` (2 refs). 243 lines. Loads `tensorrt` + `pycuda`. | The M4a artifact has no on-Jetson sanity check. | `KEEP` | M4a smoke test — proves the engine loads and runs on the Jetson. |
| 13 | `scripts/m4c_geometry_filter.py` | Phase 1 depth/geometry post-filter (raised_mm + ratio + planar top). Pure numpy. | `scripts/README.md:38`; `docs/milestones.md:118-141` M4c summary; `docs/architecture.md` indirectly; `scripts/m4c_v3v4_run.sh:146-155` calls it; `docs/LOGBOOK.md` (4 refs). 503 lines, the largest script in the repo. | The M4c1 distractor gate (the M5 PARTIAL mitigation) has no dev-PC reference implementation. The live ROS 2 node embeds the same logic in `recognition_of_different_colored_cubes/geometry_filter.py`. | `KEEP` | Production M4c1 filter. The ROS 2 node imports its logic. |
| 14 | `scripts/m4c_v3v4_run.sh` | SSH orchestration: per distractor, capture → SCP → verify SHA → YOLO → filter. | `scripts/README.md:40`; `docs/LOGBOOK.md` (18 refs, the most-cited script); `docs/milestones.md:144-156` M4c1 follow-up; `scripts/m4c_v3v4_summary.py` is the downstream consumer. 174 lines, `set -euo pipefail`. | The M4c1 V3+V4 follow-up has no orchestrator. Each distractor capture would need hand-rolled SSH/SCP/verify commands. | `KEEP` | Production orchestration for the V3+V4 distractor evaluation. |
| 15 | `scripts/m4c_v3v4_summary.py` | Combine per-distractor `filter_results_*.json` into a markdown table. | `scripts/README.md:41`; `docs/LOGBOOK.md` (5 refs); `scripts/m4c_v3v4_run.sh:174` (end-of-run message points here). 110 lines. | The V3+V4 results have no aggregator. Each distractor JSON has to be read by hand. | `KEEP` | Downstream of `m4c_v3v4_run.sh`; the summary the report reads. |
| 16 | `scripts/m4c_yolo_inference.py` | Run YOLO ONNX on a directory of RGB JPGs (no ROS). | `scripts/README.md:39`; `scripts/m4c_v3v4_run.sh:129` calls it; `docs/LOGBOOK.md` (3 refs). 151 lines. Letterbox + decode + NMS. | The V3+V4 pipeline has no dev-PC YOLO-on-JPGs harness. The script is the unit that produces `yolo_detections_<distractor>.json`. | `KEEP` | Production YOLO inference step for the V3+V4 evaluation. |
| 17 | `scripts/m5_analyze_bag.py` | Dev-PC bag analyzer — per-class kept counts, publish rate, RGB Hz, latency from a recorded bag. | `scripts/README.md:48`; `docs/LOGBOOK.md` (1 ref); `evaluation/m5_live/report.md` is the consumer of its output. 190 lines. Hardcoded `WS_INSTALL` paths suggest it was once Jetson-side. | The M5 bag evidence has no aggregator. The `summary.json` and `latency.json` sidecars in `evaluation/m5_live/` become unparseable. | `KEEP` | M5 bag analysis harness — the script that produced `evaluation/m5_live/*/summary.json`. |
| 18 | `scripts/m5_capture_bag.py` | Jetson-side orchestrator — opens `ros2 bag record`, waits N seconds, pulls the bag. | `scripts/README.md:47`; `docs/LOGBOOK.md` (2 refs). 97 lines, well under the others. | The M5 evidence has no live-capture harness. The bags in `evaluation/m5_live/*.db3` (gitignored) would not exist. | `KEEP` | M5 live capture harness. |
| 19 | `scripts/m5_offline_replay.py` | Replay the M5 pipeline on saved sync RGB+depth (no ROS, dev-PC ONNX). | `scripts/README.md:49`; `scripts/README.md` and `docs/LOGBOOK.md` call this the parity-check harness. **No LOGBOOK reference.** 204 lines. | If the live M5 results are ever questioned, this is the reproducibility harness. | `KEEP` | Production parity-check for M5 before live runs. |
| 20 | `scripts/m5_parse_latency.py` | Parse the per-100-frame latency lines from `node.log` into structured JSON. | `scripts/README.md:50`; `docs/LOGBOOK.md` (1 ref); `evaluation/m5_live/report.md` tables consume the parsed JSON. 111 lines, regex-driven. | The M5 latency numbers in the README and the report have no parser. They were hand-copied from `node.log`. | `KEEP` | M5 latency parser. |
| 21 | `scripts/normalize_dataset.py` | Convert Roboflow YOLOv5 *segmentation* export → *detection* format (polygon→bbox, class-name remap). | `scripts/README.md:64`; `docs/LOGBOOK.md` (2 refs); `docs/learn/learning-records/0003-external-dataset-gotchas.md:5` cites it as the fix; `docs/model-options.md` describes the polygon-vs-detection gotcha. 159 lines. | The M2 fine-tune would have to be re-derived from raw Roboflow export. The M2 mAP@0.5=0.954 result depends on this normalization. | `KEEP` | M2 dataset normalization — without it the Roboflow export would have failed silently. |
| 22 | `scripts/_peek_bboxes_once.py` | One-shot live RGB peek with bbox overlay + per-frame JSON dump. Jetson-side rclpy + ONNX. | `scripts/README.md:81`; **1 LOGBOOK reference** (the M4c1 follow-up session). 180 lines. Includes imports for `rclpy`, `onnxruntime`, `cv_bridge`. | M4c1 distractor inspection has no peek tool. | `MOVE` (to `scripts/dev_helpers/`) | Per M7c rule. The M4c1 follow-up is done; this is a development helper. |
| 23 | `scripts/_summarize_carton.py` | One-shot: summarize carton YOLO + filter results (counts, conf stats, bbox dump). | `scripts/README.md:82`; **1 LOGBOOK reference** (carton distractor session). 41 lines, hardcoded path to `evaluation/m4c_geometry_filter/`. | If the carton distractor numbers need re-checking, the script is the fastest way. | `MOVE` (to `scripts/dev_helpers/`) | Per M7c rule. The carton summary is now in `evaluation/m4c_geometry_filter/v3_v4_summary.md` (written by `m4c_v3v4_summary.py`); this script is redundant. |
| 24 | `scripts/_summarize_cup.py` | One-shot: summarize cup YOLO + filter results. | `scripts/README.md:83`; **0 LOGBOOK references** (per grep). 61 lines, hardcoded paths. | The cup distractor summary is in `v3_v4_summary.md`. | `MOVE` (to `scripts/dev_helpers/`) | Per M7c rule. Same redundancy as #23. |
| 25 | `scripts/_summarize_tall_cyl.py` | One-shot: summarize tall_cyl YOLO + filter results. | `scripts/README.md:84`; **1 LOGBOOK reference**. 88 lines, slightly more elaborate (handles latencies, kept samples). | The tall_cyl summary is in `v3_v4_summary.md`. | `MOVE` (to `scripts/dev_helpers/`) | Per M7c rule. Same redundancy as #23. |
| 26 | `scripts/test_inference.py` | M4b: run TensorRT FP16 engine on saved JetRover camera frames; produces per-frame annotated PNGs + `detections.json` with engine latency. | `scripts/README.md:25`; `docs/milestones.md:84` cites `scripts/test_inference.py` for M4b; `docs/LOGBOOK.md` (6 refs). 346 lines — the second-largest script. Includes the in-process pycuda/stream workaround for the helper-decomposition bug. | The M4b evidence (30 frame-hit rate, 26.6 ms median latency) has no harness. A future ONNX→engine conversion would have no benchmark. | `KEEP` | Production M4b inference harness. |
| 27 | `scripts/validate_hardneg.py` | M3c post-fine-tune validation — run `models/best_hardneg.pt` on saved frames, compare to M4b `detections.json`, produce a before/after FP table. | `scripts/README.md:67`; `docs/LOGBOOK.md` (0 direct filename refs per strict grep). 155 lines. | If `t_13b658c2` is re-opened (the M3d-revived plan), this is the validation harness. | `KEEP` | Active template for the M3d-revived validation step. |
| 28 | `scripts/verify_camera_samples.py` | Dev-PC sidecar SHA-256 + count checker for captured samples. | `scripts/README.md:58`; `docs/LOGBOOK.md` (9 refs); `scripts/m4c_v3v4_run.sh:122` calls it inline. 53 lines, simple and standalone. | Every `camera_samples` capture loses its SHA-256 verification path. The sidecar JSONs in `evaluation/camera_samples/` would not be trustworthy. | `KEEP` | Production capture-verification step. |

---

## Notes on the two stubs (`export_onnx.py`, `convert_tensorrt.py`)

Direct file inspection (lines 1–13 for `export_onnx.py`, lines 1–10 for `convert_tensorrt.py`)
shows both are stubs:

```python
# scripts/export_onnx.py
"""Export YOLOv5 weights to ONNX format (Milestone 3).

Default: export Roboflow pretrained best.pt. Re-run after optional local fine-tune.
"""

def main():
    pass

if __name__ == '__main__':
    main()
```

The M0 export chain that produced `models/best.onnx` and `models/best.engine` was:

1. `best.pt → best.onnx`: done with `ultralytics.YOLO('models/best.pt').export(format='onnx', imgsz=640, opset=13)` in a Jupyter cell (per `models/README.md` M3 entry and `docs/milestones.md:71-77`). **Not via `export_onnx.py`.**
2. `best.onnx → best.engine`: done with `/usr/src/tensorrt/bin/trtexec --onnx=best.onnx --saveEngine=best.engine --fp16 --workspace=2048` on the Jetson (per `docs/milestones.md:94-95`). **Not via `convert_tensorrt.py`.**

The two stubs document the *intended* interface for these steps; they are not the code that did the work. The M7b audit (which classified both as "KEEP") was correct to keep them but did not call out the stub status. The M7c verdict for both is to keep them as historical placeholders — `KEEP-HISTORICAL` for `export_onnx.py` (it is cited in `scripts/README.md` and `docs/technical-stack.md` M0 chain) and `KEEP` for `convert_tensorrt.py` (same reasoning). A follow-up card should either (a) implement them, or (b) delete them and remove the `scripts/README.md` references. This is Maher's call.

---

## Notes on `docs/learn/*` (six NEEDS MAHER DECISION rows)

Per the M7c card's strict rule, the default for `docs/learn/*` is `NEEDS MAHER DECISION` or `MOVE`, not automatic `KEEP`. The M7a author (in `docs/README.md:90-95`) already labels this folder as "Learning notes (personal study) ... not part of the project deliverable" and routes visitors away from it.

The M7c audit does not delete the folder — that is Maher's decision. Three plausible options:

- **Option A — keep as-is.** The current `docs/README.md:90-95` routing note already exists. Cost: 8 files / ~36 KB + 6 extra entries in the file index. Benefit: preserves the lessons.
- **Option B — move to `~/maher_ws/learn/` (sibling of the workspace).** Maher's `docs/learn/learning-records/0002-workspace-relocated.md` documents why the workspace was originally moved *into* the repo; reversing that decision is also a legitimate call.
- **Option C — delete.** If Maher no longer uses the lessons, the cheapest cleanup is to delete them and remove the routing paragraph from `docs/README.md`.

Per the M7c rule, I do not pick one. I flag the six `docs/learn/*` rows as `NEEDS MAHER DECISION`.

Of the eight files in `docs/learn/`:

- Six are unreservedly personal study (`MISSION.md`, `NOTES.md`, `RESOURCES.md`, `learning-records/0001`, `learning-records/0002`, `lessons/0001-what-yolo-outputs.html`, and the two `assets/` files which only exist for the lesson HTML).
- Two carry project-relevant content (`learning-records/0003-external-dataset-gotchas.md` and `reference/m2-implementer-handoff.md`), but the framing is personal-study. If Maher wants the project-relevant content to survive, the right move is to fold it into `scripts/normalize_dataset.py` (as a docstring block) or `models/README.md`, not to keep the personal-study file.

---

## Notes on the six underscore-prefixed scripts (six MOVE rows)

Per the M7c card's strict rule, the default for `_underscore-prefixed` scripts is `MOVE` to `scripts/dev_helpers/`, not automatic `KEEP`. The six candidates are:

- `_cleanup_inspect.py` — 9 lines, hardcoded path, not even in Git.
- `_inspect_tall_cyl_schema.py` — 18 lines, dumps JSON schema.
- `_peek_bboxes_once.py` — 180 lines, Jetson-side rclpy peek tool.
- `_summarize_carton.py` — 41 lines, redundant with `m4c_v3v4_summary.py` output.
- `_summarize_cup.py` — 61 lines, redundant with `m4c_v3v4_summary.py` output.
- `_summarize_tall_cyl.py` — 88 lines, redundant with `m4c_v3v4_summary.py` output.

All six are M4c1-era development helpers. The `m4c_v3v4_summary.py` script produces `evaluation/m4c_geometry_filter/v3_v4_summary.md` which is the canonical V3+V4 summary; the three `_summarize_*.py` scripts are pre-aggregator one-offs.

The M7c verdict for all six is `MOVE` (to `scripts/dev_helpers/`). The mechanical refactor is: `git mv scripts/_*.py scripts/dev_helpers/`, then update `scripts/README.md` to point at the new path, then update the 5 LOGBOOK references. No script is deleted; no behavior changes.

---

## Approval checklist for Maher

This section groups the per-file recommendations into decisions you can approve or reject as a set.

### A. DELETE now
**None.** Zero files have a `DELETE` recommendation.

### B. MOVE now (6 scripts → `scripts/dev_helpers/`)
- `scripts/_cleanup_inspect.py`
- `scripts/_inspect_tall_cyl_schema.py`
- `scripts/_peek_bboxes_once.py`
- `scripts/_summarize_carton.py`
- `scripts/_summarize_cup.py`
- `scripts/_summarize_tall_cyl.py`

Mechanical refactor: `git mv` + update `scripts/README.md` + update 5 LOGBOOK references. No behavior change.

### C. KEEP-HISTORICAL (5 files — already evidence of past decisions)
- `docs/model-options.md` (M2 source decision)
- `docs/model-alternative-research.md` (M3c2 alternatives)
- `docs/model-hard-negative-plan.md` (M3c plan, source of M4c1 design)
- `docs/model-objectness-addendum.md` (M3c3 addendum, source of geometry-filter design)
- `docs/repo-cleanup-audit.md` (M7b predecessor audit, kept for audit trail)

These five are not deleted because deleting them breaks the audit trail that `m3d-revived-plan.md` and `evaluation/m4c_geometry_filter/report.md` reference.

### D. DECIDE about `docs/learn/` (10 files — Maher's call)
- `docs/learn/MISSION.md`
- `docs/learn/NOTES.md`
- `docs/learn/RESOURCES.md`
- `docs/learn/learning-records/0001-workspace-established.md`
- `docs/learn/learning-records/0002-workspace-relocated.md`
- `docs/learn/learning-records/0003-external-dataset-gotchas.md`
- `docs/learn/lessons/0001-what-yolo-outputs.html`
- `docs/learn/reference/m2-implementer-handoff.md`
- `docs/learn/assets/lesson.css`
- `docs/learn/assets/quiz.js`

(Ten files; two are `assets/` which only exist if the lessons stay.) Options:

- **Option A:** keep as-is. `docs/README.md:90-95` already routes visitors away.
- **Option B:** move to `~/maher_ws/learn/`. The original 2026-06-24 location.
- **Option C:** delete. The `learning-records/0003` and `reference/m2-implementer-handoff` content can be folded into `scripts/normalize_dataset.py` docstring and `models/README.md` respectively.

### E. DECIDE about the two stubs (2 scripts — Maher's call)
- `scripts/export_onnx.py` (13-line stub)
- `scripts/convert_tensorrt.py` (10-line stub)

Both document the intended interface for the M0 export chain but were never the code that did the work (`ultralytics.YOLO().export()` and `trtexec` were). Options:

- **Option A:** keep as-is (current verdict: `KEEP-HISTORICAL` / `KEEP`).
- **Option B:** implement them properly (replace the `pass` with the `ultralytics.YOLO().export()` call and a `trtexec` subprocess wrapper).
- **Option C:** delete them and remove the `scripts/README.md` references.

### F. NO ACTION (30 files — keep as-is)
All canonical docs and all production scripts. Specifically:

- **Docs (9):** `architecture.md`, `Concept-and-Approach.md`, `evaluation.md`,
  `LOGBOOK.md`, `m3d-revived-plan.md`, `milestones.md`, `project-definition.md`,
  `docs/README.md`, `technical-stack.md` — plus the 5 `KEEP-HISTORICAL` model-* docs
  and `repo-cleanup-audit.md` from §C.
- **Scripts (21):** `build_hardneg_dataset.py`, `capture_frames.py`,
  `capture_rgb_depth_sync.py`, `check_empty_scene.py`, `convert_tensorrt.py` (stub,
  see §E), `_download_weights.py`, `finetune_hardneg.py`, `m3_smoke_inference.py`,
  `m4a_trt_smoke_inference.py`, `m4c_geometry_filter.py`, `m4c_v3v4_run.sh`,
  `m4c_v3v4_summary.py`, `m4c_yolo_inference.py`, `m5_analyze_bag.py`,
  `m5_capture_bag.py`, `m5_offline_replay.py`, `m5_parse_latency.py`,
  `normalize_dataset.py`, `test_inference.py`, `validate_hardneg.py`,
  `verify_camera_samples.py`, plus `export_onnx.py` (stub, `KEEP-HISTORICAL`, see §E).

(20 KEEP + 1 KEEP (with note) among the scripts = 21 production scripts. `convert_tensorrt.py`
is split across §E and §F because the M7c verdict on it is "keep, but call out the stub
status" — it lives in §E for the call-out and §F for the action.)

---

## Final tally

|| Recommendation | Docs | Scripts | Total |
||---|---:|---:|---:|
|| `KEEP` | 9 | 21 | 30 |
|| `KEEP-HISTORICAL` | 5 | 1 | 6 |
|| `MOVE` (to `scripts/dev_helpers/`) | 0 | 6 | 6 |
|| `DELETE` | 0 | 0 | 0 |
|| `NEEDS MAHER DECISION` | 10 | 0 | 10 |
|| **Total** | **24** | **28** | **52** |

This tally was verified by parsing the table cells with a small script
(`/tmp/m7c_count.py`; row-by-row scan, splitting on unescaped pipes). The 10
`docs/learn/*` files marked `NEEDS MAHER DECISION` are: `MISSION.md`, `NOTES.md`,
`RESOURCES.md`, `learning-records/0001-workspace-established.md`,
`learning-records/0002-workspace-relocated.md`, `learning-records/0003-external-dataset-gotchas.md`,
`lessons/0001-what-yolo-outputs.html`, `reference/m2-implementer-handoff.md`, plus the
two `assets/` files (`lesson.css`, `quiz.js`). The 5 `KEEP-HISTORICAL` docs are the
four `model-*.md` files plus `repo-cleanup-audit.md`.

Total files audited: **52** (24 docs + 28 scripts). All 24 docs and all 28 scripts in
the M7c card body appear exactly once in the Documents and Scripts tables.

---

## Appendix: how the evidence was gathered

For each file in the M7c card body, this audit verified:

1. **Existence** — `ls -la` against the live tree at `main` (ahead 12, no push).
2. **Size + line count** — `wc -l docs/*.md scripts/*.py scripts/*.sh`.
3. **First 35 lines of each script** — argparse, docstring, imports. For example,
   `scripts/convert_tensorrt.py` is 10 lines total, all visible in one read; the
   `def main(): pass` body is what flags it as a stub.
4. **Cross-reference count** — `grep -c "<path>" docs/LOGBOOK.md` per script
   (the strict-filename count; M7b used a looser regex).
5. **Cross-reference check from the README** — `README.md:223-273` has a Documentation
   section that links each canonical doc.
6. **Script README** — `scripts/README.md` has a row for every script with a one-liner.
7. **Doc README** — `docs/README.md:23-67` has a row for every canonical doc, plus a
   "Research and history" section for the `model-*.md` files.

No file was modified, deleted, moved, or rewritten during this audit. The card body's
constraints were respected:

- No destructive changes.
- No model artifacts touched.
- No vendor packages touched.
- `t_1124e5e0` (M3d-revived fine-tune) was not unblocked.
- No push to GitHub.