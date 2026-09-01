# Colored-Cube Computer-Vision Learning Plan

**Status:** Active learning plan<br>
**Audience:** Maher — beginner in computer vision, learning through a real ROS 2 robotics project<br>
**Repository:** `Recognition-of-Different-Colored-Cubes`<br>
**Created:** 2026-08-30<br>
**Last updated:** 2026-08-30<br>
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
| 0002 | How YOLO Produces Predictions | Why does YOLO create many candidates, and how do decoding and NMS produce final boxes? | `_decode_yolov5_output`, `models/README.md` | Planned |
| 0003 | PyTorch and Model Training | What are datasets, labels, epochs, validation, checkpoints, and fine-tuning? | `models/best.pt`, `models/README.md`, training artifacts | Planned |
| 0004 | Why the Model Fails on the Robot | Why can validation look good while live inference fails? | M4/M5 evaluation reports, domain-gap evidence | Planned |
| 0005 | ONNX and TensorRT | Why does the model travel through `best.pt → best.onnx → best.engine`? | `models/README.md`, export and TensorRT scripts | Planned |
| 0006 | ROS 2 Perception Wiring | How do nodes, topics, messages, `cv_bridge`, and QoS connect the detector? | `cube_detection_node.py`, `package.xml`, launch/config files | Planned |
| 0007 | Depth and Geometry Filtering | How does depth provide a second check for a raised cube-like object? | `geometry_filter.py`, M4c1 evidence | Planned |
| 0008 | Evaluation and Fine-Tuning | How do we measure success and improve the model responsibly? | `evaluation/`, `docs/evaluation.md`, M3d-revived plan | Planned |
| 0009 | Project Walkthrough and Interview Practice | Can Maher explain the complete system, trade-offs, failures, and next steps? | Full repository and evidence | Planned |

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

## 6. Repository-specific truth to preserve

- The canonical current engineering status is **M5 PARTIAL**.
- The current node synchronizes RGB and depth images in `_sync_cb`.
- The current model artifact is documented as a fused-decode output with shape `[1, 7, 8400]`.
- The current model/node class order is `0: blue_cube`, `1: green_cube`, `2: red_cube`.
- `docs/project-definition.md` still contains a different class-ID table (`0: red_cube`, `1: green_cube`, `2: blue_cube`). This documentation conflict must be reconciled before another fine-tuning run; lessons should call it out rather than silently choosing an interpretation.
- The M5 geometry filter is a second, depth-based evidence check. It does not replace YOLO and cannot recover a class that the model never proposes.
- The HiWonder vendor packages are reference/infrastructure material and must not be modified.

---

## 7. Source hierarchy

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

## 8. Progress tracking

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

## 9. Change history

| Date | Change |
|---|---|
| 2026-08-30 | Created the teaching-first curriculum and defined the first lesson scope, visuals, exercises, and repository truth. |
| 2026-08-30 | Established the reusable Lesson Overview Sheet standard and added the concept-complete 12-station Lesson 0001 PNG. |
| 2026-08-30 | Rebasing work: applied the Maher Brand System v1.1 to the shared lesson styling and Lesson 0001, including offline Poppins assets and a rebuilt technical overview sheet. |
