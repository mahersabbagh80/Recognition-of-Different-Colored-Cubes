# Milestones

Current status: 13 September 2026. Detailed evidence is in the [daily journal](development-learning-journal.md); earlier milestones retain their historical evidence in the [logbook](LOGBOOK.md).

## Goal

Recognize blue, green and red cubes in a live indoor camera view on NVIDIA Jetson hardware, publish their detections through ROS 2, and verify useful depth-based location. Intended range is 20–80 cm. Navigation, manipulation and production monitoring are outside scope.

| Milestone | Status | Evidence and remaining boundary |
|---|---|---|
| M1 — Environment | Verified for September live test | Vendor camera, ROS environment and workspace worked. Desktop rqt discovery remains unresolved; browser preview worked. |
| M2 — Model weights | Completed candidate | General pretrained YOLOv5u-small fine-tuned on 23 images, 8 held-out validation images. |
| M3 — ONNX export | Completed | Static export transferred and checksum verified. |
| M4 — Jetson inference | Completed initial checks | TensorRT 8.6.2 engine built; one saved-image conversion check completed. |
| M5 — ROS 2 live node | Partial acceptance | New engine ran live; three colors detected with filter off. Filter on rejected genuine cubes. |
| M6 — Final demonstration/evaluation | Limited demonstration completed | Broad reliability, full-range coverage and depth localization remain unverified. |
| M7 — Documentation | Current completed-work record prepared | Presentation v8, methods, evidence, commands and limitations documented; future tests will need new entries. |

## Next engineering work — not performed

1. Save aligned RGB/depth evidence and diagnose why real cube candidates fail geometry checks.
2. Verify location output separately from visible color boxes.
3. Repeat predefined cube/background scenes across the intended distances and conditions.
4. Measure complete-system timing and per-class detection errors on untouched test scenes.
5. Update acceptance status from those results.

The earlier proposed accuracy/frame-rate targets are not recorded as passed. A successful single-frame demonstration and synthetic engine benchmark do not establish full-system acceptance. See [evaluation](evaluation.md) and [project definition](project-definition.md).
