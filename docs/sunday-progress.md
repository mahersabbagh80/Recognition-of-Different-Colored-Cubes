# Sunday presentation — progress record

Deadline: 13 September 2026, 18:00 Europe/Berlin.
Plan: [sunday-presentation-plan.md](sunday-presentation-plan.md).

## Current status — 9 September

- Plan revised after Wednesday’s discussion. Wednesday preparation started: existing images and provisional annotations verified; training has not started.
- Budget: three hours per day from Wednesday; no Tuesday work session.
- Keep the current Codex task as the main conversation.
- Historical robot evidence and the separate September 7 offline diagnostic show unresolved detection quality. No fresh hardware run was performed for this plan.
- Existing evaluation work to review: `/home/maher/.codex/worktrees/67ee/Recognition-of-Different-Colored-Cubes/evaluation/robot_dataset_2026-09-07/report.md` and its associated evaluator, tests, annotations, and capture checklist.
- Main project contains existing unrelated edits, notably learning materials. Preserve them during integration.
- No training job or automation was started by this planning task.

## Wednesday clarification

Maher explained that his instructor requested a self-collected dataset, prompting the collection of 98 robot-camera images. The new training path uses reviewed self-captured data and a compatible general pretrained checkpoint, not the earlier model fine-tuned on external cube images. Verify the starting checkpoint before execution. Maher subsequently explicitly requested removal of the old model. Local artifacts were deleted as recorded below; no retraining or deployment has occurred. General pretraining is distinct from the project-specific dataset requirement and will be disclosed.

## First action next session

Image review and the initial training export are complete. Verify the compatible general pretrained checkpoint and the training/export contract next; do not silently substitute a different model family. Then perform a bounded training smoke run. Read the latest daily entries for the limited same-session validation split. The latest completed step is the three-epoch smoke run; see the final entry.

## Daily entries

Append one entry after each session with:

- Date, time spent, and actual checkout/branch.
- Checkpoint: passed, failed, or incomplete; reason.
- Verified measurements and exact evidence paths.
- Changed files and checks performed.
- Model artifact identity, settings, and deployment status.
- Dataset/label review and train/validation/test allocation status.
- Remaining blocker and chosen fallback, if any.
- Running job, log path, and how to check/resume it, or “none.”
- Presentation files and what Maher practised explaining.
- First concrete action next session.

## Freeze record — pending Friday

- Model/configuration/code identity: pending.
- Startup procedure: pending verification.
- Tested demonstration conditions and limitations: pending.
- Independent test results: pending.
- Backup video and playback check: pending.
- Slides/PDF/notes and rehearsal timing: pending.

## Old model removal — 9 September

Explicitly requested by Maher. Removed the following local cube-trained artifacts and related training checkpoints. Images, labels, source code, general pretrained checkpoints, and historical training/evaluation reports were preserved. No robot or other-checkout copies were modified. The local default engine is now absent until a replacement is trained and exported.

| Removed path | Bytes | SHA-256 before removal |
|---|---:|---|
| `models/best.pt` | 18517947 | `bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04` |
| `models/best.onnx` | 36671634 | `326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21dcee829637fa38` |
| `models/best.engine` | 21354868 | `c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1` |
| `models/best_hardneg.pt` | 18517435 | `4715bb5fccee057d817d18bda366fece74e8d295c0ba4d0067e5b0e672c6a3cf` |
| `runs/m3c/m3c_25ep/weights/best.pt` | 18517435 | `4715bb5fccee057d817d18bda366fece74e8d295c0ba4d0067e5b0e672c6a3cf` |
| `runs/m3c/m3c_25ep/weights/last.pt` | 18517435 | `f4b253d5bd72ebf7657045345dde1bc9d79e785ade552df86b7b64c2bc8d9a42` |
| `runs/detect/runs/m2/m2_30ep/weights/best.pt` | 18517947 | `bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04` |
| `runs/detect/runs/m2/m2_30ep/weights/last.pt` | 18517947 | `b6c95cff2c230b6b1f68a7a22f14f5435d80fd008e55ab447868eaa473da0a5d` |
| `runs/detect/runs/m2/smoke3/weights/best.pt` | 18514491 | `84e576433ac53ed6d6a213b84449da1ccd09301fddba0d48fbe33deeb98c454b` |
| `runs/detect/runs/m2/smoke3/weights/last.pt` | 18514491 | `70a9e51fbd05e33e1d785a8bf99bdd4c4e9a765bab3d3c88fd182c7a8e525252` |

## Wednesday first checkpoint

