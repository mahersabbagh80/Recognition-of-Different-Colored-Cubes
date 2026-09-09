# Computer Vision and Machine Learning Glossary

> **Source glossary:** this long-form Markdown file remains the vocabulary source. For printable learner-facing summaries, use [`reference/index.html`](index.html) and its five compact HTML quick-reference sheets.

**Status:** Living reference  
**Audience:** Maher — learning computer vision through the colored-cube detector  
**Created:** 2026-09-01  
**Scope:** General computer-vision and machine-learning terminology, with special attention to the YOLOv5, TensorRT, depth-camera, and ROS 2 concepts used by this project.

This glossary is intentionally **not bounded to one lesson**. Every lesson defines the technical vocabulary it uses locally. This glossary is an additional reference, not a prerequisite for reading a lesson.

## How to use this glossary

- Read the **Definition** first. It is the short, general meaning.
- Read **In this project** for the concrete connection to the JetRover detector.
- Use **Related terms** to follow the concept to its neighbours.
- Treat repository-specific facts as implementation facts, not universal definitions.
- When a term has several meanings, the meaning used in this project is stated explicitly.

The glossary favours an intuitive explanation first and technical precision second. It is a learning reference, not a replacement for the official documentation linked at the end.

## Project snapshot

The current high-level data flow is:

```text
RGB + depth camera
    -> ROS 2 image messages
    -> cv_bridge / OpenCV arrays
    -> BGR-to-RGB conversion, letterbox, normalization
    -> documented YOLOv5u-style TensorRT inference
    -> candidate decoding, confidence filtering, NMS
    -> depth/geometry KEEP or REJECT decision
    -> ROS 2 detection messages and debug image
```

Current project-specific facts:

- Target classes: `red_cube`, `green_cube`, and `blue_cube`.
- Current runtime class order in `cube_detection_node.py`: `0: blue_cube`, `1: green_cube`, `2: red_cube`.
- Model artifact chain: `models/best.pt` -> `models/best.onnx` -> `models/best.engine`.
- Main RGB input: `/depth_cam/rgb/image_raw` (`sensor_msgs/Image`).
- Depth input (RGB registration still requires hardware validation): `/depth_cam/depth/image_raw` (`uint16` millimetres).
- Standard detection output: `/cube_detections` (`vision_msgs/Detection2DArray`).
- Vendor-compatible output: `/cube_detections/vendor_objects` (`interfaces/ObjectsInfo`).
- Human-readable output: `/cube_detections/debug_image` (`sensor_msgs/Image`).
- The current M5 status is **PARTIAL**: the node and filter are live, but the model does not reliably detect the real cubes in the JetRover room at the production threshold. The geometry filter cannot recover an object the model never proposes.

> **Class-ID warning:** `models/README.md` and the running node use `0: blue_cube`, `1: green_cube`, `2: red_cube`. `docs/project-definition.md` currently contains a different class-ID table. This documentation conflict must be reconciled before another training or fine-tuning run.

---

## 1. Image and computer-vision foundations

### Computer vision

**Definition:** The field of making useful measurements or interpretations from images and video.

**In this project:** Computer vision is used to locate and classify colored cubes in frames from the JetRover camera.

**Related terms:** image, object detection, inference, frame.

### Image

**Definition:** A structured grid of measurements representing a visual scene. In a digital camera image, those measurements are usually pixel values.

**In this project:** The camera publishes an RGB image as a ROS 2 `sensor_msgs/Image` message.

**Related terms:** pixel, channel, image array, resolution.

### Frame

**Definition:** One image from a video stream at a particular point in time.

**In this project:** The node processes synchronized RGB and depth frames. It does not treat the entire video as one object; it handles the stream one frame at a time.

**Related terms:** timestamp, synchronization, throughput, FPS.

### Pixel

**Definition:** One small, addressable element of a digital image. A pixel stores one or more numerical values.

**In this project:** Pixel coordinates are used to describe the corners and size of a cube's bounding box.

**Related terms:** channel, coordinate system, bounding box.

### Channel

**Definition:** One numeric component of an image. A normal colour image commonly has three channels.

**In this project:** The colour channels are represented as blue, green, and red in the OpenCV image and reordered to red, green, blue before network inference.

**Related terms:** RGB, BGR, tensor, colour space.

### Image array

**Definition:** An array of numbers holding the pixels of an image. A common colour-image layout is height x width x channels.

**In this project:** `cv_bridge` converts a ROS image message into an OpenCV/Numpy array that the Python node can manipulate.

**Related terms:** tensor, channel, preprocessing.

### Tensor

**Definition:** A multi-dimensional numerical container. A scalar, vector, matrix, or higher-dimensional array can all be viewed as tensors.

**In this project:** The model input and output are tensors. The runtime input is arranged as a batch of three-channel 640 x 640 images.

**Related terms:** array, batch, output tensor, static shape.

### RGB

**Definition:** A colour-channel order: red, green, blue.

**In this project:** The neural network expects the prepared image in RGB channel order.

**Related terms:** BGR, channel, colour space.

### BGR

**Definition:** A colour-channel order: blue, green, red.

**In this project:** OpenCV commonly uses BGR. The node requests `bgr8` from `cv_bridge` and reverses the channel order in `_infer()` before sending the frame to the model.

**Related terms:** RGB, `cv_bridge`, `_infer()`.

### Colour space

**Definition:** A convention for describing colours numerically, such as RGB, BGR, HSV, or Lab.

**In this project:** The inference path uses BGR OpenCV data and converts it to RGB. The project does not use a classical colour-thresholding pipeline as its detector.

