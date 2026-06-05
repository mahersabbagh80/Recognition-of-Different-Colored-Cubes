
**Name:** YOLOv5 object detection with TensorRT (Machine Learning)

**Idea:** A YOLOv5 neural network recognises red, green, and blue cubes as complete objects. Camera frames pass through the model, accelerated with TensorRT on the Jetson. The model outputs detected cubes with locations, colors, and confidence scores in a single step; results are published as standard ROS 2 vision messages. Shape and color are learned from training data rather than explicit rules.

**Model strategy (one-week timeline):**

| Path | When | What |
|------|------|------|
| **Default** | Start here | Download pretrained `best.pt` from [Roboflow Universe](https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1) → ONNX → TensorRT → deploy |
| **Fallback** | Only if robot-camera accuracy fails | Fine-tune locally on dev PC (RTX 4070 Ti) — Roboflow dataset, 20–30 epochs; add robot images only if still below target |

Custom dataset collection and full 50–100 epoch training are **not** the default plan. TensorRT export on the Jetson is the main schedule risk — validate deployment before investing in training.

**Diagrams:**
- Inference pipeline: [`assets/concept2_inference_pipeline.png`](../assets/concept2_inference_pipeline.png)
- Training / export pipeline: [`assets/concept2_training_pipeline.png`](../assets/concept2_training_pipeline.png) (full path; fine-tune branch is optional)

**Steps:**
1. Obtain `best.pt` — download pretrained weights from Roboflow (fine-tune locally on dev PC only if step 6 fails).
2. Export to ONNX (`best.pt` → `best.onnx`), then convert to a TensorRT FP16 engine on the Jetson.
3. Test standalone inference on images from the robot camera.
4. Subscribe to the camera image topic and convert frames using cv_bridge.
5. Run each frame through YOLOv5 + TensorRT inference.
6. Filter detections to keep only cube classes above a confidence threshold.
7. Publish results as `vision_msgs/Detection2DArray` and a debug image on `/cube_detections/debug_image`.

**Pros:**
- Learns shape and color jointly; more robust to lighting, angle, and occlusion
- Pretrained path keeps the one-week timeline realistic while still using YOLOv5 + TensorRT
- Teaches edge deployment (ONNX, quantization, ROS 2 integration) — the highest portfolio value per hour
- Fine-tune option remains available if the Roboflow model does not generalise to the robot camera

**Cons:**
- Pretrained weights may not generalise perfectly to the JetRover Orbbec camera without fine-tuning
- TensorRT export is fragile due to version compatibility; the main technical risk
- Black box — failures may require fine-tuning and more data, not parameter tuning
- Less impressive training story if pretrained weights work out of the box (mitigate by documenting eval results and any fine-tune you did)
