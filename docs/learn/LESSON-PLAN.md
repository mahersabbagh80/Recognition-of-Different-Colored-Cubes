# Colored-Cube Computer-Vision Learning Plan

**Status:** Active learning plan<br>
**Audience:** Maher — beginner in computer vision, learning through a real ROS 2 robotics project<br>
**Repository:** `Recognition-of-Different-Colored-Cubes`<br>
**Created:** 2026-08-30<br>
**Last updated:** 2026-09-03<br>
**Scope:** Understand and explain the existing YOLOv5 + TensorRT + ROS 2 perception pipeline before making substantial implementation decisions.

---

## 1. Purpose

This learning track has two goals:

1. Build enough computer-vision and deployment knowledge to make the project's M3–M7 decisions deliberately.
2. Produce portfolio-quality evidence that Maher understands the system rather than only having generated code that appears to work.

The project remains the anchor. Every lesson should connect its concepts to a real file, command, artifact, or observed result in this repository.

This plan is a teaching document. The canonical engineering status remains in:

- [`README.md`](../../README.md)
- [`../project-definition.md`](../project-definition.md)
- [`../architecture.md`](../architecture.md)
- [`../milestones.md`](../milestones.md)
- [`../LOGBOOK.md`](../LOGBOOK.md)

---

## 2. Teaching contract

Each lesson should follow this loop:

1. **Orient** — state the question the lesson answers and why it matters here.
2. **Explain** — introduce the smallest set of concepts needed.
3. **Visualize** — show the concept with an accurate diagram, image, or interaction.
4. **Anchor** — connect it to a concrete project file and named function.
5. **Exercise** — ask Maher to predict, inspect, run, or explain something.
6. **Verify** — compare the prediction with real output or repository evidence.
7. **Explain back** — Maher summarizes the idea in his own words.
8. **Record** — capture durable lessons, corrections, and unresolved questions.

AI is used as a tutor, reviewer, and execution assistant—not as a substitute for understanding. Do not introduce a large code change until its purpose, effect, scope, and verification method have been explained and approved.

---

## 3. Lesson format

Each lesson is an HTML artifact under `lessons/` and should normally contain:

- title, estimated time, prerequisites, and project anchor;
- a Lesson Overview Sheet at the beginning: one complete PNG visual map of every core lesson concept;
- the question the lesson answers;
- plain-language explanation before technical detail;
- one central mental model;
- accurate diagrams or demonstrations;
- links to relevant repository files using stable relative paths;
- one or more knowledge checks;
- one small exercise with an observable result;
- an explain-back prompt;
- what the lesson intentionally postpones;
- primary references and a clear next lesson.

Lessons should use the shared `assets/lesson.css` and `assets/quiz.js` where possible. Prefer self-contained inline SVG for technical visuals because it keeps labels, coordinates, and arrows exact and works offline. Add custom JavaScript only for small interactions that make the concept clearer.