**Related terms:** RGB, BGR, channel.

### Image resolution

**Definition:** The number of pixels in an image, usually expressed as width x height.

**In this project:** The camera frames are 640 x 360, while the model expects a prepared 640 x 640 input.

**Related terms:** resize, letterbox, static shape.

### Aspect ratio

**Definition:** The proportional relationship between an image's width and height, or between the sides of a box.

**In this project:** `_letterbox()` preserves the camera frame's aspect ratio when preparing a square model input. The geometry filter also uses a 3D aspect-related check to reject some non-cube shapes.

**Related terms:** resize, letterbox, bounding box, geometry filter.

### Image coordinate system

**Definition:** The convention used to locate pixels in an image.

**In this project:** The origin is at the top-left; x increases to the right and y increases downward.

**Related terms:** pixel, bounding box, `xyxy`.

### Bounding box

**Definition:** A rectangle used to approximate an object's location in an image.

**In this project:** The project uses the corner form `(x_min, y_min, x_max, y_max)` internally and in the vendor-compatible `ObjectInfo.box` field.

**Related terms:** axis-aligned bounding box, localization, detection, IoU.

### Axis-aligned bounding box

**Definition:** A bounding box whose edges remain parallel to the image's horizontal and vertical axes. It cannot rotate with the object.

**In this project:** The YOLOv5 detector produces axis-aligned boxes. Polygon labels in the original Roboflow export were normalized into axis-aligned boxes before training.

**Related terms:** bounding box, segmentation, annotation.

### Region of interest (ROI)

**Definition:** A selected part of an image that should receive attention or processing.

**In this project:** The current detector processes the complete camera frame. An ROI could be added later to restrict processing to a known workspace, but it is not required by the current pipeline.

**Related terms:** crop, preprocessing, bounding box.

### Resize

**Definition:** Changing an image's pixel dimensions.

**In this project:** The image is resized as part of `_letterbox()` so that it can be fed to the fixed-size model input.

**Related terms:** resolution, aspect ratio, letterbox, padding.

### Letterbox

**Definition:** Resize an image while preserving its aspect ratio, then add padding so it fits a required rectangular or square input size.

**In this project:** `_letterbox()` prepares the camera frame for the model and returns the scale and padding needed to map predicted boxes back to the original frame.

**Related terms:** resize, padding, preprocessing, coordinate transform.

### Padding

**Definition:** Extra pixels added around an image to reach a required size.

**In this project:** The letterbox step adds constant-value borders around the resized frame. Those borders must be accounted for when decoding boxes.

**Related terms:** letterbox, preprocessing, coordinate transform.

### Normalization

**Definition:** Transforming numeric inputs into a consistent scale or range before they are processed by a model.

**In this project:** The prepared image values are converted to `float32` and divided by 255 before inference.

**Related terms:** preprocessing, tensor, input representation.

### Annotation

**Definition:** Human- or tool-provided information attached to an image, such as an object's class and location.

**In this project:** Training annotations identify cube classes and their bounding boxes.

**Related terms:** label, ground truth, dataset, segmentation.

### Segmentation

**Definition:** A computer-vision task that assigns labels to pixels or produces a mask describing an object's shape.

**In this project:** The detector is a bounding-box detector, not a segmentation model. The source Roboflow export contained polygon-style labels that were converted to boxes for detection training.

**Related terms:** object detection, mask, polygon, axis-aligned bounding box.

---

## 2. Machine learning and dataset concepts

### Machine learning

**Definition:** A family of methods that learn patterns from examples instead of being programmed with every rule explicitly.

**In this project:** The YOLOv5 model learns visual patterns associated with the three cube classes from labelled training images.

**Related terms:** model, training, inference, dataset.

### Model

**Definition:** A learned computational function that maps inputs to outputs.

**In this project:** The YOLOv5s model maps an image tensor to numerical object-detection predictions.

**Related terms:** weights, checkpoint, inference, architecture.

### Parameter

**Definition:** A numerical value learned by a model during training.

**In this project:** The model contains millions of learned parameters whose values are stored in the weight files.

**Related terms:** weight, model, checkpoint, training.

### Weight

**Definition:** A learned model parameter. The word often refers collectively to the learned numerical state of a model.

**In this project:** The weights are stored in `models/best.pt` and are carried through the ONNX export into the deployment engine.

**Related terms:** parameter, checkpoint, `.pt`, fine-tuning.

### Dataset

**Definition:** A collection of examples used to develop or evaluate a model.

**In this project:** The initial dataset came from the Roboflow red-green-blue cube-detection project and contains images plus cube annotations.

**Related terms:** sample, annotation, training set, validation set, test set.

### Sample

**Definition:** One example in a dataset, such as one image and its labels.

**In this project:** One camera image containing one or more cube annotations is a training or evaluation sample.

**Related terms:** dataset, label, ground truth, frame.

### Label

**Definition:** The target answer attached to a training example.

**In this project:** A label identifies a cube class and, for detection training, its location.

**Related terms:** annotation, class, ground truth, bounding box.

### Ground truth

**Definition:** The reference answer used to judge a model prediction. It is normally created by a human or trusted measurement process.

**In this project:** A hand-labelled cube bounding box is ground truth for evaluating whether a predicted box is correct.

**Related terms:** label, annotation, IoU, true positive.

### Supervised learning

**Definition:** Learning from examples that include target answers.

**In this project:** YOLOv5 is trained with images and annotations that specify the expected cube classes and locations.

**Related terms:** dataset, label, training, ground truth.

### Training

