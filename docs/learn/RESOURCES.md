# Resources: Computer vision for the colored-cube detector

Last reviewed: 2026-09-06

This is the canonical source shelf for the lessons in this directory. It is intentionally small. The goal is not to collect everything about machine learning; it is to give us dependable references for understanding, changing, and reviewing this project.

Access audit: 2026-09-06. Every retained external link below is directly readable with the available research tools. The Szeliski book also has a verified personal-use copy stored locally outside Git.

## How to use this shelf

When a lesson makes a technical claim, use the sources in this order:

1. **Current project evidence:** code, model metadata, export commands, tests, and measured outputs. This defines what this checkout actually does.
2. **Project documentation:** `README.md`, `models/README.md`, `docs/technical-stack.md`, lesson specifications, and experiment notes.
3. **Primary external documentation:** the official documentation for Ultralytics, PyTorch, OpenCV, ONNX, TensorRT, and ROS 2.
4. **Foundational books and papers:** use these to explain the underlying ideas and vocabulary.
5. **Community discussions:** useful for troubleshooting and alternative viewpoints, but never the sole authority for the current model contract.

For every new or revised lesson, record the relevant local file or artifact first, then link the external source that explains the general concept. Do not copy entire books or downloadable PDFs into the repository; keep stable links and our own project-specific explanations instead.

## Recommended core books

These three references complement one another. We do not need to read all three cover to cover.

### 1. Computer vision foundation

