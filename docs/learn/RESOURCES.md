# Resources: Computer vision for the colored-cube detector

Curated for the mission (own the M3–M5 decisions on the JetRover project + explain it in interviews). Every entry was chosen because it directly serves a lesson in this workspace.

## Knowledge

### Object detection foundations

- [Ultralytics — YOLOv5 documentation](https://docs.ultralytics.com/yolov5/)
  The actual library used in the project. Use for: what `model.predict()` returns, what the input/output shapes are, how Ultralytics handles NMS. **High-trust** because it's the library we'll be calling.

- [Ultralytics — YOLOv5 architecture explainer (glenn-jocher, 2020)](https://github.com/ultralytics/yolov5/issues/6998)
  Thread where the YOLOv5 maintainer explains the model head and output decoding. Use for: how a YOLOv5 output tensor (1, 25200, 85) is interpreted and decoded into boxes.

- [Joseph Redmon et al. — You Only Look Once: Unified, Real-Time Object Detection (CVPR 2016)](https://arxiv.org/abs/1506.02640)
  The original YOLO paper. Skim, don't read end-to-end. Use for: the "one forward pass = predictions for the whole image" idea and why it changes latency math vs. Faster R-CNN.

### ONNX as an intermediate representation

- [ONNX homepage](https://onnx.ai/)
  What ONNX is, the operator set idea, the runtime ecosystem. Use for: terminology (op-set, graph, node) that the M3 script will use.

- [Ultralytics — Export to ONNX](https://docs.ultralytics.com/modes/export/)
  The exact path the M3 step uses. Read alongside the project's `scripts/export_onnx.py`.

### TensorRT and the deployment chain

- [NVIDIA TensorRT Developer Guide](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html)
  The primary source. Use for: what `trtexec` does, what FP16/INT8 actually change, what calibration is, why engine files are hardware-specific.

- [NVIDIA — TensorRT ONNX parser](https://docs.nvidia.com/deeplearning/tensorrt/onnx-parser-support-guide/index.html)
  Which ONNX ops TensorRT can consume directly and which fall back to plugins. This is the version-compatibility risk mentioned in `docs/technical-stack.md`.

- [NVIDIA Jetson AI Lab — YOLOv5 + TensorRT on Jetson Orin](https://www.jetson-ai-lab.com/archived/lab-tutorials-2022/yolov5-trt.html)
  Hands-on walkthrough. Older (2022) but the export recipe is the same one the project's M4 step uses.

### ROS 2 perception wiring

- [ros2 vision_msgs / Detection2DArray](https://docs.ros.org/en/humble/p/vision_msgs/)
  Message contract for the standard output topic. Use for: understanding `cube_detection_node.to_detection_array_msg()`.

- [cv_bridge tutorial (ROS 2 Humble)](https://docs.ros.org/en/humble/p/cv_bridge/)
  How `sensor_msgs/Image` ↔ OpenCV conversion works. Use for: the `imgmsg_to_cv2` / `cv2_to_imgmsg` calls in the node.

- [ROS 2 QoS policies](https://docs.ros.org/en/humble/Concepts/About-Quality-of-Service-Settings.html)
  The QoS choices in the node (sensor-data profile for the camera, default for outputs). Use for: why a topic with a default subscriber and a BEST_EFFORT publisher silently fails.

## Wisdom (Communities)

- [r/computervision](https://reddit.com/r/computervision)
  High-signal for "is this an architectural mistake" type questions, especially around deployment on edge devices.

- [r/ROS](https://reddit.com/r/ROS)
  For integration questions specific to the ROS 2 side of the project.

- [NVIDIA Jetson developer forums](https://forums.developer.nvidia.com/c/agx-autonomous-machines/jetson-embedded-systems/)
  For TensorRT version mismatches, JetPack incompatibilities, and the kind of error you'll see when `trtexec` rejects an ONNX op.

- [Ultralytics GitHub Discussions](https://github.com/ultralytics/ultralytics/discussions)
  For the export chain specifically — many questions about FP16 vs INT8 vs TF32 land here.

## Gaps

- **No single great explainer of YOLOv5 postprocessing** (decoding the raw output tensor, applying NMS) that targets an engineering audience. Most blog posts are either too math-heavy (papers) or too shallow (tutorials that just call `model(...)`). May need to write the reference doc in `reference/` ourselves.
- **TensorRT + Jetson Orin Nano specifically** is well-documented in fragments but not as one coherent guide. The Jetson AI Lab tutorial above is the closest, but dated.
- **Community for HiWonder/JetRover-specific Q&A** doesn't exist (vendor is closed-source). Use the general Jetson + ROS 2 communities instead.
