# Project definition

Updated 13 September 2026.

## Purpose and scope

Build and understand a live detector for red, green and blue cubes using an onboard indoor camera and NVIDIA Jetson hardware. Publish cube detections through ROS 2 and verify their physical location using depth. The intended distance range is 20–80 cm.

Navigation, grasping, tracking and production monitoring are outside scope. The project is also a guided engineering learning exercise: Maher captures/reviews data, runs training/deployment and interprets results, with Codex assistance.

## Classes

The actual dataset and runtime mapping is:

| ID | Label |
|---:|---|
| 0 | blue_cube |
| 1 | green_cube |
| 2 | red_cube |

This corrects the reversed red/blue mapping in the earlier definition. The code and September dataset already use the mapping above; no model or code changes were made.

## Method

Fine-tune a general pretrained YOLOv5u-small checkpoint on reviewed project images. Export through ONNX and TensorRT FP16, then run inference on Jetson. A supporting geometry filter uses depth to reject unsuitable candidates. See [rationale](Concept-and-Approach.md) and [architecture](architecture.md).

## Success and current evidence

Success requires correct colors and boxes, rejection of non-cubes, useful update speed, and verified depth/location across intended conditions. The original planning targets were at least 80% classification accuracy on a structured 50-frame test and at least 5 frames/s. They are proposals, not passed measurements; the final protocol must define detection matching, sampling and end-to-end timing.

The September live detector produced all three colors with the filter disabled. The enabled filter rejected real cubes, so the full system remains unfinished. Full-range and broader-scene reliability are unmeasured. [Evaluation](evaluation.md) separates measured results from remaining tests.

## Interfaces

RGB, depth and camera intrinsics enter cube_detection_node. Outputs are /cube_detections, /cube_detections/vendor_objects and /cube_detections/debug_image. The vendor camera infrastructure is reused without editing vendor source.

## Principal remaining risk

The geometry-filter rejection cause is unresolved. Diagnose aligned depth and the filter's assumptions before choosing a repair. The small, one-room dataset also limits generalization claims.
