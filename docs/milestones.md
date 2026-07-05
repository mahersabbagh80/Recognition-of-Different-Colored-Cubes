# Milestones

## Model strategy (one-week timeline)

**Default path:** Follow the M2 source decision in [`archive/model-options.md`](archive/model-options.md): use raw compatible Roboflow weights if Maher's account exposes them; otherwise create a local YOLOv5s `best.pt` from the approved Roboflow dataset → export ONNX → TensorRT → deploy.

**Fallback path:** If standalone inference on robot camera images is below target accuracy, fine-tune with additional robot camera images only after the first local artifact has been tested. Do not collect and annotate a custom robot dataset upfront.

TensorRT export on the Jetson is the highest schedule risk — prioritize steps 2–6 before any training work.

---

## Overview

| # | Milestone | Done when |
|---|-----------|-----------|
| M1 | Environment ready | Camera topic verified live, ROS 2 package scaffolding exists |
| M2 | Model weights ready | Verified local `models/best.pt` obtained or produced; source/access decision documented in [`archive/model-options.md`](archive/model-options.md) |
| M3 | ONNX export | `best.pt` → `best.onnx` succeeds (fine-tune first only if needed) |
| M4 | Model on Jetson | TensorRT engine running inference on saved images on Jetson |
| M5 | ROS 2 node live | Node publishing to `/cube_detections`, `/cube_detections/vendor_objects`, and `/cube_detections/debug_image` with live vendor camera feed |
| M6 | Evaluation complete | 50-frame test done, frame rate and distance range measured |
| M7 | Repository complete | README, diagram, results, clean code all committed |

---

## M1 — Environment Ready

- [x] ROS 2 package scaffolding (`recognition_of_different_colored_cubes`)
- [x] `cube_detection_node` scaffold (no inference logic)
- [x] Launch file and config placeholders
- [x] Camera topic verified live on Jetson: `ros2 topic hz /depth_cam/rgb/image_raw` ≈ 30 Hz, ~20.65 MB/s, ~0.69 MB/frame, RELIABLE QoS, `frame_id = depth_cam_color_optical_frame`, publisher `/depth_cam`
- [x] PyTorch / ONNX / TensorRT versions confirmed on Jetson: Python 3.10.12, torch 2.4.0 (CUDA 12.2, device "Orin"), onnxruntime-gpu 1.18.0 (TensorRT+CUDA providers), tensorrt 8.6.2, ultralytics 8.3.97, torchvision 0.19.0a0
- [x] `ros-humble-vision-msgs` installed on Jetson (after refreshing the expired OSRF GPG key) so the scaffold's `vision_msgs.msg` import resolves at runtime
- [x] Build + live smoke test on Jetson: `colcon build` clean in 4.75 s (exit 0); `cube_detection_node` runs for 6 s against the live vendor bringup and advertises `/cube_detections`, `/cube_detections/vendor_objects`, `/cube_detections/debug_image` (inference still a placeholder)

**Done when:** Camera topic is publishing and the package builds cleanly.

> **Details: see LOGBOOK.md entry for 2026-06-23 M1 verification** for the full test table, command transcripts, version probe output, build/runtime numbers, and carryover notes (M3 needs `pip install onnx`; M4 needs the bundled `trtexec`; dev PC needs the same OSRF key refresh + `vision_msgs` install). The raw output transcript lives on kanban card `t_639cf91d` (tester retry-3 comment).

---

## M2 — Model Weights Ready

- [x] Raw Roboflow `.pt` / `best.pt` availability checked and not available for the current account/pages (only `Deploy Model` is exposed) — see [`archive/model-options.md`](archive/model-options.md) "Implementation access check" and [`LOGBOOK.md`](LOGBOOK.md) 2026-06-24 entry
- [x] Fallback approved: train/fine-tune YOLOv5s from the approved Roboflow YOLOv5-format dataset to produce a project-owned `models/best.pt`
- [x] Save the trained artifact to `models/best.pt` and verify it loads (file exists, non-empty, Ultralytics/PyTorch load check)
- [x] Record source/training metadata and class mapping for `models/best.pt` (source dataset, license, training command, class names) in a small sidecar file or in [`LOGBOOK.md`](LOGBOOK.md)

