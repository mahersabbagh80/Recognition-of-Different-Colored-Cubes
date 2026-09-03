# Milestones

This file is a short roadmap, not a second logbook. Detailed commands, measurements,
decisions, and failure analysis belong in [`LOGBOOK.md`](LOGBOOK.md). The user-facing
setup and run instructions belong in [`../README.md`](../README.md).

## Project goal

Detect these three classes from the JetRover camera and make the detections available
through ROS 2:

- `red_cube`
- `green_cube`
- `blue_cube`

The project is finished when the model detects the cubes reasonably reliably in the
room and the live ROS 2 demonstration works. Navigation, manipulation, tracking, and
production monitoring are out of scope.

## Fixed boundaries

- Model: YOLOv5s
- Export path: `best.pt` → `best.onnx` → TensorRT FP16 `best.engine`
- Platform: Ubuntu 22.04, ROS 2 Humble, HiWonder JetRover
- Input: `/depth_cam/rgb/image_raw`
- Outputs: `/cube_detections`, `/cube_detections/vendor_objects`, and
  `/cube_detections/debug_image`
- Vendor packages and vendor files remain reference-only and must not be modified.
- Fine-tuning is conditional: use it only if the existing model is not reliable on
  the actual room images.

## Status

| Milestone | Status | Meaning |
|---|---|---|
| M1 — Environment | Complete | Camera topic, ROS 2 package, and required runtime environment were verified. |
| M2 — Model weights | Complete | `models/best.pt` was produced and verified. |
| M3 — ONNX export | Complete | `models/best.onnx` was exported and checked. |
| M4 — Jetson inference | Complete* | TensorRT inference works on the Jetson and on saved robot-camera images. *This does not prove reliable detection in the final room setup. |
| M5 — ROS 2 live node | Partial | The node runs and publishes, but the current model does not reliably detect the room cubes. |
| M6 — Final demonstration | Pending | Confirm reasonable detection of all three classes on representative room images and in the live ROS 2 view. |
| M7 — Documentation | Ongoing | Keep the project understandable and record the final result honestly. |

The current blocker is model accuracy on the real room scene, not ROS 2 wiring or
TensorRT execution. The 2026-06-28 live test recorded `0/460` kept detections at
confidence `0.50`; at `0.25`, only a small number of green detections appeared.
See the corresponding `LOGBOOK.md` entry and `evaluation/m5_live/report.md` for the
full evidence.

## Short path to completion

1. Test the current model on representative room images.
2. If it is reliable enough, keep the model and continue to the live demonstration.
3. If it is not reliable enough, fine-tune with a small set of representative room
   images, then repeat the export chain and live test.
4. Verify the three ROS 2 output topics and the annotated debug image.
5. Record the final result, limitations, and the exact model artifact in the logbook.

## Definition of done

- `red_cube`, `green_cube`, and `blue_cube` are detected with reasonable reliability
  in the intended room setup.
- The detector runs live from the JetRover camera.
- Detections are visible through the ROS 2 output and debug-image topics.
- The model path and run command are documented in `README.md`.
- The final result is recorded in `LOGBOOK.md`.
