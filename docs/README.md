# Documentation index

Index for every document under `docs/`. Use this when you don't know where a
topic lives. The repo's top-level [`README.md`](../README.md) is the visitor
entry point; this file is the developer / contributor entry point.

Last updated: 2026-07-05 (M7a repo hygiene pass).

---

## Start here

| Doc | Read it when you want to... |
|---|---|
| [`README.md`](../README.md) | ...see the visitor-facing summary, build/run instructions, runtime parameters. |
| [`project-definition.md`](project-definition.md) | ...understand the problem, success criteria, scope/non-goals, hard constraints. |
| [`milestones.md`](milestones.md) | ...see the M1–M7 plan and the ordered steps inside each milestone. |
| [`LOGBOOK.md`](LOGBOOK.md) | ...read the chronological session log (newest entry at the top). |
| [`architecture.md`](architecture.md) | ...see the pipeline, ROS 2 topics, and node diagram. |
| [`technical-stack.md`](technical-stack.md) | ...see runtime versions, dependencies, model-export chain. |
| [`evaluation.md`](evaluation.md) | ...see the 50-frame evaluation protocol. |

## Current project docs (canonical, kept up to date)

These are the live sources of truth for the project. Update them as the
project moves; they are referenced from the README and from each other.

| Doc | What it owns |
|---|---|
| [`Concept-and-Approach.md`](Concept-and-Approach.md) | Why YOLOv5 + TensorRT; the model strategy (pretrained first, local fine-tune only if accuracy fails). |
| [`architecture.md`](architecture.md) | Pipeline diagram, ROS 2 topics, node/topic table. |
| [`technical-stack.md`](technical-stack.md) | ROS 2 distro, Python, OpenCV, cv_bridge, TensorRT, ONNX, model export chain. |
| [`milestones.md`](milestones.md) | M1–M7 with ordered steps and current status per step. |
| [`evaluation.md`](evaluation.md) | 50-frame structured test protocol, per-class pass criteria. |
| [`vendor-audit.md`](vendor-audit.md) | Which Hiwonder vendor packages we touch vs reference only. |
| [`m3d-revived-plan.md`](m3d-revived-plan.md) | The active fine-tune plan (positive-detection scope on real JetRover-room cubes). |
| [`LOGBOOK.md`](LOGBOOK.md) | Chronological session log; entry template included. |

## Research and history (do not edit as current truth)

These were written at specific points during the project. They are kept
because they explain *why* we made earlier decisions and what we ruled
out, but they are not live sources of truth. If a question is answered
in both a research doc and a current doc, the current doc wins.

| Doc | Why it still exists |
|---|---|
| [`model-options.md`](model-options.md) | Early comparison of detection approaches (YOLOv5 vs alternatives). Superseded in practice by the chosen stack. |
| [`model-alternative-research.md`](model-alternative-research.md) | Deeper dive into non-YOLO alternatives that were ruled out. Keep for portfolio evidence of the decision process. |
| [`model-objectness-addendum.md`](model-objectness-addendum.md) | An addendum that considered objectness scores as a fallback. The geometry filter made this moot. |
| [`model-hard-negative-plan.md`](model-hard-negative-plan.md) | The original hard-negative fine-tune plan. Replaced in M4c1 by the geometry filter + conf=0.50 (passed live 2026-06-28). The residual positive-detection gap is what `m3d-revived-plan.md` covers. |

## Evaluation evidence

Reports live next to the artifacts they describe (under `evaluation/`).
The docs/ folder only holds the cross-cutting protocol.

| Doc | Notes |
|---|---|
| [`evaluation.md`](evaluation.md) | Protocol only; the actual reports live in `evaluation/*/report.md`. |

For per-milestone evidence see:

- M4c1 distractor gate → [`evaluation/m4c_geometry_filter/report.md`](../evaluation/m4c_geometry_filter/report.md)
- M5 live evaluation (PARTIAL verdict) → [`evaluation/m5_live/report.md`](../evaluation/m5_live/report.md)
- Earlier M2/M3 checks → `evaluation/m2-visualizations/`, `evaluation/m3c_predictions/`, `evaluation/m3c_roboflow_valid/`

## Current status — M5 PARTIAL, M3d-revived next

The M5 ROS 2 pipeline + M4c1 geometry filter are **implemented and live on
the Jetson** (29 runtime parameters, TensorRT FP16 engine loads,
`sync_slop_sec = 0.05` median RGB+depth pairing). On 2026-06-28, two 30s
live bags were captured:

| Bag | KEEP at conf=0.50 | Verdict |
|---|---|---|
| Empty scene | 0/439 | PASS — no false positives on the bare JetRover floor |
| Cubes in frame (sticker-on, M5c) | 0/414 | FAIL — model did not fire on the cubes |
| Cubes in frame (sticker-off, M5c2) | 0/460 | FAIL — same scene, sticker removed, still zero |
| Cubes in frame (sticker-off, conf=0.25) | 2/439 (green only) | FAIL — partial response only |

**M5 acceptance is PARTIAL.** The geometry filter does its job (it
correctly rejects flat-floor and aspect-ratio distractors). The blocker
is model accuracy on real JetRover-room cubes at 60-80 cm distance.

**Next step:** fine-tune `models/best.pt` on real positive samples per
[`m3d-revived-plan.md`](m3d-revived-plan.md), then re-run the M5c2 bag.
This is tracked on the active kanban card (not in this repo).

## Learning notes (personal study)

`docs/learn/` holds my own study materials (Ros2 / ML / robotics
fundamentals), lesson HTML, and learning records. These are personal and
not part of the project deliverable. Skip them unless you are looking
for the rationale behind my approach.

## Recommended later cleanup (not done in this pass)

These are noted here so they don't get forgotten, but they were
deliberately left for a follow-up card. Do not act on them without
opening a new kanban task.

- `scripts/` has 28 tracked files in one flat folder (27 .py + 1 .sh). Six of them
  (`_cleanup_inspect.py`, `_inspect_tall_cyl_schema.py`,
  `_peek_bboxes_once.py`, `_summarize_carton.py`, `_summarize_cup.py`,
  `_summarize_tall_cyl.py`) are dev/debug helpers used once for the
  M4c1 distractor analysis. Consider moving the underscore-prefixed
  helpers into a `scripts/dev_helpers/` subfolder after the next
  release.
- `evaluation/_m2m3_verify.py` and `evaluation/_m2m3_verify_results.json`
  are tracked at the top of `evaluation/` but are already excluded by
  the `evaluation/_*.py` and `evaluation/_*.json` rules in
  [`.gitignore`](../.gitignore). They are stale local-test leftovers
  and could be removed from git in a future cleanup.
- Some `evaluation/m5_live/cubes_2026-06-28/peek_debug_*.png` and
  `peek_rgb_*.png` images are M5 reviewer re-runs. They are tracked
  intentionally as evidence; do not delete without a replacement plan.
- The M4c1 evidence is large. If the fine-tune card (`m3d-revived`)
  re-uses the M4c1 distractor samples unchanged, consider archiving the
  per-distractor annotated PNGs to a release tag rather than leaving
  them on the working branch.