**Done when:** A verified local `models/best.pt` exists, can be loaded, and its source/training/class metadata are recorded.

> **Details: see LOGBOOK.md 2026-06-24 M2 training entry.** The artifact is at
> `models/best.pt` (18.5 MB, SHA-256 `bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04`).
> Source dataset, normalization, training command, per-class mAP, and known
> caveats live in `models/README.md` (which also has the load + one-image
> inference sanity-check commands). Class order is `blue_cube` (0),
> `green_cube` (1), `red_cube` (2). **M2 verdict: COMPLETE.**

**Custom robot-image trigger (defer until after M4):** Add robot camera images only if standalone inference fails accuracy checks.

---

## M3 — ONNX Export

- [x] Export `best.pt` → `best.onnx` (local script on dev PC)
- [ ] **If M4 accuracy is poor:** fine-tune locally on dev PC (RTX 4070 Ti) — Roboflow dataset, 20–30 epochs, optional robot camera images — then re-export ONNX

**Done when:** `best.onnx` export succeeds without errors.

> **Details: see LOGBOOK.md entry for 2026-06-27 M3 export.** The artifact is at
> `models/best.onnx` (35.0 MB, SHA-256
> `326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21dcee829637fa38`). Export
> command, ONNX metadata (opset 13, static `1×3×640×640` input,
> `1×7×8400` output), `onnx.checker.check_model` result, and ORT smoke
> inference on a saved validation image live in `models/README.md` under
> the M3 artifact section. **M3 verdict: COMPLETE on the dev PC.**
> TensorRT FP16 engine build on the Jetson is still M4.

---

## M4 — Model on Jetson

- [x] Convert ONNX to TensorRT FP16 engine on Jetson
- [x] Run `scripts/test_inference.py` on saved images from the robot camera
- [x] Confirm detections with bounding boxes and correct class labels (30/30 frame-hit rate for all 3 classes; mean conf 0.57–0.73)
- [x] Per-class accuracy and Jetson latency recorded (median 26.6 ms/frame including annotation; 14.66 ms steady-state engine-only; 68 FPS engine budget)
- [ ] If accuracy below target → return to M3 fine-tune path, then repeat M4 (model is color-driven; FPs on green soil bag, blue package, blue decal; **recommended follow-up**: raise conf threshold to 0.50 or fine-tune on JetRover-room images — see `evaluation/m4b_predictions/report.md` §6)

**Done when:** Standalone inference detects cubes in robot camera images at acceptable accuracy.

