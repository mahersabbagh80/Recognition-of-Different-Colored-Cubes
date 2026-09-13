# Technical stack and artifact identity

Updated 13 September 2026 from the completed walkthrough and current checkout. These versions describe the recorded run, not a fresh remote inventory.

| Component | Recorded configuration |
|---|---|
| Robot hardware | NVIDIA Jetson Orin Nano on HiWonder JetRover |
| Robot middleware | Ubuntu 22.04 / ROS 2 Humble; Python 3.10 |
| TensorRT | 8.6.2; engine built on target Jetson |
| Desktop | NVIDIA RTX 4070 Ti; project .venv-m2 for training/export |
| Detector | General pretrained YOLOv5u-small, fine-tuned on reviewed camera data |
| Dataset | 23 training images / 8 validation images; classes 0 blue, 1 green, 2 red |
| Training | 60 epochs, batch 4, nominal batch 4, image size 640, AdamW, initial learning rate 0.001, patience 15, seed 42 |
| Selected checkpoint | Epoch 45 |
| Engine bindings | input images [1,3,640,640]; output output0 [1,7,8400] |
| Live diagnostic | Confidence 0.25; geometry filter off; explicit dated engine |

Exact environment and export flags are in the [Saturday](development-learning-journal/2026-09-12-saturday.md) and [Sunday](development-learning-journal/2026-09-13-sunday.md) records. JetPack's exact version is not established here.

## Artifact chain

Desktop run:
`runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/`

Selected `weights/best.pt` → exported `weights/best.onnx` → robot
`/home/ubuntu/maher_ws/best_2026-09-12.onnx` → robot
`/home/ubuntu/maher_ws/best_2026-09-12.engine`.

| Artifact | SHA-256 recorded at verification |
|---|---|
| ONNX | 21ecfbf89f91b7e0a47f1cb415d333ed3426d73fa7b3eca9542a0a51bfd0d589 |
| TensorRT engine | f385e0b56c8d4e517c04bae6ac34013c999d2a20367c59fcdbe3f6ace96fa0c0 |

Model binaries and raw runs are intentionally excluded from Git. Transfer them separately and verify fingerprints. The robot's old default engine was not replaced; a default launch is not sufficient to select the new model. See the [tested command](../README.md#quick-start).

## Software boundaries

- Vendor camera infrastructure owns RGB/depth capture. No vendor source changes are required.
- The project node uses cv_bridge, message_filters, NumPy, TensorRT/PyCUDA and ROS 2 publishers.
- [package.xml](../package.xml) already declares interfaces and the ROS dependencies. TensorRT/PyCUDA are installed in the Jetson environment.
- [detection.launch.py](../launch/detection.launch.py) starts the detector only; vendor-camera convenience launch is not present.
- Use setup.zsh in Zsh; setup.bash is for Bash.
- Browser preview uses the existing vendor-started web-video server. Desktop rqt discovery remains unresolved.

## Measurement limits

The synthetic engine benchmark is not live camera FPS. Recorded live-node median processing was about 58–59 ms, excluding a verified end-to-end camera-to-browser measurement. Geometry-filter failure and depth localization remain open; see [evaluation](evaluation.md).
