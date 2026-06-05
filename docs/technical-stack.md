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

Verify PyTorch, ONNX, and TensorRT versions on the Jetson **before export/conversion** to avoid failures.

### Fallback

If TensorRT conversion fails: ONNX Runtime inference (no GPU acceleration, slower but functional).

---

## Model Weights (default: pretrained)

| Step | Where | Action |
|------|-------|--------|
| 1 | Roboflow Universe | Download pretrained `best.pt` from the [RGB cube detection project](https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1) |
| 2 | Dev PC or Jetson | Export `best.pt` → `best.onnx` (script or Colab) |
| 3 | Jetson | Convert `best.onnx` → TensorRT `.engine` |

No Colab session required if pretrained weights meet accuracy on the robot camera.

## Off-Robot Fine-Tuning (optional — Google Colab)

Use only if standalone inference on robot camera images is below target accuracy.

| Component | Role |
|-----------|------|
| Google Colab | Cloud GPU for fine-tuning |
| PyTorch | Training framework |
| YOLOv5 (Ultralytics) | Object detection model (YOLOv5s) |
| ONNX | Export intermediate format |
| Roboflow | Pretrained weights and YOLOv5-format dataset |

**Fine-tune recipe:** Roboflow dataset, 20–30 epochs. Add robot camera images only if accuracy is still below 80% after fine-tuning.

**Training notebook:** [`training/train.ipynb`](../training/train.ipynb) (optional fallback)

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
| `best.pt` | PyTorch weights (Roboflow pretrained, or fine-tuned) |
| `best.onnx` | ONNX export |
| `best.engine` | TensorRT FP16 engine |