> **M4a (engine build) — COMPLETE 2026-06-27 on the Jetson.** Artifact:
> `models/best.engine` (20.4 MB, SHA-256
> `c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1`,
> FP32+FP16 plan on Orin Nano, TensorRT 8.6.2). Built with
> `/usr/src/tensorrt/bin/trtexec --onnx=best.onnx --saveEngine=best.engine
> --fp16 --workspace=2048` (859.7 s wall time). Lightweight engine-load
> + infer check on a saved validation image returns the same 7 detections
> as the M3 ORT smoke check, with classes and confidences matching the
> best.pt class order; steady-state latency on the Orin is ~14.6 ms/frame
> (trtexec random-input benchmark: 70.47 qps, GPU compute mean 14.12 ms).
> See `docs/LOGBOOK.md` 2026-06-27 M4a entry for the full transcript and
> `models/README.md` for the artifact table.
>
> **M4b (live-camera validation) — COMPLETE 2026-06-27.** 30 saved frames
> from `/depth_cam/rgb/image_raw` (1 red + 1 green + 1 blue cube in FOV)
> inferred with `models/best.engine` on the Orin Nano. Frame-hit rate
> 30/30 / 30/30 / 30/30 for blue / green / red. Mean confidences
> 0.731 / 0.567 / 0.708. Median forward-pass latency 26.59 ms (with
> annotation), 14.66 ms pure-engine steady state. Dev-PC ORT sanity
> check on `models/best.onnx` returns matching outputs (31.58 ms median,
> CPU provider). Model over-detects on color-confusable background
> (green soil bag, blue cardboard package, blue decal); cubes themselves
> always detected with high confidence. **M4 verdict: COMPLETE for the
> M4b acceptance bar (≥50% per class); FP cleanup recommended before M5
> ships.** Full report at `evaluation/m4b_predictions/report.md`. See
> `docs/LOGBOOK.md` 2026-06-27 M4b entry for the full transcript.
>
> **M4c (depth/geometry post-filter spike) — VALIDATED 2026-06-27 on
> card `t_4fcd206e`.** Subsystem: `scripts/m4c_geometry_filter.py`
> (numpy-only, median 0.21 ms / box, 0.64 ms p95 — well under the 5 ms
> median target). Validated against a synchronised RGB+depth capture
> (30 pairs, `evaluation/camera_samples/cubes_depth_2026-06-27/`,
> gitignored, SHA-256 verified): the filter **correctly rejects all
> four named M4b flat-color distractors** (blue cardboard tissue,
> blue cardboard package, blue decal, green Uber Eats Subbag) on
> 30/30 frames and the **green bag as a raised 3D colored non-cube
> distractor** on 64/64 detections across 30 frames. The real blue
> cube is preserved on 22/29 frames (76%, below 90% target) where
> YOLO gives a full bbox; the real red cube is rejected 30/30 because
> YOLO's bbox is too tight (covers only the top face). Per-class
> conclusion: **V2 solved completely, V3 solved on the green bag
> positive control, V1 partially solved.** Phase 1 is **necessary but
> not sufficient** for M5: V3 (bottle / ball / cup / carton / cube-
> shaped non-rgb toy) needs a Maher physical session to validate,
> and V1 red-cube bbox tightness needs the M3c fine-tune
> (`t_13b658c2`) as the conditional fallback. The M3c3 addendum's
> topic name `/depth_cam/depth_registered/points` was wrong on the
> live install — the actual color-registered depth image is
> `/depth_cam/depth/image_raw` (640×360, 16UC1 mm, frame_id =
> `depth_cam_color_optical_frame`, ~30.5 Hz). Full report at
> `evaluation/m4c_geometry_filter/report.md`.

> **M4c1 follow-up (V3+V4) — ORCHESTRATION PRE-STAGED 2026-06-27 on card
> `t_980263f0`, awaiting Maher physical session.** Pipeline is wired up
> end-to-end: `scripts/m4c_v3v4_run.sh <distractor|empty|all> [date]`
> runs the capture via SSH, pulls, SHA-256 verifies, YOLO infers,
> filter runs (with the M4c1 v2-only params passed explicitly:
> `--inset-px 1 --annulus-outer-px 15`), and writes per-distractor
> outputs. `scripts/m4c_v3v4_summary.py --write-md` produces the unified
> table. `scripts/check_empty_scene.py` (uploaded to
> `/tmp/check_empty_scene.py` on the Jetson) lets Maher verify the
> floor is clear before the V4 capture. Report stub at
> `evaluation/m4c_geometry_filter/v3_v4_followup_2026-06-27.md`. **No
> new filter evidence until Maher does the physical setup** — the
> JetRover floor is currently still populated with the V1 cubes from
> the M4b/M4c1 session. Phase 1 disposition unchanged from M4c1.

---

## M5 — ROS 2 Node Live