Confirmed 98 saved JPGs. Verified all 13 provisionally annotated source images against their recorded hashes. Prepared a self-contained review gallery at `evaluation/results/wednesday-review/index.html`, with historical model predictions hidden by default. No human label approval or training has occurred. Existing manifest assigns these images to one July capture session, so separate validation capture may be needed after provenance review. Next: human review of the background frame, then cube boxes and colors.

## Wednesday annotation checkpoint — first gallery complete

Maher confirmed all 13 images in the existing gallery: 27 cube boxes/color labels and one empty background. Confirmations saved in `evaluation/robot_dataset_2026-09-09/human_review.json`. The remaining 85 source images have not been human-reviewed or labeled by this task. No training has started. Next: assess the remaining images and capture-session provenance, prepare additional annotations, and establish a defensible training/validation allocation.

## Wednesday capture provenance confirmed

Maher confirmed all 98 images came from one continuous capture session. Keep this collection together as development/training data; do not randomly split neighboring frames and claim independent validation. A distinct self-captured validation session is needed before selecting the new model. The later final test stays separate. Existing image assessment/annotation can continue without robot access.

## Wednesday variety inspection — clarification of split recommendation

Inspected contact sheets of all 98 images: useful distance, color-combination, and arrangement variation across 13 named groups, but substantial repetition within groups and broadly shared room/lighting. One session alone does not invalidate a dataset. No final split has been assigned. Whole arrangement groups could support a limited same-session validation check; separate rearranged validation captures remain recommended because the existing groups are few and repetitive. See `evaluation/robot_dataset_2026-09-09/variety-review.md`. No additional annotations were human-approved by this inspection.

## Wednesday second annotation batch prepared

Selected and visually inspected the last frame of each of the 13 capture groups: 13 additional images, 27 provisional cube annotations plus one background. Coordinates seeded from first-frame proposals and checked against full new frames and enlarged target regions; user approvals were not propagated. Gallery: `evaluation/results/wednesday-review/batch2.html`; proposed annotations: `evaluation/robot_dataset_2026-09-09/batch2-provisional.json`. Names now appear separately from numbered boxes to avoid overlapping label text. This is a compact 26-image candidate subset after approval, representing the same 13 setups, not 26 independent scenes; 72 images remain unselected. New batch human review is pending. No final data split or training yet.

## Wednesday second gallery confirmed

Maher confirmed all boxes and color labels in the second gallery. The review record now contains 26 confirmed images, 54 cube annotations, and two background frames across the same 13 capture setups. Original images are unchanged. Remaining 72 images are unselected, not implicitly annotated or approved. Second gallery status updated. Next: define a whole-setup development split, export checked training labels, verify the general pretrained checkpoint and training/export compatibility. No training run started yet.

## Wednesday training export complete

Prepared 22 training images (14 cubes per color, two empty backgrounds) and four validation images (four cubes per color). Validation holds out both reviewed frames of the 40 cm and spread-out arrangements, with all sibling frames excluded from training. This is same-session development validation only: two distinct arrangements, no empty validation scenes, no independent final-test claim. Dataset config: `evaluation/results/robot_training_2026-09-09/data.yaml`; tracked manifest: `evaluation/robot_dataset_2026-09-09/development_split.json`. Verified hash/label coverage, coordinate round trips, class mapping, and group separation. Next: verify compatible general pretrained initialization and export contract, then training smoke run. No training started.

## Development learning journal created

Added `docs/development-learning-journal.md` at Maher’s request. First entry explains actual data preparation, annotation review, one exported box, scene-group splitting, limitations, and corrected assumptions. Training and mastery are explicitly unmeasured. Add a short entry after meaningful completed steps. This documents the process without treating activity logs as demonstrated learning.

## Technical documentation purpose clarified

Maher wants an engineering walkthrough sufficient to explain implementation and decisions to his tutor, including exact executed commands, code/library roles, settings, inputs/outputs, and verification. Expanded the learning journal accordingly and recorded the partial training preflight: PyTorch 2.6.0+cu124 and Ultralytics 8.4.75 import; the first restricted-process CUDA check returned false. Cause not diagnosed. Compatible YOLOv5u-small checkpoint verification and training remain pending.

## Learning journal organized by day

Kept `docs/development-learning-journal.md` as the stable index and moved the complete existing Wednesday material into `docs/development-learning-journal/2026-09-09-wednesday.md`. Relative evidence links were adjusted and checked. Future dated documents will be added when those days’ work occurs. No existing Wednesday explanation was discarded and no future work is marked complete.

## Wednesday GPU preflight and smoke training complete

