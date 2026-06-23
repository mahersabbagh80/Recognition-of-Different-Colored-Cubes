**Name:** YOLOv5 object detection with TensorRT (Machine Learning)

**Idea:** A YOLOv5 neural network recognises red, green, and blue cubes as complete objects. Camera frames come from the HiWonder vendor camera stack (`peripherals/depth_camera.launch.py` -> `/depth_cam/rgb/image_raw`) and pass through the model, accelerated with TensorRT on the Jetson. The model outputs detected cubes with locations, colors, and confidence scores in a single step; results are published as standard ROS 2 vision messages plus a vendor-compatible `interfaces/ObjectsInfo` topic. Shape and color are learned from training data rather than explicit rules.

---

## Why YOLO — Model Selection Rationale

Object detection is a well-studied problem with several established model families. The choice of architecture is a technical decision that should be justified against the specific constraints of the deployment environment. This section compares the main candidates against the requirements of this project.

### The core architectural distinction

Object detection models split into two families based on how they process an image.

**Two-stage detectors** (e.g. Faster R-CNN) run two sequential passes. The first pass — the Region Proposal Network — scans the image and proposes regions that might contain objects. The second pass classifies each proposed region. Two passes give higher accuracy but at a significant compute cost.

**One-stage detectors** (e.g. YOLO, SSD) run a single pass. The model looks at the entire image once and predicts bounding boxes and class labels simultaneously. One pass is faster and lighter at the cost of some accuracy on complex scenes.

### Candidate comparison

| Model | Architecture | Speed on edge | TensorRT support | Model size | Suited for this project |
|---|---|---|---|---|---|
| **YOLOv5s** | One-stage | High — designed for edge | Excellent — well-documented | ~7M parameters | Yes |
| **YOLOv8n** | One-stage | High | Good — improving with JetPack 6 | ~3M parameters | Yes — stronger alternative |
| **Faster R-CNN** | Two-stage | Low — RPN adds compute | Harder — two-stage pipeline complex to optimise | ~137M parameters (ResNet-50) | No — too heavy for Jetson |
| **SSD** | One-stage | High | Good | ~26M parameters | Possible — lower accuracy than YOLO |
| **MobileNet SSD** | One-stage | Very high | Good | ~6M parameters | Possible — lowest accuracy |
| **EfficientDet** | One-stage | Medium | Moderate | ~6–52M parameters | Possible — complex export path |
| **RT-DETR** | Transformer | Medium-Low | Emerging | ~32M parameters | No — too new, limited Jetson support |

### Why Faster R-CNN was ruled out

Faster R-CNN is the model most commonly brought up as a YOLO alternative, and it is worth addressing directly.

Faster R-CNN achieves higher accuracy than YOLO on complex detection benchmarks. However, accuracy is not the binding constraint for this project — speed and compute efficiency are.

The two-stage pipeline imposes a significant latency penalty. On a server GPU, Faster R-CNN typically runs at 5–17 fps. On a constrained edge device like the Jetson Orin Nano, inference would be slower still and would likely fall below the ≥5 fps project requirement. Additionally, the two-stage architecture is harder to optimise with TensorRT — the region proposal step and the classification step have different computational profiles that do not map as cleanly onto GPU kernels as a single-stage model.

Faster R-CNN is the right choice when accuracy is critical and real-time speed is not required — for example, high-stakes static image analysis, satellite imagery, or medical imaging. None of those conditions apply here.

### Why YOLO was selected

The project has three binding constraints: real-time inference (≥5 fps), edge hardware (Jetson Orin Nano), and a one-week timeline.

YOLO satisfies all three:

- **Speed:** single-stage architecture completes inference in one forward pass. YOLOv5s runs well above 5 fps on the Jetson with TensorRT.
- **Edge hardware:** designed for deployment on constrained devices. The small model variant (YOLOv5s, ~7M parameters) fits comfortably within the Jetson's memory.
- **TensorRT compatibility:** YOLOv5 has a well-documented, widely tested ONNX → TensorRT export path. The HiWonder JetRover vendor stack includes a YOLOv5/TensorRT reference node that subscribes to `/depth_cam/rgb/image_raw` and publishes `interfaces/ObjectsInfo`, reducing integration risk when used as a reference pattern.
- **Task fit:** this is a simple, constrained detection task — three classes, indoor environment, fixed distance range (20–80 cm), no dense or overlapping objects. The accuracy advantage of two-stage detectors is not needed here.

### Note on YOLOv8

YOLOv8 (Ultralytics) is a stronger model than YOLOv5 on accuracy benchmarks and has better ROS 2 integration packages available. It is a valid alternative. YOLOv5 was chosen over YOLOv8 because the Hiwonder JetRover vendor ships YOLOv5 with a pre-configured TensorRT export pipeline, which reduces setup risk under the one-week constraint. If this project is extended or repeated, YOLOv8 is the recommended upgrade.

---

## Model strategy (one-week timeline)

| Path | When | What |
|------|------|------|
| **Default** | Start here | Download pretrained `best.pt` from [Roboflow Universe](https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1) → ONNX → TensorRT → deploy |
| **Fallback** | Only if robot-camera accuracy fails | Fine-tune locally on dev PC (RTX 4070 Ti) — Roboflow dataset, 20–30 epochs; add robot images only if still below target |

Custom dataset collection and full 50–100 epoch training are **not** the default plan. TensorRT export on the Jetson is the main schedule risk — validate deployment before investing in training.

---

## Diagrams

- Inference pipeline: [`assets/concept2_inference_pipeline.png`](../assets/concept2_inference_pipeline.png)
- Training / export pipeline: [`assets/concept2_training_pipeline.png`](../assets/concept2_training_pipeline.png) (full path; fine-tune branch is optional)

---

## Steps

1. Obtain `best.pt` — download pretrained weights from Roboflow (fine-tune locally on dev PC only if step 6 fails).
2. Export to ONNX (`best.pt` → `best.onnx`), then convert to a TensorRT FP16 engine on the Jetson.
3. Test standalone inference on images from the robot camera.
4. Subscribe to the camera image topic and convert frames using cv_bridge.
5. Run each frame through YOLOv5 + TensorRT inference.
6. Filter detections to keep only cube classes above a confidence threshold.
7. Publish results as `vision_msgs/Detection2DArray`, vendor-compatible `interfaces/ObjectsInfo`, and a debug image on `/cube_detections/debug_image`.

---

## Pros

- Learns shape and color jointly; more robust to lighting, angle, and occlusion
- Pretrained path keeps the one-week timeline realistic while still using YOLOv5 + TensorRT
- Teaches edge deployment (ONNX, quantization, ROS 2 integration) — the highest portfolio value per hour
- Fine-tune option remains available if the Roboflow model does not generalise to the robot camera

## Cons

- Pretrained weights may not generalise perfectly to the JetRover Orbbec camera without fine-tuning
- TensorRT export is fragile due to version compatibility; the main technical risk
- Black box — failures may require fine-tuning and more data, not parameter tuning
- Less impressive training story if pretrained weights work out of the box (mitigate by documenting eval results and any fine-tune you did)