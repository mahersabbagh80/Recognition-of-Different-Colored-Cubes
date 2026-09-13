# Speaker notes — version 7

## Slide 1 — Project objective

Introduce the project in one sentence: the goal is live recognition of red, green, and blue cubes on NVIDIA Jetson edge hardware. Explain that the talk follows the actual path from data collection to live ROS 2 deployment. The cover illustration is conceptual, not a photograph of the final live test.

## Slide 2 — Computer vision fundamentals

Computer vision extracts information from pictures. Our task is object detection: identify each cube's color class and draw a box around it. A box gives a position in the image, not a physical distance. Depth measurements are needed for distance and later 3D localization.

Training changes the model using labeled examples. Inference uses the trained model to make predictions on a photo or a live frame. Validation compares those predictions with known answers. These are the three roles used in the following workflows. Source: docs/learn/reference/training-and-evaluation.html and docs/architecture.md.

## Slide 3 — System architecture

Walk from left to right. The RGB camera supplies pixels. The ROS 2 node prepares a 640 by 640 input. YOLO predicts cube boxes and classes. TensorRT runs the model efficiently on the Jetson GPU. The optional geometry filter uses depth data before final detections and locations are published. This last filter is the unfinished part discovered in the live test. Source: docs/architecture.md and today's technical walkthrough.

## Slide 4 — Research and method choices

We investigated how to train with a small self-collected dataset and how to evaluate it fairly. Fine-tuning reuses general visual features rather than learning everything from random weights. YOLO also fits the existing TensorRT and ROS 2 path; this is a project-fit decision, not a claim that it beats every detector. Our own camera photos match the intended viewpoint and room. Empty scenes and ordinary objects give examples where no cube should be reported. Near-identical frames add little scene variety.

The methodology review changed our temporary same-image plan: validation uses separate arrangements. Copying a training image into another folder would not make it unseen. Generalization means working on examples beyond those used for weight updates. The small one-room collection remains a limitation.

Sources: docs/training-validation-methodology-review.md; docs/indoor-cube-capture-checklist.md; docs/architecture.md. Primary references recorded in the review: PyTorch transfer learning (https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html); scikit-learn grouped evaluation (https://scikit-learn.org/stable/modules/cross_validation.html); Dive into Deep Learning generalization (https://en.d2l.ai/chapter_linear-classification/generalization-classification.html). Historical alternative-model recommendations are not presented as current benchmark findings.

## Slide 5 — Training workflow

The workflow begins before any training command. We capture varied scenes, review color labels and bounding boxes, and allocate whole arrangements to training or validation. A pretrained checkpoint supplies the initial weights: adjustable numbers inside the network. Only training examples update those weights. For each batch, the model predicts boxes and colors, compares them with the approved labels, computes an error, and adjusts the weights. Repeating a full pass through the training examples is one epoch.

Small random image shifts, scaling and flips add variation during learning; labels move with the image. They supplement scene variety but cannot replace new capture conditions. Training saves checkpoints, which are snapshots of the model. The next slide explains how validation helps select a checkpoint. Sources: scripts/run_robot_training_experiment.py; scripts/prepare_reviewed_robot_dataset.py; docs/development-learning-journal/2026-09-12-saturday.md.

## Slide 6 — Validation workflow

We run the current model on labeled scenes that did not update its weights. Inference generates predictions; comparing them with the approved answers makes it an evaluation. A correct match needs the right color and enough overlap with the approved box. An extra unmatched prediction is a false positive. A real cube without a matching prediction is a false negative.

During training, the validation score helps choose best.pt and can trigger early stopping. That makes validation a development tool, not an untouched final test. After selecting and converting the model, live scenes check the camera and robot runtime too. A later independent test is still needed for a broader reliability claim. Sources: docs/training-validation-methodology-review.md; docs/validation-prediction-review-2026-09-13.md.

## Slide 7 — Deployment on NVIDIA Jetson

Make the distinction clear: ONNX export and TensorRT conversion did not retrain the model. They changed the runtime format. The TensorRT engine was built on the Jetson Orin Nano with FP16 support. A one-image smoke test reproduced the same V03 class result as PyTorch before the live camera test.

## Slide 8 — Dataset and training outcomes

This is the first results slide. The prepared dataset combines 13 earlier approved images with 10 new training images, plus 8 separate validation images. There are 13 labeled cube instances per color in training and 6 per color in validation. Three training photos and two validation photos contain no cube. Training ran for 60 epochs and selected epoch 45 as the best checkpoint. A successful training run is not yet evidence that live detection works; we inspect validation and then the live results.

The earlier three-epoch smoke run checked execution but produced poor predictions. That led to a more suitable training schedule and later targeted captures. It is background to our iteration, rather than a dense diagnostic montage in the introduction. Source: runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/ and docs/development-learning-journal/2026-09-12-saturday.md.

## Slide 9 — Validation results

The visual review found 17 of 18 cubes, one missed red cube, and no additional visible box across the eight saved validation views. In V03, blue and green were detected and red was missed. The automated precision and recall are reported at a selected operating point, while average precision summarizes a confidence curve. They need not match the visible-box count at the plotting cutoff. Keep the dataset limitation visible.

## Slide 10 — Live ROS 2 detection

This screenshot is direct evidence from the live ROS 2 debug stream. The single red cube appeared at confidence 0.78. In the next observed scene, all three colors appeared together with exactly three boxes. After removing all cubes, the view reported keep equals zero. These are observed scenes, not a statistical reliability test.

## Slide 11 — Geometry filter limitation

Explain the diagnostic logic. With the filter disabled, the detector showed correct cubes. With the same engine and the filter enabled, the model still generated about four candidates per frame, but the filter rejected every one under the flat category and published zero detections. We did not tune thresholds today because that needs synchronized RGB and depth evidence rather than guessing.

## Slide 12 — Conclusion and next engineering step

Close with the selected core message. State the remaining scope precisely. The detector is live and the three colors were observed together. The geometry-filtered, depth-based location pipeline still needs diagnosis and verification. End by naming the parts you can now explain and reproduce: data preparation, labels, training settings, validation, checkpoint selection, ONNX export, TensorRT build, and ROS 2 live testing.