**Definition:** The process of adjusting model parameters so that predictions better match the training targets.

**In this project:** The project trained a YOLOv5s checkpoint from the approved Roboflow-format dataset. Training is performed on the development PC, not during live robot inference.

**Related terms:** epoch, loss function, optimizer, learning rate, fine-tuning.

### Epoch

**Definition:** One complete pass through the training data.

**In this project:** The M2 training recipe used 30 epochs. An epoch is a training-loop unit; it is not the same as one live inference frame.

**Related terms:** batch, training, checkpoint.

### Batch

**Definition:** A group of samples processed together during one training or inference operation.

**In this project:** Training used a batch size of 16. The deployed ROS node uses a batch of one camera frame at a time.

**Related terms:** tensor, epoch, throughput.

### Loss function

**Definition:** A numerical measure of how far a model's predictions are from the target answers during training.

**In this project:** YOLO training combines losses related to box location and class prediction. Lower loss generally indicates better agreement with the training targets, but loss alone does not prove live-camera performance.

**Related terms:** training, optimizer, ground truth, validation.

### Optimizer

**Definition:** The training algorithm that uses the loss signal to update model parameters.

**In this project:** The M2 recipe used AdamW, selected by the Ultralytics training run.

**Related terms:** loss function, learning rate, parameter, training.

### Learning rate

**Definition:** A training hyperparameter controlling how large each parameter update is.

**In this project:** The active fine-tuning plan specifies a lower starting learning rate than the original M2 training recipe to adapt the model without changing it too aggressively.

**Related terms:** optimizer, hyperparameter, fine-tuning.

### Hyperparameter

**Definition:** A setting chosen by the engineer before or around training, rather than learned directly as a model weight.

**In this project:** Epoch count, image size, batch size, learning rate, augmentation settings, and confidence thresholds are examples of settings that must be chosen and documented.

**Related terms:** learning rate, epoch, batch, confidence threshold.

### Checkpoint

**Definition:** A saved snapshot of a model's learned state, often including weights and metadata.

**In this project:** `models/best.pt` is a PyTorch/Ultralytics checkpoint selected from training results.

**Related terms:** weight, `.pt`, best model, fine-tuning.

### Fine-tuning

**Definition:** Continuing training from an existing model using new or more task-specific data.

**In this project:** Fine-tuning on JetRover-room images is the recommended path for improving positive detection of the real cubes under the robot's camera conditions.

**Related terms:** domain gap, training, checkpoint, generalization.

### Data augmentation

**Definition:** Creating varied training examples by applying transformations such as scale, crop, flip, or colour changes.

**In this project:** Augmentation helps the detector encounter visual variation during training, but it cannot guarantee that the training data represents the JetRover room.

**Related terms:** dataset, generalization, domain gap.

### Overfitting

**Definition:** When a model performs well on examples similar to its training data but poorly on new examples.

**In this project:** Strong results on the small Roboflow validation set do not guarantee strong results on the JetRover camera view.

**Related terms:** generalization, domain gap, validation set.

### Generalization

**Definition:** A model's ability to perform well on new data rather than only on the examples it saw during training.

**In this project:** The desired generalization target is from Roboflow images to real JetRover-room images at the operating distance and camera angle.

**Related terms:** overfitting, domain gap, test set.

### Domain gap

**Definition:** A difference between the data distribution used for training and the data distribution encountered in deployment.

**In this project:** Lighting, camera viewpoint, scale, floor appearance, and cube presentation can differ between the Roboflow dataset and the JetRover room. This is the main explanation being investigated for the current M5 positive-detection failure.

**Related terms:** generalization, fine-tuning, deployment.

### Data leakage

**Definition:** An evaluation mistake in which information from the evaluation data influences training, making the measured result look better than it really is.

**In this project:** Training and evaluation images must be kept separate when measuring whether a fine-tuned model truly works on new JetRover frames.

**Related terms:** validation set, test set, evaluation, overfitting.

### Feature

**Definition:** A pattern or representation that helps a model distinguish inputs or objects.

**In this project:** The network learns visual features such as edges, surfaces, colour patterns, and object arrangements rather than receiving a hand-written rule saying what a cube looks like.

**Related terms:** model, backbone, generalization.

---

## 3. Object detection and YOLO concepts

### Classification

**Definition:** Predicting which category or categories describe an entire input image or crop.

**In this project:** Classification alone would answer that a cube is present but would not identify every cube's position in the full camera frame.

**Related terms:** object detection, class, label.

### Localization

**Definition:** Estimating where an object is located in an image.

**In this project:** The bounding box is the detector's 2D localization of a cube.

**Related terms:** bounding box, object detection, IoU.

### Object detection

**Definition:** Predicting both what objects are present and where each object is located, usually with one bounding box per detected instance.

**In this project:** The detector searches for multiple `red_cube`, `green_cube`, and `blue_cube` instances in each frame.

**Related terms:** classification, localization, bounding box, confidence score.

### Instance

**Definition:** One individual occurrence of an object, even when several occurrences share the same class.

**In this project:** Three blue cubes in one image are three instances of the `blue_cube` class and should produce three detections if the model can distinguish them.

**Related terms:** class, object detection, bounding box.

### Class

**Definition:** A category the model is trained to recognize.

**In this project:** The three classes are `red_cube`, `green_cube`, and `blue_cube`.

**Related terms:** class ID, label, classification.

### Class ID

**Definition:** A numerical identifier used internally to represent a class.

**In this project:** The current model mapping is `0: blue_cube`, `1: green_cube`, `2: red_cube`.

