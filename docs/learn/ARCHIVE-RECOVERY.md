# Recovery from the nine original lessons

Reviewed 13 September 2026. The original archive remains unchanged. The main route remains eleven training lessons, followed by four optional robot lessons. Two optional workshops recover useful additional material without repeating the original nine-lesson sequence.

| Archived lesson | Already covered in the active course | Recovery decision |
|---|---|---|
| 1 · What YOLO outputs | Task distinctions, confidence, NMS and runtime path: 1, 9, 14–15 | Keep the existing coverage; retain the original historical example in the archive. |
| 2 · How YOLO produces predictions | Box formats, IoU and suppression: 2, 9 | Workshop 16 restores candidate-grid exploration, row interpretation and staged inverse letterboxing. The grid decomposition is an explicit architecture example, not proof from output shape alone. |
| 3 · PyTorch and training | Labels, normalization, batch/epoch, gradients, schedules, checkpoint selection and transfer: 1–8, 11 | Do not duplicate the theory or old training recipe. Historical metrics remain historical. |
| 4 · Why the model fails | Domain shift and pipeline diagnosis: 6, 15 | Workshop 17 recovers controlled intervention reasoning and the limits of the sticker experiment. |
| 5 · ONNX and TensorRT | Artifact roles, precision and fallback: 15 | Workshop 17 restores the distinction among structural, smoke, numerical and task checks. |
| 6 · ROS 2 wiring | Synchronization, message flow, depth guard and source connections: 14–15 | Keep the current lessons and linked code; avoid repeating the full wiring tour. |
| 7 · Depth filtering | Alignment, units, annulus, depth statistics, sign caveat and missing-depth handling: 12–13 | Restore a concise illustrated extension in lesson 13 on selected-subset extents, aspect ratio and depth spread. Preserve original case evidence as historical, not current hardware validation. |
| 8 · Evaluation and fine-tuning | Test matrix, metrics, fixed comparisons, leakage and fine-tuning: 6, 8, 10–11 | Workshop 17 adds replay/provenance, combined acceptance gates and rollback reasoning. |
| 9 · Project walkthrough | System components spread across current lessons | Workshop 17 restores a 90-second walkthrough task with a self-review rubric. |

## Where to begin

- [Workshop 16: Follow a candidate back to the camera](lessons/0016-follow-a-candidate.html), after lesson 9.
- [Workshop 17: Check the export, then defend the result](lessons/0017-defend-the-evidence.html), after lesson 15.

The recovered controls are rebuilt using the active course styles and shared JavaScript rather than copying archive-specific assets. Required terms appear before the fresh questions. The walkthrough textbox does not automatically score factual accuracy or persist its contents.

## Evidence boundary

The decoder's transpose, class-score selection and inverse transform were checked against the current source. No model was trained, exported or evaluated during this recovery. Archived M2–M5 metrics, deployment identities and proposed next steps must not be read as the latest project state. The newer dated development journal remains the source for subsequent engineering work.

The final comparison also restored a missing lesson-15 failure-explorer branch: model boxes exist, but geometry rejects them all. It teaches inspection before/after the filter and distinguishes absent messages from a received empty array. The historical hard-negative script example is now labeled older and links to the current model inventory and dated live record.