Host GPU access and a PyTorch CUDA calculation succeeded; restricted-process GPU visibility was the initial obstacle, with no driver changes required. Official YOLOv5u-small checkpoint downloaded and verified. A metadata assertion was corrected after inspecting actual depth/width multipliers. Three epochs completed on the 22/4 image split, with correct three-class saved model and output shape. Evidence: `evaluation/robot_dataset_2026-09-09/training_preflight.json`, `smoke_summary.json`, and `runs/robot_2026-09-09/smoke_3ep/`. Very poor library-reported precision (~1.42%) despite high recall (~91.67%); no fixed-threshold acceptance or live robot claim. All 18 training batches remained under the library minimum 100-iteration warm-up, so the next substantive experiment must address the schedule. Full commands/settings/results and the initial assertion failure are documented in Wednesday’s technical walkthrough. No training job remains running; no deployment. Next: controlled training configuration and fixed-confidence validation.

## Wednesday visible prediction review

Saved explicit CPU square-input predictions and threshold counts in `evaluation/robot_dataset_2026-09-09/smoke_prediction_review.json`. At 0.01: 2 correct, 20 false, 10 missed; at 0.25/0.50: none reported, all 12 missed. Saved visualization/gallery in `evaluation/results/wednesday-review/smoke-results.html`. Explained why the original library montage hides all boxes (display cutoff 0.25). Updated technical walkthrough. No retraining or deployment during this review.

## Wednesday controlled experiment completed

Fresh general YOLOv5u-small initialization, same 22/4 split, 60 epochs with AdamW lr0=0.001, warmup disabled and nbs=4 (one update per batch). Script: `scripts/run_robot_training_experiment.py`. Saved candidate: `runs/robot_2026-09-09/experiment_60ep/weights/best.pt`, SHA-256 `296663e9bdea5f7b9b7ef138654362716450947b2851078dfae464ae3bfe7984`. Reloaded classes and finite `[1,7,8400]` output passed. At predeclared confidence 0.50 using square CPU inference and same-class IoU>=0.50: TP9, FP0, FN3; blue recall50%, green75%, red100%. This remains limited same-session development evidence, below per-color recall target; no final acceptance or deployment. Commands, configuration rationale and outputs added to Wednesday walkthrough. No training job running. Next: review the missed blue/green predictions together before further experiments; independent test and robot verification remain pending.

## Wednesday missed-cube diagnosis complete

Ran `scripts/inspect_robot_experiment_misses.py` on unchanged best weights and verified reproduction of the fixed 0.50 counts. All three misses are in spread-out validation frames. Correct blue boxes have confidence0.0092/0.0310; missed green has0.4630. At0.25: TP10 FP0 FN2; at0.001: TP12 FP7 FN0. Threshold remains0.50; no acceptance claim. Original spread-out frame visually inspected. Training source blue positions are concentrated toward the center; this is a coverage observation, not a proven cause. Technical walkthrough updated with commands, evidence, interpretation and a proposed targeted capture batch. Next: obtain robot-camera access and capture deliberately varied blue/green scenes, then approve labels and allocate whole setups before another training run. No job running or deployment change.

## Thursday guided continuation — run naming

Resumed Wednesday's learning checkpoint. At Maher's suggestion, training experiments now reserve timestamped directories with numbered collision suffixes. Settings and summary are stored per run. Temporary-directory collision/preservation checks passed; no training launched. Thursday's technical walkthrough records implementation and scope limits, including existing evaluation scripts still pointing to Wednesday's candidate and shell log redirection remaining separate. Next: inspect this small change together, then continue understanding training settings.

## Thursday session handoff — Friday capture agreed

Maher is tired and plans to resume tomorrow, Friday. Wednesday's core work and explanation are complete; historical M1 camera/runtime verification is confirmed in the logbook and is not a missing Wednesday prerequisite. New-model deployment validation remains later work.

Maher agreed to try additional robot-camera photographs tomorrow and explicitly wants concrete descriptions of each scene. Begin with a manageable capture checklist specifying cube colors, placement, distance, orientation/background, and what must stay fixed or change. Guide one setup at a time; distinguish training additions, held-out development arrangements, and a later independent final test. Prioritize weak spread-out blue examples while retaining other colors and empty backgrounds. No captures have occurred and no new run is authorized merely by this handoff. Reassess available time before combining Thursday/Friday work; do not promise both fit automatically.

## Friday capture scope clarified and plan updated

Maher specified indoor photographs in his apartment, probably his room, with explicit instructions for robot placement, camera direction, cube placement/distance and background/scenery. Added this requirement and a revised Friday start message to the presentation plan. Friday begins with deferred capture/improvement work; deployment remains conditional on readiness and available time. Detailed scene checklist and captures remain pending.