**Related terms:** class, class order, output tensor.

### Class order

**Definition:** The agreed ordering that maps numerical class IDs to human-readable class names.

**In this project:** Class order must remain consistent across dataset labels, `models/best.pt`, ONNX metadata, TensorRT inference, and ROS output conversion.

**Related terms:** class ID, label, model metadata.

### Inference

**Definition:** Applying a trained model to new input data to produce predictions.

**In this project:** The live node performs inference on each prepared camera frame using the TensorRT engine.

**Related terms:** forward pass, model, TensorRT, post-processing.

### Forward pass

**Definition:** One execution of a model that transforms an input into an output without updating its learned parameters.

**In this project:** The TensorRT execution in `_infer()` is the model's forward pass for one frame.

**Related terms:** inference, training, output tensor.

### Detection candidate

**Definition:** A preliminary model proposal that may describe an object but has not yet passed all filtering stages.

**In this project:** The decoder creates candidates from the YOLO output; confidence filtering, NMS, and the depth/geometry check determine which candidates survive.

**Related terms:** confidence score, post-processing, NMS, geometry filter.

### Confidence score

**Definition:** A model-generated score expressing how strongly the model supports a candidate prediction according to its learned scoring system.

**In this project:** The score is stored in `CubeDetection.score` and published as the detection hypothesis score.

A confidence score is **evidence, not a guarantee of truth**. A high score does not prove that the object is correct, and a low score does not prove that no object exists.

**Related terms:** confidence threshold, precision, recall, false positive.

### Confidence threshold

**Definition:** A minimum score required for a candidate to continue through the pipeline.

**In this project:** The default is `0.50`. Candidates below it are removed before the geometry filter is applied.

Raising the threshold usually makes the system more selective; lowering it usually allows more candidates through. Neither change automatically fixes a model that fails to propose the target object.

**Related terms:** confidence score, post-processing, false positive, false negative.

### False positive

**Definition:** A prediction that claims an object is present when it is not a correct match.

**In this project:** A floor texture, decal, or coloured package incorrectly proposed as a cube is a false positive.

**Related terms:** precision, confidence threshold, hard negative.

### False negative

**Definition:** A real object that the detector fails to report or fails to match correctly.

**In this project:** A visible JetRover-room cube that produces no accepted detection is a false negative in the deployed system.

**Related terms:** recall, domain gap, confidence threshold.

### True positive

**Definition:** A predicted object that correctly matches a ground-truth object according to the chosen evaluation rules.

**In this project:** A correctly classified cube with sufficient box overlap is a true positive.

**Related terms:** ground truth, IoU, precision, recall.

### True negative

**Definition:** A non-object or negative case that the system correctly leaves undetected.

**In this project:** An empty scene with no published cube detections is evidence of correct negative behaviour, although object-detection metrics must be defined carefully because images contain many possible background locations.

**Related terms:** false positive, evaluation, empty scene.

### Intersection over Union (IoU)

**Definition:** A measure of overlap between two boxes: the predicted box and the reference box. It ranges from no overlap to perfect overlap.

**In this project:** IoU is used by NMS to decide whether candidate boxes overlap enough to be treated as duplicates, and by evaluation metrics to judge localization quality.

**Related terms:** bounding box, NMS, ground truth, mAP.

### Non-maximum suppression (NMS)

**Definition:** A post-processing algorithm that reduces several overlapping predictions for one object to a smaller set, usually keeping the strongest-scoring box.

**In this project:** `_decode_yolov5_output()` applies NMS separately by class using the configured IoU threshold.

**Related terms:** confidence score, IoU, post-processing, candidate.

### Post-processing

**Definition:** Operations applied after the model's forward pass to turn raw numerical outputs into usable predictions.

**In this project:** Decoding, confidence filtering, NMS, and depth/geometry decisions are post-processing stages.

**Related terms:** preprocessing, output tensor, NMS, geometry filter.

### Preprocessing

**Definition:** Operations applied to raw input data before it is sent to the model.

**In this project:** BGR-to-RGB conversion, resizing, padding, normalization, channel rearrangement, and batch insertion are preprocessing steps.

**Related terms:** letterbox, normalization, inference, post-processing.

### YOLO

**Definition:** A family of object-detection models whose name comes from “You Only Look Once.” The family performs detection with a single model pass over the image, followed by result processing.

**In this project:** YOLO is the learned detector that proposes cube candidates.

**Related terms:** YOLOv5, one-stage detector, detection head.

### YOLOv5

**Definition:** A version of the YOLO object-detection family associated with the Ultralytics implementation used by this project.

**In this project:** The selected model is YOLOv5s, trained for three cube classes and deployed through TensorRT.

**Related terms:** YOLO, backbone, neck, detection head, TensorRT.

### One-stage detector

**Definition:** An object detector that predicts object locations and classes in one main network pass instead of first generating a separate region-proposal stage.

**In this project:** The one-stage design supports the project's real-time edge-device goal, while preprocessing, post-processing, and ROS overhead still affect total frame rate.

**Related terms:** YOLO, forward pass, latency, throughput.

### Backbone

**Definition:** The part of a neural network that extracts increasingly useful visual features from the input.

**In this project:** The YOLOv5 backbone is an internal model component; the ROS node does not manually operate it.

**Related terms:** feature, neck, detection head.

### Neck

**Definition:** The model component that combines features from different scales before they are passed to the prediction head.

**In this project:** The neck helps the detector use information useful for objects appearing at different image sizes.

**Related terms:** backbone, detection head, multi-scale detection.

### Detection head