- [Richard Szeliski — Computer Vision: Algorithms and Applications, 2nd ed.](https://szeliski.org/Book/)
  Best broad computer-vision reference for images, geometry, feature representations, recognition, and the reasoning behind vision algorithms. The author provides an official electronic version for personal use; the repository should link to the official page rather than redistribute it.
  Verified local personal-use copy: `/home/maher/Dokumente/Books and Sources/Szeliski_CVAABook_2ndEd.pdf`.

### 2. Deep-learning foundation

- [Goodfellow, Bengio, and Courville — Deep Learning](https://www.deeplearningbook.org/)
  Best reference for the mathematical and conceptual backbone: tensors, probability, optimization, regularization, convolutional networks, and practical methodology. The official HTML edition is free to read online. Use it as a reference, not as the first book to read linearly.

### 3. Practical, executable companion

- [Dive into Deep Learning](https://en.d2l.ai/)
  Best hands-on companion. It combines explanations, mathematics, and executable code, and has directly relevant sections on image augmentation, fine-tuning, bounding boxes, multiscale detection, CNNs, optimization, and computational performance.

## Project-specific authority

These files outrank any generic explanation when they describe the current checkout:

- [`models/README.md`](../../models/README.md) — model input/output contract, class order, export settings, and TensorRT notes.
- [`recognition_of_different_colored_cubes/cube_detection_node.py`](../../recognition_of_different_colored_cubes/cube_detection_node.py) — camera preprocessing, inference, output decoding, confidence filtering, inverse letterboxing, NMS, and ROS publication.
- [`scripts/m3_smoke_inference.py`](../../scripts/m3_smoke_inference.py) — read-only inspection of the exported model and a real inference result.
- [`docs/technical-stack.md`](../technical-stack.md) — the intended training, export, deployment, and ROS stack.
- [`docs/learn/LESSON-PLAN.md`](LESSON-PLAN.md) — learning objectives, scope boundaries, and evidence requirements for the lesson sequence.

For example, the current project contract is `[1, 3, 640, 640]` input and `[1, 7, 8400]` output. That is evidence about this exported artifact, not a universal rule for every YOLO model.

## Official technical references

### Computer vision and image preparation

- [OpenCV — Geometric Image Transformations](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html)
  Reference for resizing, interpolation, border handling, and coordinate transformations. Use it when explaining why letterboxing preserves aspect ratio and why the decoder must undo the same transform.

### PyTorch and training

- [PyTorch — Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)
  A current step-by-step workflow covering tensors, datasets, transforms, model construction, automatic differentiation, optimization, and saving/loading models.
- [PyTorch — Transfer Learning for Computer Vision](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
  Use for the distinction between fine-tuning a pretrained model and using it as a fixed feature extractor.

### YOLO and object detection

- [Ultralytics — YOLOv5 and YOLOv5u model documentation](https://docs.ultralytics.com/models/yolov5)
  Official model and usage documentation, including the YOLOv5u anchor-free, objectness-free split-head behavior relevant to this checkout. Check the installed package and actual export before transferring any output-shape example into this project.
- [Ultralytics — Export mode](https://docs.ultralytics.com/modes/export/)
  Official export options for formats such as ONNX and TensorRT, including image size, dynamic shapes, and precision settings.
- [Redmon et al. — You Only Look Once: Unified, Real-Time Object Detection](https://arxiv.org/abs/1506.02640)
  Original YOLO paper. Use for historical and high-level one-stage-detection intuition, not for the current exported tensor layout.

### ONNX and deployment

- [ONNX — Introduction](https://onnx.ai/onnx/intro/)
  Official explanation of graphs, nodes, tensors, model inputs/outputs, operator sets, and model metadata.
- [NVIDIA TensorRT — Quick Start Guide](https://docs.nvidia.com/deeplearning/tensorrt/latest/getting-started/quick-start-guide.html)
  Current deployment overview: export, choose precision, convert to an engine, and deploy. It also explains why the best workflow depends on the target hardware and runtime.
- [NVIDIA TensorRT 8.6 Developer Guide](https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-861/developer-guide/index.html)
  Version-pinned reference for the TensorRT generation used by the project’s historical deployment notes. When current and archived documentation differ, the installed TensorRT version and the built engine are the final authority.
- [NVIDIA TensorRT — ONNX operator support](https://docs.nvidia.com/deeplearning/tensorrt/latest/reference/onnx-opset-guide.html)
  Use when an export imports successfully in one environment but fails in another because of opset or operator support.

### ROS 2 perception wiring

- [ROS 2 Humble — Topics source](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Concepts/Basic/About-Topics.rst)
  Core publisher/subscriber model for camera images and detection outputs.
- [ROS 2 Humble — Quality of Service source](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Concepts/Intermediate/About-Quality-of-Service-Settings.rst)
  Use for camera sensor-data QoS, reliability compatibility, and diagnosing topics that appear connected but do not exchange messages.
- [ROS 2 Humble — `cv_bridge` source](https://github.com/ros-perception/vision_opencv/tree/humble/cv_bridge)
  Reference for converting between `sensor_msgs/Image` and OpenCV images.
- [ROS 2 — `vision_msgs` source](https://github.com/ros-perception/vision_msgs/blob/ros2/README.md)
  Standard message definitions for object-detection results, including `Detection2DArray`.
- [ROS REP 118 — Depth Images source](https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0118.rst)
  Primary ROS convention for depth along the camera Z axis, canonical metre units, the raw `uint16` millimetre representation, and zero as invalid in that raw representation.

## Lesson-to-source map

| Lesson | Main references | What they are for |
|---|---|---|
| 0001 — What YOLO outputs | Project node and model notes; Ultralytics YOLOv5u; original YOLO paper | Separate the project’s output contract from general detection ideas. |
| 0002 — How YOLO produces predictions | Project node and model notes; Ultralytics YOLOv5u; OpenCV transforms | Explain the candidate field, tensor axes, letterboxing, coordinate conversion, and NMS. |
| 0003 — PyTorch and model training | D2L; Goodfellow et al.; PyTorch basics and transfer learning | Explain datasets, labels, optimization, validation, checkpoints, and fine-tuning. |
| 0004 — Why the model fails on the robot | Szeliski; D2L image augmentation; project evaluation evidence | Connect appearance changes, data coverage, camera conditions, and generalization. |
| 0005 — ONNX and TensorRT | ONNX introduction; Ultralytics export; NVIDIA TensorRT guides | Explain model exchange, export settings, precision, engine building, and hardware-specific deployment. |
| 0006 — ROS 2 perception wiring | ROS 2 topics, QoS, `cv_bridge`, and `vision_msgs`; project node | Explain message flow, image conversion, QoS compatibility, and detection messages. |
| 0007 — Depth and geometry filtering | Szeliski; project node and calibration/evaluation evidence | Explain image coordinates versus physical geometry and why depth/calibration are needed. |
| 0008 — Evaluation and fine-tuning | D2L; PyTorch transfer learning; project evaluation scripts | Choose data, metrics, hard negatives, and fine-tuning experiments based on evidence. |
| 0009 — Project walkthrough | All project-specific authority files plus the relevant source above | Practice explaining the actual system without confusing it with a generic YOLO pipeline. |

## Wisdom: practitioner communities

Use these places for troubleshooting patterns, implementation experience, and alternative explanations. Community answers are leads to test, not substitutes for the current checkout, official documentation, or measured evidence.

- [Open Robotics Discourse](https://discourse.ros.org/) — ROS announcements and broad design or ecosystem discussion. Its own guidance routes focused technical questions to a Q&A site.
- [Robotics Stack Exchange](https://robotics.stackexchange.com/) — focused, reproducible ROS and robotics engineering questions. Include versions, topic types, QoS details, minimal logs, and what has already been tested.
- [NVIDIA TensorRT forum](https://forums.developer.nvidia.com/c/ai-data-science/deep-learning/tensorrt/92) and [Jetson Systems forum](https://forums.developer.nvidia.com/c/robotics-edge-computing/jetson-systems/70) — target-specific engine, CUDA, JetPack, camera, and performance troubleshooting. State the exact Jetson, JetPack, CUDA, and TensorRT versions.
- [Ultralytics Discussions](https://github.com/orgs/ultralytics/discussions) — training, export, and decoder questions. Always attach the installed Ultralytics version and the actual input/output metadata because examples from another YOLO generation may not match this project.

## Known source gaps

- No recurring practitioner or local robotics reviewer has been selected for this project. Community review is currently requested only when a concrete technical question arises.
- The physical interpretation of the geometry filter still needs review against registered RGB/depth hardware evidence after its depth-sign defect is corrected.
- Community threads are intentionally not pinned as factual authorities: version-specific advice must be reproduced locally and promoted into a lesson only when code, artifacts, or primary documentation confirms it.

## Maintenance rules

- Prefer official documentation and stable landing pages over blog posts or copied snippets.
- Pin a source to a version when behavior depends on a version: for example, ROS 2 Humble or TensorRT 8.6.
- When the model, export command, dependency version, or decoder changes, re-check the affected source links and lesson claims.
- When a lesson describes a tensor shape, field order, class order, threshold, image size, or coordinate transform, verify it against the current artifact or code before publishing the lesson.
- Keep historical references labelled as historical. Do not use old output examples such as the traditional YOLOv5 `(1, 25200, 85)` layout as evidence for the current YOLOv5u-style export.
- Community discussions may suggest hypotheses or troubleshooting steps, but a claim becomes lesson material only after it is confirmed by project evidence or primary documentation.
- Add a short note to this file when a source is replaced, deprecated, or found to be misleading for this checkout.

## Historical and supplementary references

- [Ultralytics YOLOv5 issue 6998](https://github.com/ultralytics/yolov5/issues/6998) — historical maintainer discussion about the older YOLOv5 output format. It is retained for comparison only and does **not** describe the current model contract.
- [Ultralytics discussions](https://github.com/ultralytics/ultralytics/discussions) — troubleshooting and alternative viewpoints only; not an authority for this model artifact.
