# Initial training data prepared — 9 September 2026

All 26 selected images have explicit human confirmation from Maher. This is a compact initial experiment using his own captures, not the external cube dataset.

| Split | Images | Red cubes | Green cubes | Blue cubes | Empty backgrounds |
|---|---:|---:|---:|---:|---:|
| Training | 22 | 14 | 14 | 14 | 2 |
| Validation | 4 | 4 | 4 | 4 | 0 |

The two reviewed frames from each setup remain together. Validation contains the full selected `dist40cm` and `spread_out` groups; all other frames from those groups must stay excluded from training as well. These groups test a held-out scale condition and a spread-out arrangement while retaining all three colors. Selection preceded new-model training/results. No final test split is created or aliased to validation.

Four frames represent only two arrangements in the same room and capture session. This is a limited development signal, not a reliable estimate of broader accuracy. There are no background-only validation examples, so background-only false-positive performance cannot be estimated here. One error changes a color's recall by 25 percentage points. Do not use these results to declare the 80-percent final project target achieved.

## Files

- Human approvals: `human_review.json`.
- Reproducible split and per-image annotations/hashes: `development_split.json`.
- Export configuration: `evaluation/results/robot_training_2026-09-09/data.yaml` from the project root.
- Exported image and label folders are beneath that same directory.
- Exporter: `scripts/prepare_reviewed_robot_dataset.py`. It refuses to overwrite an existing export.

Each YOLO label line contains a color class ID and four normalized box values: horizontal center, vertical center, width, height. Positions and widths are divided by image width; vertical values by image height. Classes are 0 blue, 1 green, 2 red. Empty-background label files contain no lines. Image copies are unchanged photographs, without annotation overlays.

## Verification and next action

Verified all image hashes, human confirmation coverage, exact-copy equality, complete image/label pairs, class IDs, valid box bounds, normalized-coordinate round trips, and no group/exact-hash overlap between splits. Original images and existing approvals were unchanged.

Next: verify a compatible general pretrained checkpoint and training/runtime export contract before a training smoke run. No training or deployment has occurred. The locally present unrelated checkpoint must not be silently substituted for the intended model architecture.