**Definition:** The model component that converts learned features into object-detection predictions such as box coordinates and class scores.

**In this project:** The YOLOv5 head contributes to the output tensor consumed by `_decode_yolov5_output()`.

**Related terms:** backbone, neck, output tensor, candidate.

### Output tensor

**Definition:** The numerical tensor produced by a model after inference.

**In this project:** The exported model produces `output0` with shape `[1, 7, 8400]`: four box values plus three class-score values across 8400 candidate positions.

**Related terms:** tensor, output shape, decoder, class ID.

### Fused decode

**Definition:** An export/runtime arrangement in which some output-decoding operations, such as activation or box-related transformations, have already been included in the exported graph.

**In this project:** The current ONNX and TensorRT artifacts are documented as producing a fused-decode output. The decoder still converts the output layout into final image-space boxes and applies NMS.

**Related terms:** output tensor, ONNX, TensorRT, post-processing.

---

## 4. Model formats and deployment

### Framework

**Definition:** A software library or ecosystem used to build, train, export, or execute models.

**In this project:** PyTorch/Ultralytics is used for training and model export; TensorRT is used for the primary Jetson runtime.

**Related terms:** PyTorch, TensorRT, ONNX Runtime.

### PyTorch

**Definition:** A machine-learning framework used to define, train, and execute neural networks.

**In this project:** The original trained model is stored as a PyTorch checkpoint in `models/best.pt`.

**Related terms:** `.pt`, training, export, checkpoint.

### `.pt` checkpoint

**Definition:** A file convention commonly used for PyTorch model checkpoints.

**In this project:** `models/best.pt` is the starting model artifact for the export chain. The file is convenient for PyTorch/Ultralytics but is not the target Jetson deployment format.

**Related terms:** checkpoint, PyTorch, ONNX, weights.

### Export

**Definition:** Converting a model from one representation into another representation suitable for a different tool or runtime.

**In this project:** M3 exports `best.pt` to `best.onnx`; M4 converts the ONNX model into a TensorRT engine.

**Related terms:** ONNX, TensorRT, graph, runtime.

### ONNX

**Definition:** An open model-exchange format that represents a model as a computation graph with standard operators.

**In this project:** ONNX is the required intermediate format between the PyTorch checkpoint and the TensorRT engine. It also enables an ONNX Runtime fallback.

**Related terms:** graph, operator, opset, export.

### ONNX graph

**Definition:** A representation of computation as connected nodes and data values, with inputs flowing through operators to outputs.

**In this project:** `best.onnx` contains the exported computation needed to run the YOLOv5 model outside the original PyTorch training environment.

**Related terms:** ONNX, operator, output tensor.

### Operator

**Definition:** One computation in a model graph, such as convolution, addition, reshape, or activation.

**In this project:** TensorRT must be able to parse and implement the operators present in `best.onnx`.

**Related terms:** ONNX, opset, parser, TensorRT.

### Opset

**Definition:** A versioned set of operator definitions used by an ONNX graph.

**In this project:** `best.onnx` uses opset 13. Opset compatibility is one of the things to check when an exported model is rejected by a deployment runtime.

**Related terms:** ONNX, operator, version compatibility.

### Static shape

**Definition:** A model input or output shape fixed at export or engine-build time.

**In this project:** The current model input is static: batch 1, three channels, 640 x 640 pixels. The ROS node prepares every frame for that shape.

**Related terms:** tensor, input shape, letterbox, TensorRT engine.

### Runtime

**Definition:** The software that executes a model after it has been trained or exported.

**In this project:** TensorRT is the primary runtime on the Jetson. ONNX Runtime is the documented fallback.

**Related terms:** inference, TensorRT, ONNX Runtime, engine.

### ONNX Runtime

**Definition:** A runtime capable of executing models stored in ONNX format.

**In this project:** It is an optional, usually slower fallback if TensorRT conversion or execution is unavailable.

**Related terms:** ONNX, runtime, fallback, inference.

### TensorRT

**Definition:** NVIDIA's inference optimization and execution platform for neural networks, especially on NVIDIA GPUs and Jetson devices.

**In this project:** TensorRT executes the YOLOv5 model on the Jetson GPU and is the primary deployment runtime.

**Related terms:** engine, CUDA, FP16, latency.

### TensorRT engine

**Definition:** A serialized, optimized TensorRT execution plan built for a target environment.

**In this project:** `models/best.engine` is built from `models/best.onnx` on the Jetson. It is the file loaded by the live detector.

**Related terms:** TensorRT, export, serialization, hardware compatibility.

### CUDA

**Definition:** NVIDIA's platform and programming model for using NVIDIA GPUs for general computation.

**In this project:** CUDA provides the GPU execution environment used by TensorRT and the development machine's training stack.

**Related terms:** GPU, TensorRT, CUDA stream.

### GPU

**Definition:** A processor designed for highly parallel numerical computation.

**In this project:** The RTX 4070 Ti is used for development training; the Jetson Orin Nano GPU runs the TensorRT engine.

**Related terms:** CUDA, TensorRT, throughput, FP16.

### FP32

**Definition:** 32-bit floating-point numerical precision.

**In this project:** FP32 is a higher-precision reference or execution mode that can be compared with FP16 when investigating numerical differences.

**Related terms:** FP16, INT8, precision, inference.

### FP16

**Definition:** 16-bit floating-point numerical precision. It uses fewer bits than FP32 and can improve speed or reduce memory use on supported hardware.

**In this project:** The target TensorRT engine uses FP16 paths on the Jetson Orin Nano.

