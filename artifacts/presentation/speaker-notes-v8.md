# Speaker notes — version 8

## Slide 1 — Project title

Introduce the project in one sentence: the goal is live recognition of red, green, and blue cubes on NVIDIA Jetson edge hardware. Explain that the talk follows the actual path from data collection to live ROS 2 deployment. The cover illustration is conceptual, not a photograph of the final live test.

## Slide 2 — Problem and success criteria

The engineering problem is to recognize physical cubes, not merely colored pixels. The intended setting is the indoor robot-camera view at about 20–80 cm. Success has several parts: correct color and image box, rejection of non-cube objects, timely updates, and useful depth-based location. These are requirements to evaluate, not claims that every requirement has passed. Navigation and grasping are outside this presentation's project scope.

The earlier plan proposed quantitative targets, but they were not established by an independent full-range test. Do not present those proposed thresholds as a completed acceptance test. Source: docs/sunday-presentation-plan.md, completion and presentation checkpoints.

## Slide 3 — Computer vision fundamentals

Computer vision extracts information from pictures. Our task is object detection: identify each cube's color class and draw a box around it. A box gives a position in the image, not a physical distance. Depth measurements are needed for distance and later 3D localization.

Training changes the model using labeled examples. Inference uses the trained model to make predictions on a photo or a live frame. Validation compares those predictions with known answers. These are the three roles used in the following workflows. Source: docs/learn/reference/training-and-evaluation.html and docs/architecture.md.

## Slide 4 — System architecture

Walk from left to right. The RGB camera supplies pixels. The ROS 2 node prepares a 640 by 640 input. YOLO predicts cube boxes and classes. TensorRT runs the model efficiently on the Jetson GPU. The optional geometry filter uses depth data before final detections and locations are published. This last filter is the unfinished part discovered in the live test. Source: docs/architecture.md and today's technical walkthrough.

## Slide 5 — Method choices

A simple color-threshold detector is an understandable baseline: it searches for pixels in a chosen color range. The weakness is that an ordinary red surface may satisfy that rule too. We chose a pretrained YOLOv5u-small detector and fine-tuned it on reviewed camera images to adapt an existing visual model to the cube classes. Reusing the existing TensorRT and ROS 2 path reduced integration changes. This is a project-fit argument, not a controlled claim of superiority over other detectors.

Depth filtering is an additional geometric test, not another training phase. It should help reject unsuitable shapes but must also retain real cubes. The method has to be tested for both kinds of outcome. Sources: docs/architecture.md; docs/training-validation-methodology-review.md; scripts/run_robot_training_smoke.py. Research references supporting transfer learning and separate evaluation are collected in the appendix. No numerical alternative-model speed claims from historical research are repeated here.

## Slide 6 — My contribution

I used existing software instead of writing a neural network or camera driver from scratch. My work included arranging scenes, collecting camera images, approving labels, executing the dataset export and training, exporting and transferring the model, building the Jetson engine, and interpreting the live tests. Codex assisted with implementation, guided explanations, checks and documentation.

This distinguishes my hands-on work from reused components and AI assistance. It does not imply that I authored every line of code. The engineering understanding I should demonstrate is how the pieces connect, why a choice was made, and what the evidence supports. Sources: docs/development-learning-journal/2026-09-12-saturday.md and 2026-09-13-sunday.md.

## Slide 7 — Data quality

Labels are the expected answers: a class number for the color and coordinates for the box. I reviewed the proposed annotations in the gallery. The exporter converted approved boxes to training labels and checked the selected files against their records. Human review is a quality check, not a guarantee that no labeling error exists.

The capture plan targeted positions and backgrounds underrepresented in the existing photos. We removed redundant selected frames and kept different arrangements for validation. Research corrected the temporary plan to check on the same images: putting a copy in a second folder cannot create unseen evidence. Training examples change the weights; validation examples guide model selection; a later untouched test is required for independent performance claims. Lighting diversity and other rooms remain gaps. Sources: docs/training-validation-methodology-review.md; docs/indoor-cube-capture-checklist.md; scripts/prepare_reviewed_robot_dataset.py. Primary guidance: https://scikit-learn.org/stable/modules/cross_validation.html and https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html.

## Slide 8 — Training workflow

The workflow begins before any training command. We capture varied scenes, review color labels and bounding boxes, and allocate whole arrangements to training or validation. A pretrained checkpoint supplies the initial weights: adjustable numbers inside the network. Only training examples update those weights. For each batch, the model predicts boxes and colors, compares them with the approved labels, computes an error, and adjusts the weights. Repeating a full pass through the training examples is one epoch.

Small random image shifts, scaling and flips add variation during learning; labels move with the image. They supplement scene variety but cannot replace new capture conditions. Training saves checkpoints, which are snapshots of the model. The next slide explains how validation helps select a checkpoint. Sources: scripts/run_robot_training_experiment.py; scripts/prepare_reviewed_robot_dataset.py; docs/development-learning-journal/2026-09-12-saturday.md.

## Slide 9 — Validation workflow

We run the current model on labeled scenes that did not update its weights. Inference generates predictions; comparing them with the approved answers makes it an evaluation. A correct match needs the right color and enough overlap with the approved box. An extra unmatched prediction is a false positive. A real cube without a matching prediction is a false negative.

During training, the validation score helps choose best.pt and can trigger early stopping. That makes validation a development tool, not an untouched final test. After selecting and converting the model, live scenes check the camera and robot runtime too. A later independent test is still needed for a broader reliability claim. Sources: docs/training-validation-methodology-review.md; docs/validation-prediction-review-2026-09-13.md.