- [x] Subscribe to vendor camera topic `/depth_cam/rgb/image_raw` — DONE 2026-06-27 (M1 verification, confirmed live 2026-06-28)
- [x] Run TensorRT inference per frame — DONE 2026-06-28 (M5 card run 82 + M5b empty-scene replay, 26.6 ms/yolo steady state)
- [x] Publish `/cube_detections`, `/cube_detections/vendor_objects`, and `/cube_detections/debug_image` — DONE 2026-06-28 (all 3 publishers registered; live verified on bag)
- [x] Add `interfaces` to `package.xml` when vendor-compatible output is implemented — DONE (vendor_objects topic publishing `interfaces/msg/ObjectsInfo`)
- [x] Visualize in RViz2 or `rqt_image_view` — PARTIAL: live `debug_image` topic publishes annotated frames (M5b empty-scene preview saved + M5c cubes-in-frame debug overlay with `keep=0`); RViz2/rqt visual not run this round
- [x] Capture empty-scene bag (KEEP=0 at conf≥0.50, M4c1 V4 PASS) — DONE 2026-06-28 (M5b, 30s sqlite3, 0/439)
- [x] Capture cubes-in-frame bag — DONE 2026-06-28 (M5c, 30s sqlite3, 0/414 at conf≥0.50 — see §11.3 for the model-accuracy analysis)

**Done when:** Live detections visible with bounding boxes overlaid on camera feed.

**Status (2026-06-28 04:37 HKT):** PARTIAL — both bags captured + analyzed.
Empty-scene: KEEP=0/439 at conf≥0.50 (M4c1 V4 PASS replicated live).
Cubes-in-frame: KEEP=0/414 at conf≥0.50 — **the Roboflow `best.engine` does
not fire on the actual cubes at the JetRover-room distance and camera
angle** (the geometry filter is doing its job, but a model that doesn't
fire on the target class cannot be salvaged by post-filtering). All 41700
geometry-filter rejects are `flat` (YOLO bbox depth ≈ floor depth,
indicating the bboxes are landing on floor texture, not on the cubes).

Next-step diagnostic: recapture cubes bag at conf=0.25 (mirrors the M4c1
V1 cubes capture where geometry filter kept 22/29 blue cubes). If that
shows ≥3 KEEPs, the model is fine and the only fix is to lower the
production conf threshold. If conf=0.25 still shows 0 KEEPs, the model
genuinely does not fire on real cubes and the fine-tune card
(`t_13b658c2`, previously closed as no-longer-needed) should be
re-opened with a fresh scope: produce a `best.engine` that detects
real JetRover-room cubes at conf≥0.50.

Publish-rate ceiling 15.52 Hz remains a separate concern — TensorRT FP16
+ sync overhead, below the original ≥25 Hz target. Options documented
in `evaluation/m5_live/report.md` §10: accept as-is, re-export FP32, or
skip frames.

---

## M6 — Evaluation Complete

- [ ] Run structured 50-frame test (see [`evaluation.md`](evaluation.md))
- [ ] Measure classification accuracy, inference fps, operating distance

**Done when:** Results recorded; success criteria met or gaps documented.

---

## M7 — Repository Complete

- [ ] README populated with results
- [ ] Pipeline diagram in `assets/`
- [ ] Clean code, all milestones documented in LOGBOOK

**Done when:** Repository is portfolio-ready on GitHub.

---

## Implementation Steps (ordered)

1. **Verify vendor camera** — with `peripherals/depth_camera.launch.py` running, confirm `ros2 topic hz /depth_cam/rgb/image_raw`
2. **Check versions** — PyTorch, ONNX, TensorRT on Jetson
3. **Obtain weights** — follow [`archive/model-options.md`](archive/model-options.md): raw Roboflow weights if available, otherwise create `best.pt` with a short YOLOv5s fine-tune from the approved Roboflow dataset
4. **Export ONNX** — `best.pt` → `best.onnx`
5. **TensorRT conversion** — ONNX → TensorRT FP16 `.engine` on Jetson
6. **Standalone inference test** — `scripts/test_inference.py` on robot camera snapshots; if accuracy poor → fine-tune locally (RTX 4070 Ti, 20–30 epochs) and repeat steps 4–6
7. **Minimal ROS 2 node** — subscribe, infer, print detections to terminal
8. **Add publishers** — `/cube_detections`, `/cube_detections/vendor_objects`, and `/cube_detections/debug_image`
9. **Visualize** — confirm bounding boxes in RViz2 or `rqt_image_view`
10. **Evaluate** — 50-frame structured test, measure fps and distance