**Related terms:** FP32, INT8, TensorRT, precision.

### INT8

**Definition:** 8-bit integer numerical representation used for more aggressive model quantization and potentially faster, smaller inference.

**In this project:** INT8 is not the current deployment target. It would require careful calibration and accuracy verification before replacing FP16.

**Related terms:** quantization, calibration, FP16, precision.

### Quantization

**Definition:** Representing model values with a lower-precision numerical format.

**In this project:** FP16 is a lower-precision format than FP32; INT8 would be a more aggressive quantization choice.

**Related terms:** FP16, INT8, calibration, accuracy.

### Latency

**Definition:** The time required to complete one operation or one end-to-end processing cycle.

**In this project:** The node records total frame latency, model latency, and geometry-filter latency separately.

**Related terms:** throughput, FPS, benchmark, bottleneck.

### Throughput

**Definition:** The amount of work completed per unit of time.

**In this project:** Live publish rate in frames per second or hertz is a system-throughput measure, not just a measure of TensorRT execution time.

**Related terms:** latency, FPS, queue, benchmark.

### Frames per second (FPS)

**Definition:** The number of video frames processed or published per second.

**In this project:** FPS depends on camera rate, synchronization, preprocessing, TensorRT, post-processing, publishing, and scheduling overhead.

**Related terms:** throughput, latency, benchmark.

### Benchmark

**Definition:** A repeatable measurement of performance under stated conditions.

**In this project:** A TensorRT benchmark may measure engine-only latency, while an M5 live bag measures the complete ROS pipeline. These measurements must not be treated as interchangeable.

**Related terms:** latency, throughput, evaluation, reproducibility.

---

## 5. ROS 2 integration terms

### ROS 2

**Definition:** A robotics middleware ecosystem providing communication, lifecycle, tooling, and conventions for robot software.

**In this project:** ROS 2 connects the vendor camera, the cube detector node, and downstream consumers of detections.

**Related terms:** node, topic, message, QoS.

### Node

**Definition:** A logical computation participant in the ROS 2 communication graph. Multiple nodes can share a process; a node is not the same thing as an operating-system process.

**In this project:** `cube_detection_node` receives images, runs inference, filters candidates, and publishes results.

**Related terms:** topic, publisher, subscriber, callback.

### Topic

**Definition:** A named ROS 2 communication channel for continuous streams of messages.

**In this project:** `/depth_cam/rgb/image_raw` carries camera images; `/cube_detections` carries standard detection arrays.

**Related terms:** publisher, subscriber, message, QoS.

### Publisher

**Definition:** A ROS 2 endpoint that sends messages to a topic.

**In this project:** `cube_detection_node` publishes standard detections, vendor-compatible objects, and an annotated debug image.

**Related terms:** topic, subscriber, message.

### Subscriber

**Definition:** A ROS 2 endpoint that receives messages from a topic.

**In this project:** The detector subscribes to the vendor RGB stream, the depth stream, whose alignment to RGB must be verified, and camera information.

**Related terms:** topic, publisher, callback, synchronization.

### Message

**Definition:** A typed data structure transmitted through a ROS 2 topic.

**In this project:** `sensor_msgs/Image`, `sensor_msgs/CameraInfo`, `vision_msgs/Detection2DArray`, and `interfaces/ObjectsInfo` are message types used by the pipeline.

**Related terms:** topic, interface, header, QoS.

### Quality of Service (QoS)

**Definition:** A set of communication policies describing how ROS 2 messages are delivered, queued, and retained.

**In this project:** The camera subscription uses the sensor-data QoS profile because camera streams commonly prioritize current data over delivery of every old frame.

**Related terms:** topic, subscriber, reliability, queue.

### `sensor_msgs/Image`

**Definition:** A standard ROS 2 message type for image data, including dimensions, encoding, data, and a header.

**In this project:** It is the type of the camera RGB/depth input and the annotated debug-image output.

**Related terms:** `cv_bridge`, image, header, encoding.

### `sensor_msgs/CameraInfo`

**Definition:** A standard ROS 2 message containing camera calibration information and image metadata.

**In this project:** The node reads RGB camera information to obtain or override the intrinsics used by the geometry filter.

**Related terms:** camera intrinsics, calibration, depth, frame ID.

### `cv_bridge`

**Definition:** A ROS package that converts between ROS image messages and OpenCV image representations.

**In this project:** `_sync_cb()` uses `imgmsg_to_cv2()` to convert the RGB and depth messages before inference and geometry processing.

**Related terms:** `sensor_msgs/Image`, OpenCV, BGR, preprocessing.

### Synchronization

**Definition:** Matching messages from different streams that belong to approximately the same moment in time.

**In this project:** An RGB frame must be paired with a corresponding depth frame so that the geometry filter samples depth at the correct scene moment.

**Related terms:** timestamp, approximate synchronization, RGB-depth registration.

### Approximate time synchronizer

**Definition:** A synchronizer that pairs messages whose timestamps are close enough rather than requiring exactly equal timestamps.

**In this project:** `ApproximateTimeSynchronizer` pairs RGB and depth images within the configured synchronization slop.

**Related terms:** synchronization, timestamp, queue, `sync_slop_sec`.

### Header

**Definition:** Metadata attached to many ROS 2 messages, commonly including a timestamp and coordinate-frame identifier.

**In this project:** Detection messages copy the source image header so downstream consumers can relate detections to the camera frame and time.

**Related terms:** timestamp, frame ID, message, `sensor_msgs/Image`.

### Frame ID

**Definition:** The name of the coordinate frame associated with a ROS message.