The current [Maher Brand System](https://drive.google.com/drive/folders/1SBTxnRAZkqTOzhmUOA5bqJhLmspCXOVJ) is mandatory for all lesson prose, data artifacts, HTML, images, diagrams, and supporting deliverables. It is authoritative in Google Drive and locally available through the Google Drive GVFS mount. Apply its Poppins typography, Navy/Cool Silver/Electric Blue visual system, direct technical voice, real-system imagery rule, and calm grid-based composition; do not invent a generic style when the brand book supplies a rule.

A lesson may use real project images when they teach an authentic behavior. Generated or stylized images must never imply measurements, detections, or labels that were not actually observed.

### Lesson Overview Sheet standard

Every lesson begins with a standalone **Lesson Overview Sheet**: a readable PNG that gives the learner a complete visual map before the detailed explanation starts.

- Use a tall portrait sheet when a landscape image would make labels or explanations too small.
- Make one numbered station for every independently teachable core concept. Each station must include a small visual example and a short, technically exact explanation.
- Establish one obvious reading order (for example, `1 → 12`, left to right and top to bottom). A short pipeline ribbon may show the main data flow, but it must not replace the full station sequence.
- Use one coherent illustration system across the entire sheet: shared paper/background treatment, semantic colors, typography, spacing, and line style. Compose the artwork as a single layout; do not place opaque explanatory cards over unrelated generated art.
- Apply the current Maher Brand System before designing the sheet. Near-black Navy and Cool Silver are the dominant surfaces; Industrial/Steel Blue structure information; Electric Blue remains a focused accent. Use Poppins, a calm grid, realistic technical imagery or clearly labelled explanatory diagrams, and direct technically grounded copy.
- Reserve a compact footer for the project anchor—real file names and functions—not for new concepts. Keep the footer below all stations.
- Treat the sheet as an orientation aid, not an evidence artifact. Stylized examples must be labelled as explanatory, and observed results must preserve their exact context.
- Validate the final PNG independently and inspect its complete rendered image plus detailed crops before embedding it in a lesson.

---

## 4. Curriculum

| ID | Lesson | Main question | Project anchor | Status |
|---|---|---|---|---|
| 0001 | [From Pixels to Detections](lessons/0001-what-yolo-outputs.html) | How does a camera image become a structured cube detection? | `cube_detection_node.py`, especially `_letterbox`, `_sync_cb`, `CubeDetection` | Implemented; learner review pending |
| 0002 | [How YOLO Produces Predictions](lessons/0002-how-yolo-produces-predictions.html) | Why does YOLO create many candidates, and how do decoding and NMS produce final boxes? | `_decode_yolov5_output`, `models/README.md` | Implemented; validation complete; learner review pending |
| 0003 | [PyTorch and Model Training](lessons/0003-pytorch-and-model-training.html) | What are datasets, labels, epochs, validation, checkpoints, and fine-tuning? | `models/best.pt`, `models/README.md`, training scripts | Implemented; validation complete; learner review pending |
| 0004 | [Why the Model Fails on the Robot](lessons/0004-why-the-model-fails-on-the-robot.html) | Why can validation look good while live inference fails? | M4/M5 evaluation reports, domain-gap evidence | Implemented; validation complete; learner review pending |
| 0005 | [ONNX and TensorRT](lessons/0005-onnx-and-tensorrt.html) | Why does the model travel through `best.pt → best.onnx → best.engine`? | `models/README.md`, export and TensorRT commands | Implemented; validation complete; learner review pending |
| 0006 | [ROS 2 Perception Wiring](lessons/0006-ros-2-perception-wiring.html) | How do nodes, topics, messages, `cv_bridge`, and QoS connect the detector? | `cube_detection_node.py`, `package.xml`, launch/config files | Implemented; validation complete; learner review pending |
| 0007 | [Depth and Geometry Filtering](lessons/0007-depth-and-geometry-filtering.html) | How does depth provide a second check for a raised cube-like object? | `geometry_filter.py`, M4c1 evidence | Implemented; validation complete; learner review pending |
| 0008 | [Evaluation and Fine-Tuning](lessons/0008-evaluation-and-fine-tuning.html) | How do we measure success and improve the model responsibly? | `evaluation/`, `docs/evaluation.md`, M3d-revived plan | Implemented; validation complete; learner review pending |
| 0009 | [Project Walkthrough and Interview Practice](lessons/0009-project-walkthrough-and-interview-practice.html) | Can Maher explain the complete system, trade-offs, failures, and next steps? | Full repository and evidence | Implemented; validation complete; learner review pending |

The order is intentional: concepts needed to read the runtime path come before training and deployment internals, and evaluation is taught before the next fine-tuning decision.

---

## 5. Lesson 0001 specification

### Working title

**From Pixels to Detections: How One Camera Image Becomes a Cube Detection**

### Learning objectives

By the end of the lesson, Maher should be able to:

- describe an image as a grid of pixel values;
- identify image width, height, channels, and the top-left coordinate origin;
- distinguish image classification from object detection;
- explain the three essential parts of a detection: class, bounding box, and confidence score;
- describe the runtime pipeline at a high level;
- explain why weak or duplicate predictions need post-processing;
- identify the roles of `_letterbox`, `_infer`, `_decode_yolov5_output`, `_sync_cb`, and `_publish_outputs`;
- explain why a confidence score is evidence from the model, not a guarantee of truth.

### Concepts included

- image and pixel grid;
- RGB/BGR as an image-representation issue;
- pixel coordinates and bounding boxes;
- classification versus detection;
- class label, confidence score, and location;
- inference as applying a trained model;
- high-level confidence filtering and non-maximum suppression;
- the connection between the conceptual pipeline and the current node.

### Concepts postponed

- CNN layer mathematics and backpropagation;
- YOLO anchors and feature-map calculations;
- the detailed `[1, 7, 8400]` output tensor;
- ONNX graph conversion;
- TensorRT engine building and FP16 details;
- ROS 2 QoS compatibility;
- camera intrinsics and depth geometry thresholds;
- fine-tuning commands and hyperparameter selection.

### Planned visuals

1. A 12-station tall portrait, hand-drawn technical Lesson Overview Sheet at `assets/lesson-0001-concept-art-handdrawn-portrait.png`, embedded at the beginning of the lesson and linked at full resolution. It covers the goal/scope; ROS image conversion; pixels/channels; coordinates/boxes; classification versus detection; detection anatomy; BGR→RGB and letterbox preparation; YOLOv5/TensorRT candidates; confidence thresholding; NMS; depth/geometry; ROS output and the M5 evidence note. Its footer maps the concepts to the current node functions. The earlier landscape artistic variant is preserved at `assets/lesson-0001-concept-art.png`, and the precise portrait technical sheet remains available at `assets/lesson-0001-concept-art-technical-sheet.png` for comparison.
2. A clean vector camera frame with three colored cubes and final bounding boxes.
3. A coordinate-grid diagram showing the top-left origin and box corners.
4. A detection record showing class, score, and box as structured data.
5. A simplified end-to-end pipeline diagram.
6. A before/after NMS illustration with overlapping candidate boxes.
7. A small confidence-threshold interaction showing weak candidates being removed.
8. An optional real-project comparison using the M5 RGB frame and its `keep=0` debug overlay.

### Exercise and verification

The lesson should use a verified repository image or a deliberately generated teaching diagram. It must not depend on the nonexistent `data/sample.jpg` referenced by the older draft lesson.

The exercise should produce an observable result, such as identifying the coordinate system and detection fields in a displayed example, or running a tested read-only inference inspection command against an available image.

---

## 6. Lesson 0002 specification

### Working title

**How YOLO Produces Predictions: From a 640×640 Tensor to Final Cube Boxes**

### Learning objectives

By the end of the lesson, Maher should be able to:

- distinguish candidate rows from final detections;
- explain why the current 640×640 export contains `80² + 40² + 20² = 8400` candidate positions;
- read `output0 [1, 7, 8400]` and explain why the decoder transposes it to `[8400, 7]`;
- describe the current candidate row as `xywh` plus three sigmoid class scores, with no separate objectness column;
- explain `max`/`argmax`, the confidence mask, `xywh → xyxy`, letterbox reversal, IoU, and per-class NMS;
- trace the decoder path through `_letterbox()`, `_infer()`, and `_decode_yolov5_output()`;
- explain why the deployed decoder is part of the model artifact contract.

### Concepts included

- dense candidate prediction in a one-stage detector;
- three detection grids and the `8400` candidate count;
- tensor axes and the `[1, 7, 8400]` artifact layout;
- candidate-row anatomy and project class order;
- confidence filtering versus IoU filtering;
- `xywh` center/size and `xyxy` corner coordinates;
- letterbox padding and inverse coordinate mapping;
- IoU and greedy non-maximum suppression;
- per-class NMS and the final detection tuple;
- the connection between the mental model and the current code.

### Concepts postponed

- CNN layer mathematics and backpropagation;
- the internal anchor/stride calculations inside the exported graph;
- dataset labels, loss functions, epochs, validation, and fine-tuning;
- ONNX graph conversion and TensorRT engine construction;
- ROS 2 message wiring, depth geometry, and the M5 acceptance evidence.

### Planned visuals

1. A 12-station tall portrait, hand-drawn technical Lesson Overview Sheet at `assets/lesson-0002-concept-art-handdrawn-portrait.png`, embedded at the beginning of the lesson and linked at full resolution. It covers the dense candidate field; `8400` grid decomposition; tensor axes; transpose; candidate-row anatomy; class selection; `xywh → xyxy`; confidence thresholding; letterbox reversal; IoU; per-class NMS; and the final detection tuple. Its footer maps the concepts to the current decoder functions and artifact notes.
2. A dense candidate-field diagram showing why one forward pass produces many guesses.
3. An interactive three-grid comparison for `80×80`, `40×40`, `20×20`, and the total `8400` positions.
4. An interactive tensor-view diagram showing `[7,8400] → [8400,7]`.
5. Exact class-score, coordinate-conversion, confidence-mask, letterbox, IoU, and NMS diagrams with small interactions.

### Exercise and verification

The lesson uses the tested read-only command `.venv-m2/bin/python scripts/m3_smoke_inference.py --topk 5` when the local model and validation image are present. The learner traces the real decoder and hand-decodes one illustrative row; no implementation change is required.

---

## 7. Lessons 0003–0009 specifications

The following specifications keep the remaining pages aligned with the repository instead of turning them into generic machine-learning or ROS tutorials. Each page has a twelve-station portrait overview, small interactive checks, a read-only exercise, an explain-back prompt, postponements, local anchors, and primary external references.

### Lesson 0003 — PyTorch and Model Training

- **Question:** What do datasets, detection labels, epochs, validation metrics, and checkpoints mean in this project?
- **Objectives:** Read a YOLO label; distinguish train/validation/test; explain forward/loss/backpropagation; interpret mAP and a best checkpoint; identify the class-ID documentation conflict.
- **Anchors:** `models/README.md`, `models/best.pt`, `scripts/normalize_dataset.py`, and `scripts/finetune_hardneg.py`.
- **Visuals:** Dataset-to-checkpoint learning loop, label anatomy, split discipline, metric bars, and checkpoint selection.
- **Exercise:** Inspect the documented M2 artifact and verify its presence/read-only metadata; no training run is required.

### Lesson 0004 — Why the Model Fails on the Robot

- **Question:** Why can a model look strong on a small validation set and still miss cubes in the live room?
- **Objectives:** Separate validation, saved-frame, and live-bag evidence; explain domain gap; localize a failure before changing code; interpret the M5 PARTIAL verdict.
- **Anchors:** `evaluation/m5_live/report.md`, `evaluation/m4c_geometry_filter/report.md`, and the M5 RGB/debug evidence.
- **Visuals:** Two-world comparison, candidate-versus-keep gate, threshold experiment, controlled bags, and falsified sticker hypothesis.
- **Exercise:** Reconstruct the current evidence matrix from the report and state which stage the data does—and does not—blame.

### Lesson 0005 — ONNX and TensorRT

- **Question:** Why does one learned detector need three artifact containers and several verification boundaries?
- **Objectives:** Distinguish checkpoint, exchange graph, and engine; read the static tensor contract; explain FP16 and device specificity; verify export and runtime boundaries.
- **Anchors:** `models/README.md`, `scripts/m3_smoke_inference.py`, `scripts/m4a_trt_smoke_inference.py`, and the node engine loader.
- **Visuals:** Artifact chain, tensor contract, checker/smoke steps, TensorRT builder, and runtime binding path.
- **Exercise:** Run the verified ONNX smoke command when local artifacts are present; mark TensorRT commands as Jetson-only.

### Lesson 0006 — ROS 2 Perception Wiring

- **Question:** How do ROS 2 messages enter the detector and leave as standard, vendor, and debug outputs?
- **Objectives:** Trace topics and message types; explain approximate RGB/depth synchronization; distinguish `cv_bridge` encodings; locate parameters, launch, and package dependencies; use read-only graph inspection.
- **Anchors:** `cube_detection_node.py`, `package.xml`, `config/params.yaml`, and `launch/detection.launch.py`.
- **Visuals:** ROS graph, callback sequence, QoS boundary, message contracts, and output fan-out.
- **Exercise:** Compile the Python sources locally, then inspect `ros2 topic info/echo/hz` on the already-running Jetson stack if available.

### Lesson 0007 — Depth and Geometry Filtering

- **Question:** How does depth provide a second check for a raised cube-like object without becoming a second detector?
- **Objectives:** Explain aligned pixel assumptions and depth units; derive the floor annulus and raised fraction; interpret extent/aspect/planarity; explain fail-open low-quality decisions; read M4c1 limits.
- **Anchors:** `geometry_filter.py`, node depth handling, `config/params.yaml`, and `evaluation/m4c_geometry_filter/report.md`.
- **Visuals:** RGB/depth coordinate sharing, annulus, raised subset, 3-D extent, aspect/planar checks, and decision tree.
- **Exercise:** Run a synthetic, read-only `decide()` example and predict its verdict before reading the output.

### Lesson 0008 — Evaluation and Fine-Tuning

- **Question:** How do we measure success and improve the model without promoting an unverified experiment?
- **Objectives:** Match metrics to questions; build a controlled test matrix; separate capture provenance from labels; read the M5 matrix; distinguish the unexecuted M3d plan from evidence; preserve rollback.
- **Anchors:** `docs/evaluation.md`, `evaluation/m5_live/report.md`, `scripts/capture_frames.py`, `scripts/m5_analyze_bag.py`, and `docs/m3d-revived-plan.md`.
- **Visuals:** Metric matrix, capture/replay loop, current M5 counts, acceptance gates, positive-domain data, hold-out split, and rollback.
- **Exercise:** Audit `evaluation/evaluate.py` as a placeholder and use the recorded report/analyzer workflow as the current evidence path.

### Lesson 0009 — Project Walkthrough and Interview Practice

- **Question:** Can Maher explain the full system, trade-offs, failures, and next reversible step without overclaiming?
- **Objectives:** Deliver a 90-second summary; whiteboard the runtime path; name interfaces and artifact boundaries; cite M5 evidence; answer failure and next-step questions.
- **Anchors:** `README.md`, `docs/architecture.md`, `models/README.md`, `cube_detection_node.py`, and `evaluation/m5_live/report.md`.
- **Visuals:** Complete pipeline, contracts, artifact/evidence timeline, trade-off map, failure answer, and interview loop.
- **Exercise:** Record or write a timed walkthrough and check it against the data/evidence/boundaries rubric.

## 8. Repository-specific truth to preserve

- The canonical current engineering status is **M5 PARTIAL**.
- The current node synchronizes RGB and depth images in `_sync_cb`.
- The current model artifact is documented as a fused-decode output with shape `[1, 7, 8400]`.
- The current model/node class order is `0: blue_cube`, `1: green_cube`, `2: red_cube`.
- `docs/project-definition.md` still contains a different class-ID table (`0: red_cube`, `1: green_cube`, `2: blue_cube`). This documentation conflict must be reconciled before another fine-tuning run; lessons should call it out rather than silently choosing an interpretation.
- The M5 geometry filter is a second, depth-based evidence check. It does not replace YOLO and cannot recover a class that the model never proposes.
- The HiWonder vendor packages are reference/infrastructure material and must not be modified.

---

## 9. Source hierarchy

For project-specific behavior, prefer sources in this order:

1. current code and verified artifacts;
2. current project documentation and evaluation evidence;
3. official library, framework, ROS 2, ONNX, NVIDIA, and Ultralytics documentation;
4. community explanations only for supplementary intuition.

Primary external references for this learning track:

- [PyTorch beginner workflow](https://pytorch.org/tutorials/beginner/basics/intro.html)
- [Ultralytics YOLOv5 documentation](https://docs.ultralytics.com/yolov5/)
- [Ultralytics YOLOv5 repository](https://github.com/ultralytics/yolov5)
- [ONNX introduction](https://onnx.ai/onnx/intro/)
- [NVIDIA TensorRT 8.6 Quick Start Guide](https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-861/quick-start-guide/index.html)
- [ROS 2 nodes](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Concepts/Basic/About-Nodes.rst)
- [ROS 2 topics](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Concepts/Basic/About-Topics.rst)
- [ROS 2 QoS](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Concepts/Intermediate/About-Quality-of-Service-Settings.rst)

---

## 10. Progress tracking

A lesson is complete only when:

- [ ] the lesson content matches the current repository behavior;
- [ ] all local paths and external links were checked;
- [ ] every visual is readable and technically accurate;
- [ ] quizzes and interactions were exercised;
- [ ] the practical exercise was tested or explicitly marked illustrative;
- [ ] Maher can explain the core idea without copying the lesson text;
- [ ] corrections and unresolved questions are recorded.

This file tracks curriculum status. Individual understanding, quiz answers, and session-specific observations belong in a learning record under `learning-records/`.

---

## 11. Change history

| Date | Change |
|---|---|
| 2026-08-30 | Created the teaching-first curriculum and defined the first lesson scope, visuals, exercises, and repository truth. |
| 2026-08-30 | Established the reusable Lesson Overview Sheet standard and added the concept-complete 12-station Lesson 0001 PNG. |
| 2026-08-30 | Rebasing work: applied the Maher Brand System v1.1 to the shared lesson styling and Lesson 0001, including offline Poppins assets and a rebuilt technical overview sheet. |
| 2026-09-03 | Added Lesson 0002, its concept-complete portrait overview sheet, interactive decoding diagrams, project-specific exercises, and validation status. |
| 2026-09-03 | Added Lessons 0003–0009 with concept-complete portrait overview sheets, repository-specific explanations, exercises, quizzes, and validation metadata. |
