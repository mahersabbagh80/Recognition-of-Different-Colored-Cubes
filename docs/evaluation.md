# Evaluation

**Status, 13 September 2026:** the new checkpoint has completed development validation and limited live integration checks. The planned full-range 50-frame evaluation, a repeatability study, an independent final test, and verification of depth-based locations have not been performed. No system-level acceptance decision is recorded here.

**Local artifacts:** Links into `../runs/` point to generated files in this checkout. The `runs/` directory is Git-ignored, so those run artifacts are not included in the tracked documentation.

## Development validation

The selected checkpoint was evaluated on eight human-reviewed, held-out arrangements from the same room and capture session. The set contains 18 cubes: six blue, six green, and six red. V01–V06 each show all three colors; V07 is empty; V08 contains an ordinary bottle. The training and validation filenames and arrangement groups are separate, but the validation set is small and does not cover a new session or changed room conditions.

Ultralytics' saved report for `best.pt` gives these results:

| Class | Labeled cube instances | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| All | 18 | 0.982 | 0.964 | 0.995 | 0.707 |
| Blue cube | 6 | 0.957 | 1.000 | 0.995 | 0.788 |
| Green cube | 6 | 0.989 | 1.000 | 0.995 | 0.609 |
| Red cube | 6 | 1.000 | 0.892 | 0.995 | 0.723 |

The run selected epoch 45 by validation fitness, which is mAP50-95. These are development-validation metrics for this split; they do not measure live reliability or establish final acceptance.

### Human review of the saved predictions

The image-by-image review of the saved validation mosaic found 17 visible correct matches among the 18 labeled cubes. V03 contains the one miss: its red cube is not predicted, while the blue and green cubes are detected. V01, V02, V04, V05, and V06 each show all three expected detections. The empty V07 and bottle-only V08 show no cube detections. No extra detection was visible in the reviewed tiles. The confusion matrix shows six matched blue cubes, six green, five red, and one missed red cube.

The **17/18** count is a human inspection of the fixed boxes displayed in the saved prediction mosaic. Precision, recall, and mAP are the automated validation report. These are different views of the run and should be reported with their methods instead of treating them as interchangeable.

## Live integration observations

The dated TensorRT FP16 engine was loaded in the JetRover ROS node with confidence threshold 0.25. These were short integration checks, not a sampled reliability test:

| Live condition | Observation | Evidence limit |
|---|---|---|
| V03 TensorRT smoke inference | Blue (0.761) and green (0.719) were reported; red was missed, matching the PyTorch validation result. | One saved validation image. |
| Geometry filter disabled | One red cube was shown at confidence 0.78. In a separate three-cube view, blue (about 0.85), green (about 0.86), and red (about 0.74) were all shown; an empty-room view showed `keep=0`. | A few manually observed scenes; no repeated-trial rate. |
| Geometry filter enabled | With all three cubes and a carton visible, `keep=0`. The detector continued to produce candidates, but every rejection accumulated in the `flat` bucket: 2,400 over 600 frames. | The downstream filter is blocking candidates; the exact cause has not been isolated. |

The ROS node reported median total processing of about 57.7–59.1 ms and median TensorRT inference of about 25.9 ms in sampled 100-frame windows. These are internal node timings, not camera-to-output latency or a formal end-to-end frame-rate measurement. Because the filter-enabled check removed all candidates, reliable depth-based locations have not been demonstrated.

The [Sunday walkthrough](development-learning-journal/2026-09-13-sunday.md) records the deployment and live-test conditions. A [saved red-cube frame](assets/live-test-2026-09-13/red-single-filter-off.png) is available. The multi-cube, empty-scene, and filter-on observations are documented there; they were not saved as separate screenshots in this workspace.

## Planned full-range protocol — not performed

The existing plan is to place one cube of each color in view, test at 20 cm, 40 cm, 60 cm, and 80 cm, capture 50 frames per test run, and manually record ground truth for every frame. No such structured 50-frame runs or per-distance results have been recorded. [`evaluation/evaluate.py`](../evaluation/evaluate.py) is currently a stub (`main(): pass`); it cannot capture or label frames, so evaluator implementation and verification are still required before this protocol can run. Minimum and maximum reliable range, repeated-scene reliability, and formal end-to-end frame rate therefore remain unmeasured.

This protocol describes work still to do; it does not set an acceptance threshold. No pass/fail criteria are supplied by the current evidence.

## Independent test and next evidence

The eight-image set is development validation, and the live observations were used as integration diagnostics. Neither is an untouched final test. After diagnosing and correcting the geometry filter and completing any model or threshold choices, evaluate a later set of new scenes without using it to tune the system. Record the model and engine hashes, confidence and filter settings, scene conditions, expected cubes and locations, detections, misses, false detections, and the per-frame ground truth. Keep detection quality separate from depth and location quality.

## Evidence

- [Run summary](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/summary.json), [complete terminal report](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/terminal_output.txt), and [epoch metrics](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/results.csv)
- [Confusion matrix](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/confusion_matrix.png), [approved annotations](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/val_batch0_labels.jpg), and [saved predictions](../runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/val_batch0_pred.jpg)
- [V03 approved annotation](assets/validation-review-2026-09-13/v03-approved.jpg) and [V03 prediction](assets/validation-review-2026-09-13/v03-prediction.jpg)
- [Image-by-image validation review](validation-prediction-review-2026-09-13.md)
- [Held-out split manifest](../evaluation/robot_dataset_2026-09-12/development_split.json) and [dataset configuration](../evaluation/results/robot_training_2026-09-12/data.yaml)
- [Saturday journal](development-learning-journal/2026-09-12-saturday.md) and [Sunday journal](development-learning-journal/2026-09-13-sunday.md)