**In this project:** Camera messages use a camera optical frame identifier. The header allows downstream systems to know which frame the image or detection belongs to.

**Related terms:** header, camera calibration, coordinate frame.

### `vision_msgs/Detection2DArray`

**Definition:** A standard ROS 2 message containing a collection of 2D object detections.

**In this project:** `/cube_detections` publishes the accepted detections using class hypotheses, scores, and 2D bounding-box geometry.

**Related terms:** detection, message, bounding box, standard interface.

### `interfaces/ObjectsInfo`

**Definition:** A project/vendor-specific ROS message containing a collection of object information records.

**In this project:** `/cube_detections/vendor_objects` provides a HiWonder-compatible representation with class name, box, score, and image dimensions.

**Related terms:** `ObjectInfo`, vendor compatibility, message, detection.

### Debug image

**Definition:** An image created to make internal system behaviour visible to a human, often by drawing boxes, labels, scores, or timing information.

**In this project:** `/cube_detections/debug_image` is an annotated overlay intended for `rqt_image_view`, RViz2, and debugging live bags.

**Related terms:** visualization, detection, HUD, evaluation.

### ROS bag

**Definition:** A recorded collection of ROS 2 messages that can be replayed or analyzed later.

**In this project:** M5 bags preserve live RGB/depth and detector behaviour so the pipeline can be measured without repeating the physical camera session.

**Related terms:** frame, evaluation, replay, reproducibility.

---

## 6. Depth, calibration, and geometry filtering

### Depth image

**Definition:** An image whose pixels represent depth under a declared convention. ROS canonical depth measures distance along the camera optical Z axis, not Euclidean distance along an off-axis viewing ray.

**In this project:** The node expects `/depth_cam/depth/image_raw` to supply unsigned 16-bit millimetres, with zero invalid. RGB registration is a required assumption, not established by matching image dimensions or the topic name.

**Related terms:** RGB-depth registration, depth unit, camera intrinsics, geometry filter.

### RGB-depth registration

**Definition:** Aligning depth pixels with RGB pixels so that a location in the colour image refers to the corresponding location in the depth image.

**In this project:** The geometry filter uses depth values inside an RGB detection box, so the depth stream must be registered to the RGB camera view.

**Related terms:** depth image, camera calibration, bounding box, synchronization.

### Camera calibration

**Definition:** The process of estimating camera properties needed to interpret image measurements geometrically.

**In this project:** Calibration information is delivered through `sensor_msgs/CameraInfo` and is used by the geometry stage when available.

**Related terms:** camera intrinsics, focal length, principal point, depth.

### Camera intrinsics

**Definition:** Internal camera parameters describing how 3D rays project into the image. Common values include focal lengths and the principal point.

**In this project:** The node uses `fx`, `fy`, `cx`, and `cy` from camera information or configured fallback values.

**Related terms:** calibration, focal length, principal point, projection.

### Focal length (`fx`, `fy`)

**Definition:** The horizontal and vertical scale factors in a camera's intrinsic calibration. They describe how strongly 3D position changes appear in image pixels.

**In this project:** The geometry filter reads `fx` and `fy` from the RGB camera information when available.

**Related terms:** camera intrinsics, calibration, principal point.

### Principal point (`cx`, `cy`)

**Definition:** The image location at which the camera's optical axis intersects the image plane, represented by horizontal and vertical coordinates.

**In this project:** The geometry filter reads `cx` and `cy` from the RGB camera information when available.

**Related terms:** camera intrinsics, calibration, focal length.

### Depth unit

**Definition:** The physical unit represented by one depth-pixel value.

**In this project:** The M4c1 filter assumes the depth image stores unsigned 16-bit values in millimetres. A wrong unit would make geometric thresholds meaningless.

**Related terms:** depth image, millimetre, geometry filter.

### Floor reference

**Definition:** An estimate of the background or supporting surface against which an object's height can be compared.

**In this project:** The filter estimates a local depth around a candidate box. Its current greater-than comparison selects farther points under optical Z depth. Neither this comparison nor reversing it alone establishes physical height above an oblique floor.

**Related terms:** annulus, raised fraction, geometry filter.

### Annulus

**Definition:** A ring-shaped region surrounding another region.

**In this project:** A rectangular ring around the detection box provides a local floor-depth reference for the raised-object test.

**Related terms:** floor reference, bounding box, depth image.

### Geometry filter

**Definition:** A rule-based check that uses geometric measurements to accept or reject a model candidate.

**In this project:** The M4c1 filter applies depth-based acceptance rules after YOLO proposes candidates. Rejecting flat distractors is the intent, not validated behavior: registration and the current depth-selection sign need verification. The filter cannot create a missing candidate.

**Related terms:** depth image, KEEP, REJECT, raised fraction, aspect ratio.

### Raised fraction

**Definition:** A project-named fraction intended to indicate a raised surface. Its physical meaning depends on how points are selected and how the supporting surface is represented.

**In this project:** The current selection uses depth greater than floor depth plus a margin. For optical Z depth this selects farther points. Calling that subset raised does not validate the intended interpretation or prove rejection of flat distractors.

**Related terms:** depth image, floor reference, geometry filter.

### Planar top

**Definition:** A relatively flat upper surface of a raised object.

**In this project:** The filter checks depth variation in the selected subset. Small variation in Z is not a general planarity test: a tilted flat plane can have substantial Z variation. A geometric plane fit would answer a different question.

**Related terms:** standard deviation, geometry filter, depth image.

### Standard deviation

**Definition:** A statistical measure of how much values vary around their average.

