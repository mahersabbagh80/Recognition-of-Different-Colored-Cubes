# Training and validation workflow

**Updated:** 13 September 2026. This records the completed experiment with 23 training images and eight development-validation images, its ONNX/TensorRT export, and the live ROS smoke checks. The geometry filter, a repeatable reliability study, and an independent final test remain unfinished.

**Local artifacts:** Links into `../runs/` point to generated files in this checkout. The `runs/` directory is Git-ignored, so those run artifacts are not included in the tracked documentation.

## Data and split used

The reviewed dataset contains 31 images with human-confirmed annotations. The two roles use separate photographed arrangements:

| Role | Images | Contents | Use |
|---|---:|---|---|
| Training | 23 | 13 retained first-frame images from the earlier approved set, plus new captures T01–T10; 39 cube boxes (13 per color) and three negative/background images | Update model weights |
| Development validation | 8 | New, held-out arrangements V01–V08; V01–V06 each show all three colors, V07 is empty, and V08 contains a bottle; 18 cube boxes (six per color) | Compare predictions and select the checkpoint |

The manifest records disjoint image and setup groups. All eight validation images were captured in the same room and session, so they test held-out arrangements under similar conditions; they do not represent a separate-session or independent final test. The class mapping is `0=blue_cube`, `1=green_cube`, `2=red_cube`.

Evidence: the [dataset configuration](../evaluation/results/robot_training_2026-09-12/data.yaml), [31-image split manifest](../evaluation/robot_dataset_2026-09-12/development_split.json), [confirmed annotations](../evaluation/robot_dataset_2026-09-12/human_review.json), and [record of the retained earlier frames](../evaluation/robot_dataset_2026-09-09/first-frame-selection-2026-09-12.md).

## Fine-tuning run

The run started from the general pretrained [YOLOv5u-small checkpoint](../models/pretrained/yolov5su.pt). Fine-tuning updates those existing weights using the project images; it is not general pretraining from scratch. Maher launched the checked script manually:

```bash
.venv-m2/bin/python scripts/run_robot_training_experiment.py
```

The [run summary](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/summary.json) records all 60 configured epochs. The best checkpoint was selected at epoch 45 by validation fitness (`mAP50-95`); `last.pt` preserves epoch 60. Key settings were 640-pixel input, batch size 4, AdamW, initial learning rate 0.001, seed 42, and patience 15. The exact requested settings and library arguments are saved in [requested_settings.json](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/requested_settings.json) and [args.yaml](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/args.yaml). The [training log](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/terminal_output.txt) and [epoch results](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/results.csv) preserve the run details.

The selected [best.pt](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/weights/best.pt) was exported in the next step. The automated validation metrics and their limitations are summarized in [Evaluation](evaluation.md).

## Export and live integration

The selected checkpoint was exported on the desktop to static-batch ONNX at 640×640, opset 13, without graph simplification or dynamic dimensions. The exported graph passed the ONNX checker and has input shape `[1, 3, 640, 640]` and output shape `[1, 7, 8400]`. The [verified ONNX file](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/weights/best.onnx) was copied to the JetRover with its SHA-256 checked. TensorRT 8.6.2 built a separate FP16 engine at `/home/ubuntu/maher_ws/best_2026-09-12.engine`; the previous engine was left in place.

The dated engine was loaded by the ROS detection node for smoke checks at confidence 0.25. With `filter_enabled=false`, live views showed one red cube detection, then one correct detection for each of blue, green, and red, and no detection in one empty-room view. These are successful smoke observations, not a measured reliability rate. A TensorRT smoke run on validation image V03 found blue and green but missed red, matching the PyTorch validation result.

With `filter_enabled=true`, a live scene containing all three cubes and a carton produced no kept detections. The node continued to produce candidates, but every rejection accumulated in the `flat` geometry bucket: 2,400 rejections over 600 frames. The underlying filter cause has not been isolated. This result leaves the full filtered detection and depth-localization path unfinished; it must not be hidden by changing a threshold without diagnosing the measurements.

The live observations and deployment checks are recorded in the [Sunday walkthrough](development-learning-journal/2026-09-13-sunday.md), including the [saved red-cube frame](assets/live-test-2026-09-13/red-single-filter-off.png), the [three-color observation](development-learning-journal/2026-09-13-sunday.md#three-color-live-frame-reviewed), the [empty-scene check](development-learning-journal/2026-09-13-sunday.md#empty-live-scene-checked), and the [filter failure](development-learning-journal/2026-09-13-sunday.md#geometry-filter-rejects-the-live-cube-scene).

## Remaining work

1. Capture synchronized RGB and depth data for the live cube scene and record each candidate's geometry values. Diagnose the flat-surface rejection, depth alignment, and box-to-depth sampling assumptions before changing the filter.
2. Correct and verify the filter on cube and non-cube scenes. Confirm that detections and depth-based locations reach the ROS outputs.
3. Measure live reliability with a defined set of varied scenes and recorded ground truth. Repeated frames of one unchanged camera view are not independent scene trials.
4. After model or threshold choices are finished, run a later untouched test from new scenes or a separate session. The current same-room validation set and live debugging observations have already served development and integration checks.

No system-level pass/fail threshold or acceptance decision is established by this workflow. It reports completed work and the next evidence needed.

## Reading the evaluation terms

- **True positive (TP):** a prediction matched to a real cube with the correct color and sufficient box overlap.
- **False positive (FP):** an unmatched cube prediction.
- **False negative (FN):** a real cube without a qualifying prediction.
- **Precision = TP / (TP + FP):** the share of reported detections that are correct.
- **Recall = TP / (TP + FN):** the share of real cubes that are detected.

Always include the data split, model, test conditions, and measurement method with these values. A validation score, a visual count from saved predictions, and a live smoke test answer different questions.

## Evidence index

- [Run summary](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/summary.json), [plots](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/results.png), and [confusion matrix](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/confusion_matrix.png)
- [Approved and predicted validation mosaics](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/val_batch0_labels.jpg) and [predictions](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/val_batch0_pred.jpg)
- [Image-by-image validation review](validation-prediction-review-2026-09-13.md)
- [Saturday walkthrough](development-learning-journal/2026-09-12-saturday.md) and [Sunday walkthrough](development-learning-journal/2026-09-13-sunday.md)
