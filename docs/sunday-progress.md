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

Confirm the remaining session time and inspect the 98-image inventory and existing annotation gallery. Review and integrate useful evaluation work, then prioritize annotation and session-separated training/validation data. Keep the pipeline check brief. Confirm the proposed measurement targets before using them as acceptance criteria.

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