**In this project:** `filter_max_planar_top_stddev_mm` limits depth variation on the candidate's raised top region. Large variation can indicate that the region is not a flat cube top.

**Related terms:** planar top, depth image, geometry filter.

### KEEP / REJECT

**Definition:** The two possible decisions of the project's geometry stage.

**In this project:** A YOLO candidate must first exist, then pass confidence and NMS, and finally receive a geometry decision. Only `KEEP` detections are published by the current node.

**Related terms:** detection candidate, confidence threshold, geometry filter, false negative.

---

## 7. Evaluation and measurement

### Evaluation

**Definition:** Measuring how well a model or complete system performs against a defined protocol.

**In this project:** Evaluation must state the dataset or bag, confidence threshold, classes, distance, camera conditions, and whether the measurement covers the model alone or the complete ROS pipeline.

**Related terms:** benchmark, ground truth, precision, recall, domain gap.

### Precision

**Definition:** Among the predictions made by a system, the proportion that are correct.

**In this project:** Low precision means the detector publishes too many false cube detections, such as coloured background objects.

**Related terms:** false positive, recall, mAP.

### Recall

**Definition:** Among the real target objects, the proportion that the system successfully detects.

**In this project:** Low recall means the detector misses real cubes, which is the main type of failure observed in the current M5 live scene.

**Related terms:** false negative, precision, mAP.

### Mean Average Precision (mAP)

**Definition:** A common object-detection metric that summarizes precision-recall performance across confidence thresholds and classes, while accounting for box overlap requirements.

**In this project:** The M2 report includes mAP at IoU 0.5 and across IoU thresholds from 0.5 to 0.95. The small validation set means those numbers must be interpreted with their dataset size and context.

**Related terms:** precision, recall, IoU, evaluation.

### mAP@0.5

**Definition:** Mean Average Precision using an IoU threshold of 0.5 for deciding whether a predicted box sufficiently overlaps a reference box.

**In this project:** `models/README.md` reports the M2 validation mAP@0.5. It is useful evidence, but it does not by itself prove live JetRover performance.

**Related terms:** mAP, IoU, validation set, domain gap.

### Frame-hit rate

**Definition:** The proportion of evaluation frames in which a required target is detected according to the defined hit rule.

**In this project:** M4/M5 reports use frame-hit measurements to describe how consistently cube detections survive the pipeline across recorded frames.

**Related terms:** recall, evaluation, frame, bag.

### Detection accuracy

**Definition:** A general phrase for how often a detector produces correct results. It is incomplete unless the measurement definition is stated.

**In this project:** A meaningful result should distinguish class correctness, box overlap, false positives, false negatives, frame-hit rate, and whether the geometry filter is enabled.

**Related terms:** precision, recall, IoU, frame-hit rate, evaluation.

### Hard negative

**Definition:** A negative example that looks similar to a target and is therefore especially useful for exposing false positives.

**In this project:** Coloured bags, cardboard, decals, and similar objects were used as hard-negative evidence for the detector and geometry filter.

**Related terms:** false positive, dataset, fine-tuning, domain gap.

### Reproducibility

**Definition:** The ability to repeat a measurement or experiment under documented conditions and obtain comparable results.

**In this project:** Model path, confidence threshold, bag, image size, hardware, runtime, and filter parameters should be recorded with evaluation results.

**Related terms:** benchmark, evaluation, ROS bag, configuration.

---

## Official and project references

### Project references

- [`docs/learn/LESSON-PLAN.md`](../LESSON-PLAN.md) — curriculum scope and project-specific teaching facts.
- [`docs/learn/lessons/0001-what-yolo-outputs.html`](../lessons/0001-what-yolo-outputs.html) — Lesson 0001, the first detailed application of this glossary.
- [`recognition_of_different_colored_cubes/cube_detection_node.py`](../../../recognition_of_different_colored_cubes/cube_detection_node.py) — current runtime implementation.
- [`models/README.md`](../../../models/README.md) — model artifacts, class mapping, export metadata, and evaluation context.
- [`docs/architecture.md`](../../architecture.md) — current ROS 2 and inference architecture.
- [`docs/evaluation.md`](../../evaluation.md) — structured evaluation protocol.

### Authoritative external references

- [Ultralytics YOLOv5 inference documentation](https://docs.ultralytics.com/yolov5/tutorials/pytorch_hub_model_loading) — example detection fields, confidence settings, and inference usage.
- [Ultralytics model export documentation](https://docs.ultralytics.com/yolov5/tutorials/model_export) — PyTorch, ONNX, TensorRT, and other export formats.
- [ONNX introduction](https://onnx.ai/onnx/intro/) — graphs, operators, and the model-exchange format.
- [NVIDIA TensorRT Developer Guide](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html) — TensorRT engines, optimization, and deployment concepts.
- [ROS 2 Humble topics](https://docs.ros.org/en/humble/Concepts/Basic/About-Topics.html) — typed publish/subscribe communication and continuous data streams.
- [ROS 2 Humble `vision_msgs`](https://docs.ros.org/en/humble/p/vision_msgs/) — standard detection message types.
- [ROS 2 Humble `cv_bridge`](https://docs.ros.org/en/humble/p/cv_bridge/) — ROS image and OpenCV conversion.
- [PyTorch beginner tutorials](https://pytorch.org/tutorials/beginner/basics/intro.html) — introductory model and training concepts.

## Change log

| Date | Change |
|---|---|
| 2026-09-01 | Created the living glossary for general computer vision, machine learning, object detection, deployment, ROS 2, depth geometry, and evaluation terms. |
