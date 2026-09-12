# Training and validation workflow

Agreed on 12 September 2026. This is a guide for the next run, not a record of completed training or deployment.

**Selection revision:** Maher subsequently chose one first frame per setup within the existing training folder: 11 kept and 11 excluded. Selection of the four validation-folder images is still pending. See the [keep/exclude record](../evaluation/robot_dataset_2026-09-09/first-frame-selection-2026-09-12.md). The all-26 configuration described below is superseded; the next configuration must reference only the selected images. The training/check/live-evaluation sequence remains applicable.

## Objective and working method

Fine-tune a general pretrained YOLO model on our own approved cube images, then run it live on the JetRover to detect and locate blue, green, and red cubes. Maher edits and runs the commands; Codex explains each step, checks the result with him, and documents completed work in the daily technical walkthrough. We pause between meaningful steps.

## Training workflow

1. **Inspect the current inputs.** Open the dataset configuration and identify its image folders and class mapping. Each photo is paired with a same-named text label containing the expected class and box coordinates. The existing experiment used 22 training images and four development-validation images.
2. **Prepare a separate configuration for all 26 approved images.** Include the former four validation photos in training. Preserve the original configuration, labels, and experiment results. These 26 images represent two frames from each of 13 setups; the remaining photos are not automatically included.
3. **Adapt the training script together.** Point it at the new configuration and check its data checks and result descriptions. Review the pretrained checkpoint, epochs, batch size, learning rate, augmentations, and output naming. The existing script still assumes the original split and must be adapted before this run.
4. **Decide how training stops and which checkpoint to use.** With no held-out photos, a score measured on reused training images cannot select a model on independent validation evidence. Agree explicitly on the stopping and checkpoint-selection rules before running; do not silently inherit the previous early-stopping interpretation.
5. **Launch training manually.** Maher runs the agreed command in the project environment. For each batch, the training library makes predictions, compares them with approved labels, computes an error and its gradients, and uses the optimizer to adjust weights. An epoch is one pass through the training set.
6. **Inspect the saved outputs.** Check the run folder, requested settings, logs, completed epoch count, saved checkpoints, and class mapping. A successful run shows that training executed; it does not establish live detection quality.

The starting point is a general pretrained checkpoint. Our further training is fine-tuning. We are not performing the original general pretraining ourselves.

## Validation and evaluation workflow

### A. Check whether the model learned its training examples

1. Load the new run's selected checkpoint explicitly.
2. Run predictions on the approved photos and inspect the boxes, colors, and confidence scores beside the annotations.
3. Use an explicit confidence cutoff and box-overlap matching rule. Count correct matches, extra predictions, and missed cubes.
4. Label these results **training-set checks** because the images were used for learning. Even excellent results here do not demonstrate performance on unseen scenes.

### B. Deploy and evaluate on fresh live scenes

1. Convert the selected checkpoint into the format required by the robot runtime. Verify the input/output structure and color-class mapping, then configure the live detector to load the new artifact.
2. Check that the live camera pipeline actually uses the new model. This verifies replacement-model integration; the earlier basic camera and robot setup need not be repeated without a reason.
3. Prepare manageable indoor scenes with changed cube positions and arrangements, each color represented, all three together, and an empty scene. Give precise placement instructions before each setup. No separate photo-collection session is required for the agreed training run.
4. Inspect the live predictions and reported locations. Compare boxes and colors against the visible cubes; check depth/location outputs separately from color detection.
5. Record conditions, model identity, thresholds, correct detections, false detections, and misses. Use a defined set of scenes or sampled frames; repeatedly counting nearly identical video frames would exaggerate the amount of evidence.
6. Review whether the model meets the intended demonstration needs. If it fails, identify whether the problem is detection, model conversion, runtime integration, or location/depth filtering before choosing a remedy.

Fresh live scenes provide evidence beyond the training photos. If we use those scenes to tune settings or retrain, they become development examples; a later untouched test is needed for an independent final assessment. Simply deploying the model is not itself validation.

## Reading the counts

- **True positive (TP):** a prediction matched to a real cube with the correct color and sufficient box overlap.
- **False positive (FP):** an unmatched prediction, such as a background object reported as a cube.
- **False negative (FN):** a real cube with no qualifying matched prediction.
- **Precision = TP / (TP + FP):** how many reported detections were correct.
- **Recall = TP / (TP + FN):** how many real cubes were found.

Report the counts and test conditions alongside percentages. The earlier proposed target was at least 80% precision and recall for each color; results on reused training images cannot establish that target for live operation.

## Documentation and current checkpoint

After each completed step, record actual edits, commands, inputs, outputs, checks, and limitations in the [daily technical walkthrough](development-learning-journal.md).

**Current checkpoint:** the project and dataset configuration are open in VS Code. Preparing the new configuration is the next guided step. No new 26-image training run or live deployment has been executed as part of this workflow.
