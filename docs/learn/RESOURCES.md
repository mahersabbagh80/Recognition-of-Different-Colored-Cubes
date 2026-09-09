# Machine Learning and Computer Vision Resources

Last reviewed: 2026-09-07

This is the source shelf for the fundamentals-first course. Lessons use the smallest relevant section of a source; they do not require reading a textbook cover to cover.

## Knowledge: foundations

- [Richard Szeliski — Computer Vision: Algorithms and Applications, 2nd ed.](https://szeliski.org/Book/)
  Primary computer-vision reference for image formation, filtering, recognition, geometry, and depth. The author provides an official personal-use electronic edition.
- [Goodfellow, Bengio, and Courville — Deep Learning](https://www.deeplearningbook.org/)
  Reference for machine-learning basics, feedforward networks, optimization, regularization, convolutional networks, and practical methodology. The official HTML edition is free.
- [Dive into Deep Learning](https://en.d2l.ai/)
  Executable companion for data manipulation, classification, generalization, multilayer networks, convolution, transfer learning, bounding boxes, and object detection.
- [PyTorch — Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)
  Official practical reference for tensors, datasets, models, automatic differentiation, optimization, and saved models.
- [PyTorch — Transfer Learning for Computer Vision](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
  Official worked comparison of fine-tuning a pretrained network and using it as a fixed feature extractor.

## Knowledge: detection and evaluation

- [Redmon et al. — You Only Look Once](https://arxiv.org/abs/1506.02640)
  Original one-stage detection paper; use for the high-level “predict boxes and classes together” idea, not for the current export layout.
- [Lin et al. — Microsoft COCO](https://arxiv.org/abs/1405.0312)
  Primary dataset and evaluation reference for object detection in complex scenes.
- [Ultralytics — YOLOv5 and YOLOv5u](https://docs.ultralytics.com/models/yolov5/)
  Official project-family documentation. Always check the installed model and export before assuming a tensor layout.
- [OpenCV — Geometric Image Transformations](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html)
  Official reference for resizing, interpolation, borders, and coordinate mappings such as the project's letterbox transform.

## Knowledge: geometry and robotics integration

- [ROS REP 118 — Depth Images](https://www.ros.org/reps/rep-0118.html)
  Primary ROS convention for depth along the camera Z axis, units, encodings, and invalid readings.
- [ROS 2 Humble — Topics](https://docs.ros.org/en/humble/Concepts/Basic/About-Topics.html)
  Official explanation of nodes exchanging typed messages through topics.
- [ROS 2 Humble — Quality of Service](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
  Official reference for reliability, history, durability, and compatibility of camera and perception streams.
- [cv_bridge repository, Humble branch](https://github.com/ros-perception/vision_opencv/tree/humble/cv_bridge)
  Source and API reference for converting ROS image messages to OpenCV images.
- [ONNX — Introduction](https://onnx.ai/onnx/intro/)
  Official explanation of the portable graph boundary used between training and deployment.
- [NVIDIA TensorRT — Quick Start](https://docs.nvidia.com/deeplearning/tensorrt/latest/getting-started/quick-start-guide.html)
  Official deployment overview for importing, optimizing, and executing a model on NVIDIA hardware.

## Current project evidence

- [Model artifact notes](../../models/README.md)
  Current training data, checkpoint, ONNX and TensorRT contracts, commands, metrics, and known limits.
- [Detection node](../../recognition_of_different_colored_cubes/cube_detection_node.py)
  Current preprocessing, inference, decoding, RGB/depth synchronization, and ROS publication behavior.
- [Geometry filter](../../recognition_of_different_colored_cubes/geometry_filter.py)
  Current depth post-filter behavior; useful as a code-reading example, including a known z-depth sign defect.
- [Architecture](../architecture.md) and [milestones](../milestones.md)
  Intended ROS 2 interfaces and current M5 PARTIAL engineering status.
- [Live evaluation report](../../evaluation/m5_live/report.md)
  Measured deployment evidence under its recorded conditions.

## Lesson-to-source map

| Lessons | Primary foundation | Main project evidence |
|---|---|---|
| 0001–0003 | Szeliski; D2L | Project definition; detection node preprocessing |
| 0004–0005 | Deep Learning; D2L; PyTorch basics | Model notes and training record |
| 0006 | Deep Learning practical methodology; D2L generalization | Dataset splits and M5 evidence |
| 0007–0008 | D2L CNN and transfer-learning chapters; PyTorch tutorials | Current pretrained/fine-tuned artifacts |
| 0009–0010 | YOLO and COCO papers; D2L detection | Export contract, decoder, evaluation reports |
| 0011 | Szeliski; REP 118 | Geometry filter and depth handling |
| 0012 | ROS 2, cv_bridge, ONNX, and TensorRT official docs | Architecture, node, model notes, milestones |

## Wisdom: practitioner communities

- [Robotics Stack Exchange](https://robotics.stackexchange.com/)
  Use for focused, reproducible questions about ROS, cameras, calibration, and robot perception.
- [Open Robotics Discourse](https://discourse.ros.org/)
  Use for ecosystem design discussions and announcements; focused troubleshooting is usually better on Robotics Stack Exchange.
- [NVIDIA Developer Forums — TensorRT](https://forums.developer.nvidia.com/c/ai-data-science/deep-learning/tensorrt/92)
  Use for device- and version-specific engine behavior after recording JetPack, CUDA, and TensorRT versions.

## Gaps

- No recurring practitioner or local robotics reviewer has been selected.
- The physical depth-filter assumptions still require validation with registered RGB/depth data after the known predicate defect is corrected.

## Source rules

- For general ideas, prefer the books, papers, and official documentation above.
- For what this checkout does, verify current code and artifacts.
- Do not transfer an example tensor shape or class order from another YOLO version.
- Treat community advice as a hypothesis until reproduced.
- Label illustrative numbers as examples and measured numbers with their conditions.

## Sources checked for the interactive revision

- [Torchvision NMS](https://docs.pytorch.org/vision/stable/generated/torchvision.ops.nms.html): strict overlap cutoff and box suppression.
- [Official COCO evaluator](https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/cocoeval.py): one-to-one matching, IoU thresholds, precision/recall averaging.
- [ROS node definition, official Humble source](https://github.com/ros2/ros2_documentation/blob/humble/source/Concepts/Basic/About-Nodes.rst): nodes can share a process.
- [ROS REP 103, official source](https://github.com/ros-infrastructure/rep/blob/master/rep-0103.rst): optical camera axes and robot coordinate conventions.
- [ROS REP 118, official source](https://github.com/ros-infrastructure/rep/blob/master/rep-0118.rst): optical-axis depth, meters, millimeters, invalid data.
- [ROS QoS, official Humble source](https://github.com/ros2/ros2_documentation/blob/humble/source/Concepts/Intermediate/About-Quality-of-Service-Settings.rst): delivery policies and compatibility. Official source mirrors are useful when rendered ROS pages block automated access.

Interactive controls use deliberately small hypothetical examples. They are not live model inference, robot measurements, or evidence of learner mastery.

## Training code connections (reviewed 2026-09-08)

The application sections now trace dataset preparation in `scripts/normalize_dataset.py` and `scripts/build_hardneg_dataset.py`, fine-tuning in `scripts/finetune_hardneg.py`, prediction reporting in `scripts/validate_hardneg.py`, and the runtime handoff. `training/train.ipynb` currently contains instructions only. Repository scripts are evidence of implementation, not proof of training success or independent test performance.

[Ultralytics training documentation](https://docs.ultralytics.com/modes/train/) explains batch size, initial learning rate, optimizer selection, freezing, and augmentation arguments. These are living API documents; use explicit script settings and recorded run information when describing this project.
