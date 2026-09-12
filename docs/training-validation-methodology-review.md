# Training and validation methodology review

12 September 2026. Research only; no training, file moves, or configuration changes executed during this review.

## Recommendation

Use disjoint training and development-validation examples while choosing training settings and checkpoints, then assess the selected system on fresh live robot scenes. Physical folder separation is optional; different examples serving different roles is what matters. This is the recommended methodology, not an assertion that a small split will produce an accurate model.

## Sources and findings

The local [training reference](learn/reference/training-and-evaluation.html), [generalization lesson](learn/lessons/0006-generalization-and-data-splits.html), and [resource shelf](learn/RESOURCES.md) distinguish weight learning, validation-based model selection, and final evaluation. Their guidance was checked against primary documentation:

- [PyTorch's transfer-learning tutorial](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html) uses separate training and validation datasets. Only the training phase updates weights; validation performance selects saved weights. It is a classification example illustrating the general workflow, not a cube-detector benchmark.
- [Dive into Deep Learning: Generalization in Classification](https://en.d2l.ai/chapter_linear-classification/generalization-classification.html) explains why performance on training examples does not establish performance on new examples. Reused-image checks are useful diagnostics; a high score neither proves generalization nor, by itself, proves memorization.
- [Scikit-learn's cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html) separates fitting from evaluation and warns that repeated model choices based on test results compromise their role as final evidence. Its grouped-data guidance keeps related examples together when assessing unseen groups. For this project, that supports keeping neighboring frames from one setup together rather than splitting nearly identical frames across roles.
- [Ultralytics detection dataset documentation](https://docs.ultralytics.com/datasets/detect/) permits directory paths, text lists of image paths, and lists of directories. Two physical folders are not required. Copying a training image into another folder does not make it unseen validation data.

## Current project implications

We verified 13 selected JPGs and 13 matching labels in the training folders, with empty validation folders. The current YAML points both train and val at images/train. This can run and measure fit to training examples, but provides no held-out signal for model selection. The earlier 26-image split record remains historical; it does not describe the current file layout.

Installed Ultralytics source was inspected directly: detection fitness uses mAP at overlap thresholds 0.50 through 0.95; the trainer tracks that fitness for best-checkpoint selection. EarlyStopping uses the configured patience, currently 15. Setting patience to zero disables this stopping rule in the installed implementation. Setting val=False alone does not eliminate every validation call: the final epoch and final checkpoint evaluation also invoke validation. These are verified implementation details, not proposed edits.

Relevant installed files: `ultralytics/engine/trainer.py`, `ultralytics/utils/torch_utils.py`, and `ultralytics/utils/metrics.py` within `.venv-m2/lib/python3.11/site-packages/`.

## Suggested next decision

Reserve a small, deliberate subset of different setups for development validation, with all three colors represented in both sets. Choose examples together before moving files. The 13 images come from one capture session; any small held-out subset will be noisy and limited to similar room conditions. An automatic 80/20 rule cannot fix limited coverage. Grouped cross-validation is another possible later method, but adds multiple runs and still cannot manufacture new conditions.

For the final live assessment, record the model, settings, scene conditions, correct detections, false detections, and misses; verify depth/location separately. Live scenes used to adjust thresholds or choose checkpoints become development evidence. An untouched later check is needed for an independent final estimate.

Training on all development images can be considered as a later refit after settings and a stopping policy are fixed, followed by new external evaluation. For this project, this is a conditional engineering option rather than a claim that the current all-13 run is already a validated final-refit procedure. A time-limited prototype can also use all images, provided its scores are explicitly described as training checks and its live limitations are reported.

## Correction to earlier guidance

The same-image setup was technically workable for the requested fit check, but should not have been presented as equivalent to a held-out development workflow. The recommendation above is to restore sample separation for model selection; no reversal of the user's file organization has been performed without discussion.