## Slide 10 — Deployment workflow

Make the distinction clear: ONNX export and TensorRT conversion did not retrain the model. They changed the runtime format. The TensorRT engine was built on the Jetson Orin Nano with FP16 support. A one-image smoke test reproduced the same V03 class result as PyTorch before the live camera test.

## Slide 11 — Geometry filter purpose

The detector first proposes a box based on the visible image. The geometry filter then uses depth information to check whether the region fits the expected raised, compact shape. It is intended to reject flat colored surfaces and unsuitable shapes. It must also keep real cubes: rejecting every candidate would be a failure, even if false positives disappeared.

Depth values depend on alignment and sampling around the box. Comparing filter-off and filter-on behavior isolates whether this stage removes candidates. It does not identify the root cause of an incorrect rejection by itself. This is the intended method; the actual result appears later. Source: docs/architecture.md and docs/development-learning-journal/2026-09-13-sunday.md.

## Slide 12 — Dataset and training outcomes

This is the first results slide. The prepared dataset combines 13 earlier approved images with 10 new training images, plus 8 separate validation images. There are 13 labeled cube instances per color in training and 6 per color in validation. Three training photos and two validation photos contain no cube. Training ran for 60 epochs and selected epoch 45 as the best checkpoint. A successful training run is not yet evidence that live detection works; we inspect validation and then the live results.

The earlier three-epoch smoke run checked execution but produced poor predictions. That led to a more suitable training schedule and later targeted captures. It is background to our iteration, rather than a dense diagnostic montage in the introduction. Source: runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/ and docs/development-learning-journal/2026-09-12-saturday.md.

## Slide 13 — Validation results

The visual review found 17 of 18 cubes, one missed red cube, and no additional visible box across the eight saved validation views. In V03, blue and green were detected and red was missed. The automated precision and recall are reported at a selected operating point, while average precision summarizes a confidence curve. They need not match the visible-box count at the plotting cutoff. Keep the dataset limitation visible.

## Slide 14 — Live results

The saved screenshot shows the red cube at confidence 0.78. The model score is a ranking or confidence signal, not a measured 78% success rate. In another observed scene, blue, green and red were present together and the view showed exactly three matching boxes. Maher then removed the cubes and reported keep=0. These are limited scene observations, not a long-duration accuracy study.

The node's recent 100-frame windows reported median total processing around 57.7–59.1 ms and median TensorRT inference around 25.9 ms. The slide rounds the first measurement. This is node processing time, not camera-to-browser end-to-end latency or a directly measured output frame rate. A separate synthetic TensorRT benchmark used random inputs and is not substituted for live-pipeline performance. No full distance sweep or stability test is claimed. Source: docs/development-learning-journal/2026-09-13-sunday.md, temporary live model node and live observations.

## Slide 15 — Geometry filter limitation

Explain the diagnostic logic. With the filter disabled, the detector showed correct cubes. With the same engine and the filter enabled, the model still generated about four candidates per frame, but the filter rejected every one under the flat category and published zero detections. We did not tune thresholds today because that needs synchronized RGB and depth evidence rather than guessing.

## Slide 16 — Conclusion

Return to the requirements from the beginning. The new learned detector is deployed and has direct live evidence, including three colors together and a negative scene. The evidence is limited to the tested conditions. We have not established reliability across the full intended distance range, long-running changes, or other environments. The current filter is not acceptable for the complete pipeline because it removes valid cubes.

The next engineering action is to capture synchronized RGB and depth and inspect per-candidate values, then correct the diagnosed cause and test both cube retention and distractor rejection. Verify physical locations separately. The project demonstrates the learning-to-deployment path while making its incomplete acceptance clear. Source: docs/development-learning-journal/2026-09-13-sunday.md; docs/sunday-presentation-plan.md.

## Slide 17 — Validation score definitions

Precision is correct detections divided by reported detections; recall is found objects divided by real objects. Average precision summarizes precision/recall behavior across confidence levels. mAP averages across classes. IoU, intersection over union, measures box overlap: the shared area divided by the total area covered by both boxes. mAP50 uses IoU 0.50; mAP50–95 averages thresholds 0.50 through 0.95 in increments of 0.05.

The eight-image visual review counted 17 matching visible boxes for 18 cubes. Do not substitute that count for the library's reported precision and recall. Ultralytics calculates class curves and reports precision and recall at a selected point; plotted detections use a display confidence threshold. The two presentations can therefore differ without contradiction. All values still describe this small development-validation set. Sources: runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/summary.json; installed Ultralytics utils/metrics.py and utils/plotting.py; docs/validation-prediction-review-2026-09-13.md.

## Slide 18 — Research and experiment references

Primary sources: PyTorch transfer learning tutorial, https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html ; scikit-learn cross-validation and grouped data guidance, https://scikit-learn.org/stable/modules/cross_validation.html ; Dive into Deep Learning generalization, https://en.d2l.ai/chapter_linear-classification/generalization-classification.html . They support general methods, not a benchmark claim about this detector.

Local rationale: docs/training-validation-methodology-review.md; docs/indoor-cube-capture-checklist.md; docs/architecture.md. Authoritative run: runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/summary.json, requested_settings.json, results.csv and weights/best.pt. Training uses YOLOv5u-small, 60 epochs, batch=4, nbs=4, image size 640, AdamW lr0=0.001, warmup_epochs=0, patience=15 and seed=42. The output used the best epoch 45 checkpoint. Model conversion and live evidence are documented in docs/development-learning-journal/2026-09-13-sunday.md. The full source files preserve details omitted from the main slides for clarity.
