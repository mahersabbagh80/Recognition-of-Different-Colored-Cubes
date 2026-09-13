# Revision 6 — fundamentals and methods before results

Prepared in response to Maher's first presentation feedback. This is the next review draft, not an assertion that Maher has accepted the revised presentation.

| Slide | Topic | Purpose |
|---:|---|---|
| 1 | Project title | Introduce live colored-cube detection on NVIDIA Jetson |
| 2 | Computer vision fundamentals | Explain color classes, bounding boxes, and the separate role of depth |
| 3 | System architecture | Retain the existing camera-to-output architecture |
| 4 | Research and method choices | Explain pretrained YOLO, own-camera examples, and separate validation scenes |
| 5 | Training workflow | Capture, review labels, split scenes, fine-tune; explain the learning loop |
| 6 | Validation workflow | Run inference, compare with labels, count errors, select a checkpoint |
| 7 | Deployment workflow | Move the existing PyTorch–ONNX–TensorRT–ROS 2 flow earlier |
| 8 | Dataset and training outcomes | Summarize the exported dataset and selected checkpoint without dense plots |
| 9 | Validation results | Show the missed red cube and distinguish visible counts from automated metrics |
| 10 | Live results | Present the saved red-cube screenshot and documented live observations |
| 11 | Remaining limitation | Explain the geometry-filter rejection and what remains unverified |
| 12 | Conclusion | State the demonstrated result and the next engineering step |

## Changes from version 5

The opening no longer presents performance results. Its image is explicitly an approved-label example that illustrates the task. The old slide 4 smoke-result montage is replaced by method reasoning. The old label-distribution plot and training-curve montage are replaced with a concise later summary. The training and validation diagrams are editable slide objects. The system architecture remains slide 3, and the deployment diagram moves from slide 9 to slide 7. English speaker notes were regenerated in the new order, with sources for the research decisions.

## Research basis

- [Training and validation methodology review](../../../docs/training-validation-methodology-review.md): different examples for weight learning and model selection; avoid splitting neighboring frames across roles.
- [Capture checklist](../../../docs/indoor-cube-capture-checklist.md): targeted camera scenes and human review.
- [Architecture](../../../docs/architecture.md): existing Jetson/TensorRT/ROS 2 integration and why the learned detector is the main path.
- The primary transfer-learning and evaluation references from the methodology review are listed in slide 4's notes.

Historical alternative-model research contains superseded recommendations and unverified comparative estimates. Those are not promoted into current performance claims. The deck explains why the chosen method fits this project without claiming it is universally the best detector.

## Review record

All 12 rendered slides were inspected individually. PowerPoint package and layout checks passed. The PDF is a static copy of the final slide renders. The small one-room validation set and incomplete geometry-filtered localization remain visible limitations. No new training or evaluation was run for this revision.
