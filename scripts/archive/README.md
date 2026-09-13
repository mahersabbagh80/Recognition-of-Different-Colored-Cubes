# Historical scripts archive

These scripts are retained for project history and to make earlier experiments
inspectable. They are not part of the active September workflow in
[`../README.md`](../README.md), and should not be treated as the current
training or evaluation entry points.

## Roboflow and hard-negative experiment

These scripts supported the earlier Roboflow export and M3c hard-negative
fine-tuning workflow:

| Script | Historical role |
|---|---|
| [`roboflow/_download_weights.py`](roboflow/_download_weights.py) | Download Roboflow artifacts and place the checkpoint under `models/`. |
| [`roboflow/normalize_dataset.py`](roboflow/normalize_dataset.py) | Convert the mixed Roboflow export into YOLOv5 detection labels. |
| [`roboflow/build_hardneg_dataset.py`](roboflow/build_hardneg_dataset.py) | Combine the old Roboflow and JetRover-room examples into the M3c dataset. |
| [`roboflow/finetune_hardneg.py`](roboflow/finetune_hardneg.py) | Fine-tune the earlier checkpoint on that hard-negative dataset. |
| [`roboflow/validate_hardneg.py`](roboflow/validate_hardneg.py) | Produce the earlier before/after predictions and summary. |

The scripts that derive paths from their location still resolve project data
and model defaults against the repository root. Their inputs, dependencies,
and reported results belong to those earlier experiments.

## M4c1 distractor-analysis helpers

These were one-shot debug tools and are not part of a routine pipeline:

| Script | Historical role |
|---|---|
| [`dev_helpers/_cleanup_inspect.py`](dev_helpers/_cleanup_inspect.py) | Remove the old `_*` inspection files from `data/hardneg`. |
| [`dev_helpers/_inspect_tall_cyl_schema.py`](dev_helpers/_inspect_tall_cyl_schema.py) | Print the JSON schema of the M4c1 tall-cylinder outputs. |
| [`dev_helpers/_peek_bboxes_once.py`](dev_helpers/_peek_bboxes_once.py) | Capture one live RGB frame with a bounding-box overlay and JSON output. |
| [`dev_helpers/_summarize_carton.py`](dev_helpers/_summarize_carton.py) | Summarize the carton YOLO and geometry-filter results. |
| [`dev_helpers/_summarize_cup.py`](dev_helpers/_summarize_cup.py) | Summarize the cup YOLO and geometry-filter results. |
| [`dev_helpers/_summarize_tall_cyl.py`](dev_helpers/_summarize_tall_cyl.py) | Summarize the tall-cylinder YOLO and geometry-filter results. |

Some helpers contain machine-specific paths or require the original ROS and
model environment. Review their inputs before attempting to run them.
