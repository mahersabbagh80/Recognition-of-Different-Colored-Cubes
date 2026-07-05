# Documentation index

Index for every document under `docs/`. The repo's top-level [`README.md`](../README.md)
is the visitor entry point; this file is the developer / contributor entry point.

Last updated: 2026-07-05 (repo cleanup).

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

## Current project docs (canonical)

| Doc | What it owns |
|---|---|
| [`Concept-and-Approach.md`](Concept-and-Approach.md) | Why YOLOv5 + TensorRT; model strategy. |
| [`architecture.md`](architecture.md) | Pipeline diagram, ROS 2 topics, node/topic table. |
| [`technical-stack.md`](technical-stack.md) | ROS 2 distro, Python, OpenCV, TensorRT, ONNX, export chain. |
| [`milestones.md`](milestones.md) | M1–M7 with ordered steps and current status per step. |
| [`evaluation.md`](evaluation.md) | 50-frame structured test protocol, per-class pass criteria. |
| [`vendor-audit.md`](vendor-audit.md) | Which HiwWonder vendor packages we touch vs reference only. |
| [`m3d-revived-plan.md`](m3d-revived-plan.md) | Active fine-tune plan (positive-detection scope on real JetRover-room cubes). |
| [`LOGBOOK.md`](LOGBOOK.md) | Chronological session log; entry template included. |

## Archive (research and history)

Superseded plans and decision research live in [`archive/`](archive/README.md).
Do not edit them as current truth.

## Evaluation evidence

Reports live next to the artifacts they describe (under `evaluation/`).
The docs/ folder only holds the cross-cutting protocol.

| Doc | Notes |
|---|---|
| [`evaluation.md`](evaluation.md) | Protocol only; actual reports live in `evaluation/*/report.md`. |

Per-milestone evidence:

- M4c1 distractor gate → [`evaluation/m4c_geometry_filter/report.md`](../evaluation/m4c_geometry_filter/report.md)
- M5 live evaluation (PARTIAL verdict) → [`evaluation/m5_live/report.md`](../evaluation/m5_live/report.md)
- Earlier M2/M3 checks → `evaluation/m2-visualizations/`, `evaluation/m3c_predictions/`, `evaluation/m3c_roboflow_valid/`

## Current status — M5 PARTIAL, M3d-revived next

The M5 ROS 2 pipeline + M4c1 geometry filter are **implemented and live on
the Jetson**. On 2026-06-28, two 30s live bags were captured:

| Bag | KEEP at conf=0.50 | Verdict |
|---|---|---|
| Empty scene | 0/439 | PASS — no false positives on the bare JetRover floor |
| Cubes in frame (sticker-on, M5c) | 0/414 | FAIL — model did not fire on the cubes |
| Cubes in frame (sticker-off, M5c2) | 0/460 | FAIL — same scene, sticker removed, still zero |
| Cubes in frame (sticker-off, conf=0.25) | 2/439 (green only) | FAIL — partial response only |

**M5 acceptance is PARTIAL.** The geometry filter works; the blocker is model
accuracy on real JetRover-room cubes at 60–80 cm distance.

**Next step:** fine-tune `models/best.pt` on real positive samples per
[`m3d-revived-plan.md`](m3d-revived-plan.md), then re-run the M5c2 bag.

## Learning notes (personal study)

`docs/learn/` holds personal study materials. Not part of the project
deliverable — skip unless you want the rationale behind my approach.
