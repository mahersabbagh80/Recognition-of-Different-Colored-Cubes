# Machine Learning and Computer Vision Foundations

**Status:** Training-focused tracks; current checks recorded in VALIDATION.md
**Audience:** A programmer new to machine learning, computer vision, and ROS 2 perception
**Format:** Eleven main training lessons and four optional robot lessons, targeting 15–20 minutes for each core path; optional notes and further practice take extra time; PDF regeneration deferred
**Last updated:** 2026-09-08

## Course design

The course starts with the general problem and builds the smallest useful mental model at each step. The colored-cube repository is a recurring worked example, not the source of the fundamentals. Each lesson follows this loop:

1. Frame one concrete question.
2. Explain one central mental model in plain language.
3. Work through a small example.
4. Distribute two or three topic-specific interactions through the explanation, with predictions and explanatory feedback.
5. Apply the idea to the colored-cube project, defining project terminology locally.
6. Ask for an explain-back and point to one primary source.

## Curriculum

| ID | Lesson | Tangible win | Project application |
|---|---|---|---|
| 0001 | [Choose the Vision Task](lessons/0001-choose-the-vision-task.html) | Distinguish classification, detection, and segmentation; write an input/output/success contract. | Decide what colored-cube recognition must return. |
| 0002 | [Images Are Data](lessons/0002-images-are-data.html) | Read pixels, channels, coordinates, shapes, and normalization. | Trace a camera image into the model tensor. |
| 0003 | [Visual Features](lessons/0003-visual-features.html) | Explain color, edges, filters, invariance, and fragility. | Compare color cues with learned cube features. |
| 0004 | [How Models Learn](lessons/0004-how-models-learn.html) | Identify examples, targets, parameters, predictions, and inference. | Interpret labeled cube examples and a trained checkpoint. |
| 0005 | [Loss and Optimization](lessons/0005-loss-and-optimization.html) | Follow prediction → loss → gradient → update. | Explain what a training step changes. |
| 0006 | [Generalization and Data Splits](lessons/0006-generalization-and-data-splits.html) | Separate fitting from generalization; prevent leakage. | Explain why room-domain performance can differ from validation. |
| 0007 | [Neural Networks and Convolutions](lessons/0007-neural-networks-and-convolutions.html) | Trace activations, convolution kernels, feature maps, and receptive fields. | Understand the detector's visual feature extractor. |
| 0008 | [Transfer Learning and Augmentation](lessons/0008-transfer-learning-and-augmentation.html) | Choose when to fine-tune and whether an augmentation preserves a label. | Judge useful and harmful cube-image transformations. |
| 0009 | [Object Detection](lessons/0009-object-detection.html) | Read boxes and scores; calculate IoU; explain thresholding and NMS. | Decode the role of the current YOLO output. |
| 0010 | [Evaluate a Detector](lessons/0010-evaluate-a-detector.html) | Count TP/FP/FN and interpret precision, recall, and AP. | Design an honest colored-cube test matrix. |
| 0011 | [Did Fine-Tuning Help?](lessons/0011-compare-a-fine-tune.html) | Compare matched results against fixed requirements. | Plan a controlled validation/test experiment. |
| 0012 (optional) | [From pixels to 3-D points](lessons/0012-depth-and-camera-geometry.html) | Robot integration after model selection. | Follow-on runtime application. |
| 0013 (optional) | [Can we trust this depth?](lessons/0013-check-depth-evidence.html) | Robot integration after model selection. | Follow-on runtime application. |
| 0014 (optional) | [How ROS 2 carries a frame](lessons/0014-ros2-message-flow.html) | Robot integration after model selection. | Follow-on runtime application. |
| 0015 (optional) | [Deploy the model and diagnose a result](lessons/0015-deploy-and-diagnose.html) | Robot integration after model selection. | Follow-on runtime application. |

## Scope and sequencing

The main course is lessons 0001–0011. It teaches task choice, image representation, useful features, learning, optimization, data quality and splits, network intuition, fine-tuning, detection, evaluation, and a controlled model comparison. Annotation inspection, camera-capture diversity, and actual augmentation choices receive practical attention. Manual arithmetic remains a small explanatory aid, not an implementation requirement.

Lessons 0012–0015 are the optional robot track: camera geometry, depth reliability, ROS 2 flow, and deployment diagnosis. The main finale retains the distinction between a training checkpoint and the model actually loaded at runtime. No required exercise launches training or needs robot hardware.

## Evidence rules

- General ML/CV claims require a primary textbook, paper, course, or official framework source.
- Repository claims require a current file, artifact, or measured report.
- A configured threshold is a policy choice, not a universal constant.
- A smoke test proves execution under its conditions, not real-world accuracy.
- Current code can illustrate an idea while still implementing it incorrectly.

## Completion gate

A lesson is ready for review only when its HTML parses, internal links resolve, interactions work, both themes are readable, and technical claims have an appropriate source. Visual checks must verify the teaching meaning as well as appearance: task outputs must be distinguishable, diagram geometry must match its labels, and plotted values must follow the stated equations. PDF generation is deferred for this revision. Learner mastery remains unmeasured until Maher completes an explain-back or applies the concept.

## Archive

The superseded nine-lesson course is preserved in [`archive/2026-09-07-project-first-course/`](archive/2026-09-07-project-first-course/). Its `SHA256SUMS` file records the archived contents.

## Editorial structure

Start with a concrete problem, introduce terms where they explain it, preserve a worked visual, then explore and attempt a fresh case. Local definitions remain available before dependent questions. Optional notes hold secondary audit details and advanced calculations. The final case brings together artifact selection, data contracts, matching, and a controlled comparison; page completion does not establish mastery.
