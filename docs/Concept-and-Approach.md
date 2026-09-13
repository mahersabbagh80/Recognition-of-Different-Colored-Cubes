# Concept and approach

Updated 13 September 2026. This page records the rationale for the implemented approach; it does not claim a comparative model benchmark.

## Why a learned detector?

Color thresholds identify colored regions, but color alone does not establish that an object is a cube. We use a pretrained YOLO detector and fine-tune it on images from the intended camera. This reuses learned visual features and the existing Jetson inference integration.

We did not demonstrate that YOLO outperforms every alternative. Historical model comparisons are preserved in the archive and are not current measured rankings.

## Why our own data and separate validation?

The actual camera introduces room background, object scale, lighting and viewpoints that general datasets may not represent. Labels were visually reviewed. Near-identical captures were reduced, and whole arrangements were kept separate across training and validation.

The final run used 13 earlier images plus 10 new training images and 8 fresh validation arrangements. It still covers one room and limited lighting. Validation selects a development checkpoint; a later untouched test is needed for broader independent claims.

[Methodology review and primary sources](training-validation-methodology-review.md) · [Actual workflow](training-and-validation-workflow.md)

## Why TensorRT and ROS 2?

Training happens on the desktop. ONNX transfers the computation graph, and TensorRT builds an engine for the target Jetson. ROS 2 connects vendor camera inputs to the detector and downstream outputs. Export changes execution format; it does not retrain the model.

## Why geometry after detection?

Depth offers physical evidence beyond appearance. The filter tests candidate shape and raised surfaces before publication. It must reject distractors while retaining actual cubes. September's test showed that it rejected the cubes too. That is an unresolved failure, not a successful full pipeline.

See [architecture](architecture.md), [evaluation](evaluation.md) and the [Sunday record](development-learning-journal/2026-09-13-sunday.md).
