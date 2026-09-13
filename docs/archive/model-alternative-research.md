# M3c2 — Model alternatives: do we need custom hard-negative training?

Date: 2026-06-27
Scope: research / decision only. No training, exports, or code changes in this card.
Parent: `t_bfeee153`. Inputs: prior `docs/model-options.md` (M2), `docs/model-hard-negative-plan.md` (M3c), M4b live-camera evidence (`evaluation/m4b_predictions/`).

> **Update 2026-06-27 (M3c3, `t_becf3451`):** the primary-path recommendation
> in this document (option F — depth/geometry post-filter only) is
> **superseded** by the hybrid plan in
> [`docs/model-objectness-addendum.md`](model-objectness-addendum.md)
> §0/§5. Option F remains correct as Phase 1 of the hybrid. The
> addendum introduces Phase 1 (combined height + ratio + planar-top
> filter) and a V3 raised-3D-distractor validation gate that option F
> alone does not address. The §5 disposition of `t_13b658c2` and the
> open questions for Maher are also updated there.

## 0. TL;DR

The current model fails because it is **color-driven, not object-driven**: it fires on any saturated colored region of roughly cube size. There is no off-the-shelf pretrained detector that solves this — every plausible option still needs a cube-shape signal that has to come from data, geometry, or both. Custom hard-negative fine-tuning is therefore not a "wrong path" in principle; it is the right path *if* you want to keep the existing YOLOv5s + TensorRT + ROS pipeline. The decision is whether to commit to that pipeline or replace it.

**Recommendation:**

1. **Primary path (recommended):** keep `best.pt` and `best.engine`, add a **shape/geometry post-filter** on the YOLOv5 detections (option F). The depth topic `/depth_cam/depth_registered/points` is already published by the vendor camera stack and is sufficient to tell "flat colored surface at the same depth as the floor" from "compact cube with non-zero height above the floor." This avoids 2-3 hours of capture/label/train/export work, reuses the validated TensorRT engine, and fixes the three named distractors (green soil bag, blue cardboard package, blue decal) which are all flat surfaces flush with the background. The fine-tune can be kept as a follow-up if the depth post-filter turns out to miss non-flat distractors.
2. **Fallback path:** execute the existing `docs/model-hard-negative-plan.md` exactly as written (option E). Use a 60-frame held-out JetRower validation set and the §2.1 acceptance criteria. If F turns out to leave residual FPs, this is the next stop.
3. **Do not pursue:** existing pretrained cube detectors (none match our class set with downloadable weights), open-vocabulary detectors (NanoOWL/Grounding DINO can run on Jetson Orin but are 5-25× slower than YOLOv5s, fragile on Jetson Orin Nano, and still need color-saturated distractors handled), and architecture swaps (RF-DETR / YOLOv11 / YOLO-World — all change the vendor-aligned artifact path for no measurable win on this 3-class task).

**Disposition of the blocked card `t_13b658c2`:** replace. The M3c hard-negative fine-tune card should remain blocked **until** the post-filter (option F) is implemented and shown to leave residual FPs on the M4b 30-frame set. The fine-tune card stays as the explicit next step if option F is insufficient. Do not resume it speculatively; do not silently kill it.

## 1. What the M4b evidence actually shows

From `evaluation/m4b_predictions/report.md` and `detections.json` (30 live `/depth_cam/rgb/image_raw` frames, conf 0.25):

- 30/30 frame-hit on each of the three real cubes (real cubes are detected, with high conf: blue 0.97-0.99, red 0.68-0.82, green 0.26-0.41 — green is the weak one).
- ~3 blue + ~1.7 green + ~1.1 red boxes per frame in addition to the real cubes — i.e. about 90 expected positives became 177 detections.
- Three named FP hot-spots, all flat color regions:
  - Blue cardboard package: conf 0.83-0.88 every frame.
  - Green soil/sand bag: conf 0.65-0.78 every frame.
  - Blue decal: conf 0.25-0.58 (intermittent).
  - Red chair/object: conf 0.31-0.39 (intermittent).

The real cubes are ~50 mm wooden blocks sitting **on** the floor. All four named distractors are roughly **flat** regions **flush** with the floor (or a wall behind it). This is the critical geometric distinction the current color-driven model cannot make.

