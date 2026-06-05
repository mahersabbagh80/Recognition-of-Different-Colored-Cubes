# Technical Stack

## On-Robot Runtime (Jetson Orin Nano)

| Component | Version / Notes |
|-----------|----------------|
| OS | Ubuntu 22.04 LTS |
| SDK | NVIDIA JetPack |
| ROS 2 | Humble |
| Python | 3.10 |
| OpenCV | Image processing, debug overlay drawing |
| cv_bridge | ROS `sensor_msgs/Image` ↔ OpenCV conversion |
| vision_msgs | `Detection2DArray` output format |
| TensorRT | FP16 inference engine (primary inference backend) |

### Model Export Chain

```
PyTorch (YOLOv5s weights)
    → ONNX (intermediate format)
    → TensorRT FP16 engine (Jetson GPU)
```

Verify PyTorch, ONNX, and TensorRT versions on the Jetson **before training** to avoid conversion failures.

### Fallback

If TensorRT conversion fails: ONNX Runtime inference (no GPU acceleration, slower but functional).

---

## Off-Robot Training (Google Colab)

| Component | Role |
|-----------|------|
| Google Colab | Cloud GPU for training |
| PyTorch | Training framework |
| YOLOv5 (Ultralytics) | Object detection model (YOLOv5s) |
| ONNX | Export intermediate format |
| Roboflow | Dataset annotation and YOLOv5-format export |

**Starting dataset:** https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1

Supplement with images captured from the robot's own Orbbec camera for better generalization.

**Training notebook:** [`training/train.ipynb`](../training/train.ipynb) (Milestone 3)

---

## Visualization

| Tool | Use |
|------|-----|
| RViz2 | View detection overlays and debug image |
| rqt_image_view | Quick live camera / debug image inspection |

---

## Development Tools

| Tool | Use |
|------|-----|
| Git / GitHub | Version control and portfolio |
| VS Code / Cursor | Editing and debugging |
| colcon | ROS 2 workspace build |
| rosdep | Install declared ROS dependencies |

---

## ROS 2 Package Dependencies

Declared in `package.xml` (installed via `rosdep`):

- `rclpy`
- `sensor_msgs`
- `vision_msgs`
- `cv_bridge`
- `std_msgs`

Not in `package.xml` (system / pip, managed manually on Jetson):

- OpenCV (`python3-opencv` or pip)
- PyTorch (Jetson-specific wheel)
- ONNX / ONNX Runtime
- TensorRT (ships with JetPack)
- YOLOv5 (cloned or pip-installed for export scripts)

---

## Model Artifacts

Stored in `models/` (gitignored):

| File | Description |
|------|-------------|
| `best.pt` | PyTorch weights from Colab training |
| `best.onnx` | ONNX export |
| `best.engine` | TensorRT FP16 engine |