A conf threshold alone cannot fix this: the green soil bag (0.65-0.78) sits above the real green cube (0.26-0.41), so the only conf threshold that kills the bag kills the green recall. The M3c plan's "must have zero detections on named distractors" criterion is therefore correct.

## 2. What "object-driven" needs that color-only cannot provide

A correct cube detector needs to answer two questions at the same time:

1. Is the region a *cube-shaped 3D object* (bounded, compact, raised above the surface)?
2. What color is it?

The current model answers #2 confidently but has no signal for #1, so any saturated color blob of the right size qualifies. To make #1 work you need one of:

- A trained detector whose training set included many "colored non-cube" examples as negatives so it learns to suppress them.
- A geometric cue at inference time (depth, pointcloud, known floor plane) that distinguishes flat surfaces from objects raised above them.
- A pretrained detector whose pretraining set already contained lots of cubes in varied poses (and therefore has a cube-shape prior baked in).

This framing is what makes the option comparison below honest: options A and B are about *getting a pretrained cube-shape prior*; option D and F are about *injecting a geometric prior at inference time*; option E is about *teaching the existing detector a cube-shape prior through data*; option C is a different paradigm.

## 3. Options compared

### A) Existing pretrained cube/block detector

**What exists:**

- `thohemp/cube_detector` (https://github.com/thohemp/cube_detector): YOLOv5 OBB cube detector. Class set is not red/green/blue. OBB head, custom fork, license not visible on the page extract. Not a drop-in.
- `robotics25/color-cube-identifier` on Roboflow Universe (https://universe.roboflow.com/robotics25/color-cube-identifier): six classes including blue/green/orange/pink/red/yellow cube. Model type reported as YOLOv11s Model Upload, not YOLOv5s. Public raw `.pt` not visible (Roboflow weights are account/plan-gated per https://docs.roboflow.com/deploy/download-roboflow-model-weights). Even if accessible, the label set is the wrong granularity and the model family breaks vendor alignment.
- `HSLU Luzern Cube_Detector` on Roboflow Universe (https://universe.roboflow.com/hslu-luzern/cube_detector-m5ieb): generic cube detector. Class set and provenance unverified; no red/green/blue specificity.
- Hugging Face API search for `red green blue cube detection`, `colored cube detection`, `cube detection yolo best.pt` (run 2026-06-23 in `docs/model-options.md` §Outside Roboflow addendum) returned no direct cube-color detector `best.pt`.

**Verdict: not available.** No pretrained detector ships with weights that map cleanly to `red_cube`/`green_cube`/`blue_cube` for the Jetson + YOLOv5 path. The Roboflow-hosted detectors are reachable only via hosted API or Roboflow Inference cache, neither of which gives us a local `.pt` we can export through `best.pt → best.onnx → best.engine`.

### B) Existing external dataset + fine-tune

**What exists:**

- Jakub Slof `red-green-blue-cube-detection/1` on Roboflow Universe (https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1): 103 images, CC BY 4.0, YOLOv5 format export. **This is the dataset already used for M2.** Per-class mAP@0.5 from the M2 fine-tune was blue 0.982 / green 0.885 / red 0.995 on the Roboflow validation split. It is small, web-collected, and does not contain the JetRover-room distractors (green soil bag, blue cardboard package, blue decal, red chair). It is the reason M4b over-fires on color.
- Ezhil `red-green-blue-cube-detection-tkoml` on Roboflow Universe (https://universe.roboflow.com/ezhil-sdu5m/red-green-blue-cube-detection-tkoml): same class names, larger (461 images), higher reported metrics, but provenance unclear and no raw `.pt`.
- `AnnTarek/ShapeDetection` on GitHub (https://github.com/AnnTarek/ShapeDetection): YOLO-format detection dataset with classes `triangle, red_cube, yellow_cube, green_cube, blue_cube, rectangle, circle, ball, Cube_silicone` and ~1319 training / 355 valid / 163 test images. License not visible on the page extract; verify before use. **This is a real candidate for B-style external augmentation** because it covers all three project colors *plus* other shapes as negatives, which is exactly the kind of shape-vs-color supervision the current model needs. It is still a clean background dataset, so it will not by itself teach the model to reject a green soil bag, but it will at least teach it that other shapes exist.
- Edge Impulse / Kaggle *Cubes on conveyor belt* (https://www.kaggle.com/datasets/edgeimpulse/cubes-on-conveyor-belt): 70 images, Apache 2.0, bounding boxes for blue/green/red/yellow cubes. Too small and too domain-specific (conveyor-belt viewpoint) to be more than a sanity-check supplement.

**Verdict: usable but insufficient alone.** Adding `AnnTarek/ShapeDetection` as a second training source is a reasonable experiment for the M3c fine-tune recipe (option E below), but no external dataset alone contains the JetRover-room distractors that drive the M4b false positives. You still need the 60-frame hard-negative capture called for in `docs/model-hard-negative-plan.md` §4.

### C) Open-vocabulary detector (YOLO-World, Grounding DINO, OWL-ViT)

**What exists:**

- **YOLO-World** (https://docs.ultralytics.com/models/yolo-world/): Ultralytics-maintained; supports text prompts like `red cube, green cube, blue cube`; can export to ONNX and TensorRT per the Ultralytics integration docs. Real Jetson Orin Nano benchmarks at 640 input are not published; community threads suggest YOLO-World-M/S is 3-10× slower than YOLOv5s on Orin Nano because of the text encoder.
- **Grounding DINO 1.5 Edge** (https://arxiv.org/html/2405.10300v2): NVIDIA paper claims "over 10 FPS at input size 640 on Jetson Orin NX" for the Edge variant. Community reports on AGX Orin 64GB (https://github.com/NVIDIA-AI-IOT/jetson-platform-services/issues/3) measured 2-3 FPS in practice vs the advertised 11.6 FPS. Orin Nano is a smaller chip than Orin NX/AGX Orin; expect 3-8 FPS best case at 640. NVIDIA JPS service exists (https://docs.nvidia.com/jetson/jps/inference-services/gdino.html) but ships in a container, not as a `.engine` we can drop into the existing ROS node. Community TensorRT recipe: https://github.com/shentan-shiina/GroundingDINO-TensorRT (tested on Orin NX/AGX Orin).
- **NanoOWL** (OWL-ViT) (https://github.com/NVIDIA-AI-IOT/nanoowl): "optimizes OWL-ViT to run real-time on NVIDIA Jetson Orin Platforms with NVIDIA TensorRT". Community benchmarks on AGX Orin 64GB: 40-60 ms per image for `owl_image_encoder_patch32.engine` (https://forums.developer.nvidia.com/t/nanoowl-inference-takes-more-time-than-nanoowl-official-github-shows/293051). At Orin Nano's smaller GPU and memory budget, expect 80-150 ms (7-12 FPS) at best for real-time text-prompted detection. JetPack 6.2 Super Mode gives 1.5-2× improvement but we are on JetPack with the original Orin Nano config.

**Verdict: technically possible, practically wrong.**

Pros:
- No training needed for new classes; prompts can be edited at deploy time.
- Has been demonstrated on Jetson Orin (NanoOWL, Grounding DINO JPS container).
- Could in principle handle the four named distractors if the prompt is well chosen.

Cons:
- 5-25× slower than the existing YOLOv5s engine (14.66 ms steady-state). M4b reported engine-only latency of 14.66 ms; NanoOWL is ~80-150 ms, Grounding DINO is 125-330 ms. The camera publishes at ~30 Hz; this would drop us to 6-12 FPS detection, below the 30 Hz camera rate. ROS 2 latency would balloon and the `bounded queue, drop stale frames` pattern in `example/yolov5_detect/yolov5_node.py` would start throwing away real cubes.
- Output is text-conditioned; labels can drift between runs unless the prompt and tokenizer are version-pinned. Stable `red_cube`/`green_cube`/`blue_cube` class IDs in `Detection2DArray` and `interfaces/ObjectsInfo` is the project's vendored output contract — open-vocabulary boxes need a label-mapping shim and the shim is fragile.
- Container / non-`.engine` deployment for the most production-ready options breaks the vendor-aligned YOLOv5/TensorRT artifact chain.
- Jetson Orin Nano is the small end of the Orin family; published Grounding DINO / NanoOWL numbers are on Orin NX or AGX Orin. Real Orin Nano numbers in the project's configuration are likely 30-50% slower.

If this were a one-month architecture project with the Jetson Orin NX, NanoOWL would be a serious candidate. For a one-week portfolio project on Orin Nano with a published TensorRT engine already running, it is a poor trade.

### D) Depth/geometry-assisted cube detector + color classifier

**What exists:**

- `/depth_cam/depth_registered/points` is published by the Orbbec/Dabai driver per the vendor launch `src/vendor/peripherals/launch/include/dabai_dcw.launch.py` (the remap `/<camera_name>/depth/color/points` → `/<camera_name>/depth_registered/points` is documented in `docs/vendor-audit.md` §1). The topic is `sensor_msgs/PointCloud2` and is the depth stream for the same camera that publishes the RGB topic already in use.
- Orbbec Dabai DCW2 depth camera specs: structured-light binocular depth, ~0.3-3 m working range (per Yahboom product page https://www.yahboom.net/public/upload/upload-html/1755249144/1.Dabai_DCW2+camera+introduction.html and Hiwonder JetRover docs https://docs.hiwonder.com/projects/JetRover/en/jetson-orin-nano/docs/7.Robot_Arm_Control_Course.html). Within the project's 20-80 cm operating distance the depth is reliable.
- The four named M4b distractors are visually flat surfaces flush with the floor or wall behind them. A pointcloud-derived height-above-floor (or curvature, or backface ratio) feature would assign them a height near zero while a 50 mm wooden cube raised on the surface would have a non-zero height distribution inside its YOLO box.

**Verdict: feasible and underexplored.** This option reuses the validated YOLOv5s detector unchanged and adds a small post-filter node that consumes both `/cube_detections` (or the raw YOLO boxes before publishing) and `/depth_cam/depth_registered/points` to reject boxes whose internal depth statistics look like a flat surface.

Pros:
- Zero new training. The YOLOv5s detector we already have keeps detecting colored cube candidates; the post-filter just vetoes the ones that are not actually raised off the floor.
- Reuses the validated TensorRT engine, the existing ROS node scaffolding, and the existing vendor stack. No new packages, no vendor modifications.
- Geometry is a stronger signal than more color training. A green soil bag and a green wooden cube have similar RGB signatures; their depth signatures are completely different.
- Can be implemented and tested on the existing M4b 30-frame set plus a small depth-validation set within 1-2 hours of implementer time (vs ~3 hours for the M3c fine-tune plan).

Cons:
- Requires the Orbbec pointcloud to be reasonably dense at 640x360. The Dabai publishes a 640x360 depth image typically; sparse points at 50 mm cube scale need checking. If the per-cube pointcount inside a YOLO box at 20-80 cm is too small (<10 points), the height statistic is unreliable and the filter becomes a coin flip.
- The Orbbec depth has known noise and "edge artifacts" at object boundaries. The YOLO box is axis-aligned and the cube is small; the box edge will include background floor points. The implementation needs to be careful about which points count as "inside the box" (typically: median z within the box minus median z of an annulus around the box).
- Adds a second subscription and a small per-frame pointcloud crop. Adds ~5-10 ms compute on top of the 14.66 ms engine latency on Orin Nano. Still well under the 33 ms budget for 30 Hz.
- If the depth stream is unreliable for any reason (lighting, distance, reflective surfaces), the filter degrades to "trust the YOLO box" and we are back where we started. This must be tested empirically on the actual hardware.

Implementation sketch (for the implementer card, not this one):

1. Subscribe to `/depth_cam/depth_registered/points` and the YOLO boxes.
2. For each candidate box, sample points inside the box (with a small inset to avoid edge bleed).
3. Compute `height = median(z inside box) - median(z in annulus around box)`. Reject if height < 15 mm (one third of a cube's 50 mm nominal height, with margin for depth noise).
4. For boxes where fewer than N points (e.g. 30) are inside, fall back to "no depth evidence" — keep the box but mark it `low_confidence_depth=true` in the debug image and the vendor message.
5. The threshold (15 mm) is a tunable; run the M4b 30 frames and the 30 empty-scene frames first to choose it.

This is option F below, just described in implementation detail.

### E) Continue current YOLOv5 hard-negative fine-tune

The full plan is in `docs/model-hard-negative-plan.md`. Summary:

- Merge Roboflow positives (~103 imgs) + ~120 new JetRover-room cube frames + ~60 hard-negative frames (empty room with distractors).
- Train YOLOv5s from `models/best.pt` for 25 epochs at LR 0.0005 with stronger augmentation.
- Hold out 60 frames for the §2.1 acceptance test (≥55/60 hit rate on real cubes, zero hits on the named distractors).
- Produce `models/best_hardneg.pt`, `best_hardneg.onnx`, `best_hardneg.engine` as separate artifacts until the tester approves.
- Implementer effort: ~3 hours focused work, gated on a Maher physical session to capture frames and label.

**Verdict: correct plan, expensive plan.** This is the only path that adds shape supervision directly to the model weights and therefore improves the model on out-of-distribution distractors we have never seen. It is the fallback to F if F is insufficient.

### F) Hybrid: YOLO candidate detections + depth/geometry false-positive rejection

Same as D in spirit, but framed as "keep YOLO + add a cheap veto" rather than "replace YOLO with a depth-first pipeline". The depth/geometry step is purely a post-filter, not a re-architecting of the detector. This is the recommended primary path; see D for the analysis.

Pros and cons are the same as D, with the framing advantage that the YOLOv5s detector remains the canonical project artifact (matches `docs/architecture.md`, `docs/technical-stack.md`, and the vendor reference `example/yolov5_detect`).

## 4. Recommendation table

| Option | Fixes named FPs? | New data needed? | Jetson Orin Nano real-time? | Vendor-stack impact | License/provenance | Effort | Verdict |
|---|---|---|---|---|---|---|---|
| A) pretrained cube detector | No — no matching detector ships with cube-color `.pt` | n/a | n/a | breaks vendor YOLOv5 alignment | unclear | n/a | **No.** Not available. |
| B) external dataset + fine-tune | Partial — only on in-distribution distractors | 1 dataset review + 1 fine-tune run | yes (same YOLOv5) | none | CC BY 4.0 / Apache 2.0 candidates | 1-2 days | **Useful as augmentation** inside option E, not standalone. |
| C) open-vocab detector | Possible | none | **No** (3-25× slower than YOLOv5s on Orin Nano) | breaks vendor YOLOv5 alignment; container-first | Apache 2.0 / NVIDIA Open Model License | 1-2 days | **No.** Latency breaks 30 Hz loop. |
| D) depth/geometry pipeline | Yes — named FPs are flat | none | yes (~20-25 ms total per frame) | adds one new subscription | n/a | 1-2 hours | **Strong.** Underused; the depth topic is already live. |
| E) hard-negative YOLO fine-tune | Yes — strongest guarantee | 120 cube frames + 60 distractor-only frames + labels + held-out set | yes (same YOLOv5) | none | CC BY 4.0 dataset + project labels | ~3 hours + Maher session | **Correct fallback.** Most general fix. |
| F) YOLO + depth/geometry post-filter | Yes for flat distractors; partial for 3D-shaped distractors | none | yes (~20-25 ms total per frame) | adds one new subscription, no model change | n/a | 1-2 hours | **Primary recommendation.** Cheapest fix; preserves validated engine. |

**Primary path:** F. **Fallback path:** E (run the existing M3c plan as written if F is insufficient on the M4b + depth validation set).

## 5. Disposition of blocked card `t_13b658c2`

`docs/model-hard-negative-plan.md` and its implementing card `t_13b658c2` should be:

- **Kept as a documented plan**, not deleted. The plan itself is correct; the strategic question was whether it is necessary. Option F now answers that: it is not necessary *first*, but it remains the right next step if F is insufficient.
- **Resumed only after F is implemented and tested.** Concretely: implementer should run F against the M4b 30-frame set + the empty-scene 30-frame set. If FPs on named distractors drop to zero (or to a documented non-zero rate that the project accepts), `t_13b658c2` stays blocked indefinitely. If F leaves residual FPs on a NEW distractor (something not in the M4b set), unblock `t_13b658c2` and execute the M3c plan against that distractor as well.
- **Not silently killed.** If at any point the project decides to ship without it, mark it as `cancelled` with a one-line rationale in the LOGBOOK and update `.cursorrules` Current Status. Do not let it sit in `blocked` forever.

## 6. Open questions for Maher

1. **Approve option F as the primary path?** Implementation is small (one new subscription + one filter function + one config param), reuses the existing TensorRT engine, and fixes all four named M4b distractors on geometric grounds. Y/N.
2. **If F is approved, who captures a small depth-validation set?** Need ~30 frames with cubes + depth at 20/40/60/80 cm and ~30 empty-scene frames with depth (the empty-scene Phase A set already exists; the cube-arranged set is the gated Phase B per LOGBOOK). This is the same Maher-physical-session requirement as the M3c plan, just smaller.
3. **Is there appetite for a one-line "do not modify `src/vendor`" check in the post-filter card?** The post-filter should live in the project package (`recognition_of_different_colored_cubes`), consume the existing vendor topics, and not touch `src/vendor` — same constraint as the rest of the project.
4. **If F leaves residual FPs, accept the full M3c plan as the next step?** The M3c plan calls for ~3 hours focused work plus a Maher capture session. Confirm budget.

## 7. References

### Internal

- `docs/model-options.md` — M2 model source research (Roboflow, Roboflow addendum, external model options)
- `docs/model-hard-negative-plan.md` — M3c hard-negative fine-tune plan (the option E artifact)
- `docs/vendor-audit.md` — vendor stack and depth topic audit (`/depth_cam/depth_registered/points` published by `peripherals/depth_camera.launch.py`)
- `docs/architecture.md` — current vendor-aligned pipeline (YOLOv5 + TensorRT + `/depth_cam/rgb/image_raw` → `/cube_detections`)
- `docs/technical-stack.md` — current model export chain
- `docs/milestones.md` — M4b verdict (over-detection on color-confusable background, FP cleanup recommended before M5)
- `docs/LOGBOOK.md` 2026-06-27 M4b entry — live-camera inference numbers
- `evaluation/m4b_predictions/report.md` and `detections.json` — the 30-frame FP evidence

### External — datasets

- Jakub Slof red-green-blue-cube-detection: https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1
- Ezhil same-class dataset: https://universe.roboflow.com/ezhil-sdu5m/red-green-blue-cube-detection-tkoml
- AnnTarek ShapeDetection dataset (classes include red/green/blue cube + other shapes): https://github.com/AnnTarek/ShapeDetection
- Edge Impulse / Kaggle Cubes on conveyor belt: https://www.kaggle.com/datasets/edgeimpulse/cubes-on-conveyor-belt
- robotics25 color-cube-identifier: https://universe.roboflow.com/robotics25/color-cube-identifier
- HSLU Luzern Cube_Detector: https://universe.roboflow.com/hslu-luzern/cube_detector-m5ieb

### External — detectors and tools considered

- Ultralytics YOLOv5: https://github.com/ultralytics/yolov5
- Ultralytics TensorRT export: https://docs.ultralytics.com/integrations/tensorrt/
- Ultralytics Jetson guide: https://docs.ultralytics.com/guides/nvidia-jetson/
- Ultralytics YOLO-World: https://docs.ultralytics.com/models/yolo-world/
- Roboflow weights download docs: https://docs.roboflow.com/deploy/download-roboflow-model-weights
- RF-DETR: https://github.com/roboflow/rf-detr
- RF-DETR Jetson Orin performance issue (2× slower than YOLOv11): https://github.com/roboflow/rf-detr/issues/340
- Grounding DINO 1.5 Edge (NVIDIA paper, 10+ FPS on Orin NX): https://arxiv.org/html/2405.10300v2
- Grounding DINO NVIDIA JPS: https://docs.nvidia.com/jetson/jps/inference-services/gdino.html
- Grounding DINO community TensorRT recipe (tested on Orin NX/AGX Orin): https://github.com/shentan-shiina/GroundingDINO-TensorRT
- Grounding DINO AGX Orin community FPS report: https://github.com/NVIDIA-AI-IOT/jetson-platform-services/issues/3
- NanoOWL (OWL-ViT optimized for Jetson Orin): https://github.com/NVIDIA-AI-IOT/nanoowl
- NanoOWL community latency report: https://forums.developer.nvidia.com/t/nanoowl-inference-takes-more-time-than-nanoowl-official-github-shows/293051
- thohemp cube_detector (YOLOv5 OBB, not drop-in): https://github.com/thohemp/cube_detector
- Orbbec Dabai DCW2 camera overview: https://www.yahboom.net/public/upload/upload-html/1755249144/1.Dabai_DCW2+camera+introduction.html
- Hiwonder JetRover camera docs: https://docs.hiwonder.com/projects/JetRover/en/jetson-orin-nano/docs/7.Robot_Arm_Control_Course.html

---

Card status: research/decision complete. **Primary path:** F (YOLO + depth post-filter, no new training). **Fallback path:** E (existing M3c plan, unchanged). `t_13b658c2` remains blocked until F is tested; unblock only if F leaves residual FPs.