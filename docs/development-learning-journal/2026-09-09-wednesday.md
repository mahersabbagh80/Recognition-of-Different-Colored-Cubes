# Wednesday, 9 September 2026 — technical development journal

[Journal index](../development-learning-journal.md) · [Daily plan](../sunday-presentation-plan.md) · [Progress record](../sunday-progress.md)

This records data preparation, environment checks, and the completed three-epoch training smoke run. Earlier sections preserve the status at each stage; the latest outcome is at the end. Paths in code examples are relative to the project root unless stated otherwise.

## 9 September — from camera photographs to training examples

**Status:** data preparation completed for an initial experiment. No new model has been trained or deployed. Approximate reading time: 10–15 minutes.

### 1. What problem were we solving?

We have photographs of our cubes, but photographs alone do not tell a training program which objects it should learn to locate and name. We needed to turn a useful selection of those photographs into checked teaching examples.

**Computer vision** means extracting useful information from images. Our chosen task is **object detection**: locate each target object and assign its category. Here, the categories, also called **classes**, are red cube, green cube, and blue cube.

An **annotation** is the information we add about an image. Our annotations contain a class and a **bounding box**: a rectangle enclosing the visible cube. A photograph with its annotations forms a labeled example. A **dataset** is a collection of these examples.

### 2. Which model and which images?

Two different collections caused confusion in our discussion. The historical project records describe an earlier model trained using an external cube dataset. Maher later captured **98 robot-camera images** following his instructor's advice to collect his own data. Those captures were not the images used for that earlier training.

The revised approach is to train a new cube model using Maher's checked images. The intended starting point is a compatible **general pretrained checkpoint**: a saved model whose numerical parameters have already been learned from a broader image collection. Adapting that learned model to our task is **transfer learning**, also called fine-tuning. Starting with no learned parameters would be training from scratch. We have not yet verified or loaded the new starting checkpoint.

The project-specific training data will be our own images. General pretraining still brings knowledge learned from external data; this distinction should be clear in the presentation. We have not been told that the instructor prohibits general pretraining.

At Maher's request, the old cube-trained files and related checkpoints were removed from this local checkout. Historical reports remain, and robot-side copies were not changed. Removing a model does not change the camera photographs or their annotations.

### 3. What did we actually review?

The first gallery contained 13 previously proposed annotations, one image from each capture group. Codex had placed the boxes; Maher checked that every target cube had the correct color and a box covering its complete visible extent, excluding its cast shadow. The empty background was confirmed to contain no target cubes.

We then inspected contact sheets showing all 98 images. A **contact sheet** places many photographs on one page so we can compare scenes efficiently. It showed useful changes in distance, color combinations, and spacing, but many repeated frames within each setup.

The second gallery used a different frame from each of the same 13 setups. First-frame coordinates were only starting proposals: Codex inspected the new full frames and enlarged target regions, and Maher confirmed the second batch. Prior approval was not automatically transferred to another image.

**Result: 26 human-confirmed images, 54 cube boxes, and two empty backgrounds.** The other 72 photographs remain available but are unselected. They are not implicitly labeled or approved. The 26-image subset is a compact experiment, not a claim that 26 images are sufficient for dependable detection. The second batch adds modest appearance variation, not new independent scenes.

### 4. What does “saving the labels” mean?

The original photograph stays unchanged. A separate review record stores its identity, cube classes, box coordinates, and Maher's confirmation. The exporter creates image copies and separate text label files for training.

The green rectangles and text in the gallery are a viewing aid. They are not painted into the training photographs. Overlapping label text was therefore a readability problem, not corrupt training data. In the second gallery, numbered boxes and separate color names made review easier.

An image's **hash** is a fingerprint calculated from its file contents. We used hashes to check that the reviewed photograph was the same file we later copied. Hash agreement checks file identity; it does not prove that its labels are correct or that another photograph is visually different.

### 5. One actual box, from pixels to a label file

A **pixel** is one position in the image grid. Our photographs are 640 pixels wide and 360 pixels high. Horizontal position increases from left to right; vertical position increases from top to bottom. We describe a rectangle with left, top, right, and bottom coordinates.

The red cube in the first close-up image has the approved coordinates:

| Quantity | Value | Meaning |
|---|---:|---|
| Left | 284 | Left boundary in the image |
| Top | 193 | Top boundary |
| Right | 310 | Right boundary |
| Bottom | 225 | Bottom boundary |

The exported format uses the box's center, width, and height instead of its corners:

- Center horizontally: `(284 + 310) / 2 = 297` pixels.
- Center vertically: `(193 + 225) / 2 = 209` pixels.
- Width: `310 - 284 = 26` pixels.
- Height: `225 - 193 = 32` pixels.

**Normalization** here means expressing those values as fractions of the image dimensions. Horizontal center and width are divided by 640; vertical center and height are divided by 360. These are geometric fractions, not confidence scores or accuracy values.

| Exported field | Calculation | Value |
|---|---|---:|
| Class ID | Our mapping: blue = 0, green = 1, red = 2 | 2 |
| Horizontal center | 297 / 640 | 0.4640625 |
| Vertical center | 209 / 360 | 0.5805556 |
| Width | 26 / 640 | 0.040625 |
| Height | 32 / 360 | 0.0888889 |

The actual first line in that image's exported label file is:

```text
2 0.4640625000 0.5805555556 0.0406250000 0.0888888889
```

One line describes one cube; an image with three cubes has three lines. A reviewed empty background has an empty label file. This says that none of our target classes is present; it does not mean the photograph contains no furniture or other objects.

**Connection to our code:** in [prepare_reviewed_robot_dataset.py](../../scripts/prepare_reviewed_robot_dataset.py), `main()` reads approved boxes and performs this exact conversion. The local variables `x1`, `y1`, `x2`, and `y2` mean left, top, right, and bottom:

```python
values = [(x1 + x2) / (2 * width), (y1 + y2) / (2 * height),
          (x2 - x1) / width, (y2 - y1) / height]
```

The script also reconstructs the pixel box from the exported values and checks it against the input. That round-trip check catches conversion mistakes. It cannot replace visual review of the original box.

### 6. Why split the examples?

**Training** adjusts the model's learned parameters using labeled examples. **Validation** checks a candidate on examples excluded from that parameter-fitting step and helps us choose model versions or settings. A **final test** is a separate assessment after those choices are frozen.

If almost identical frames appear in both training and validation, the validation result may mostly measure performance on a scene the model has effectively already seen. That makes it weak evidence of **generalization**: performing well on different, unseen examples.

We initially said that one continuous capture session necessarily required another session for validation. That was too categorical. A single session can contain distinct arrangements. Actual scene similarity matters, not just the date or session name.

After inspecting the photographs, we chose a limited same-session development split. A **group** here means all frames of one named physical setup. Both selected frames of each group stay together, and unused siblings of validation groups must also stay out of training.

| Allocation | Images | Cubes of each color | Empty backgrounds |
|---|---:|---:|---:|
| Training: 11 setups | 22 | 14 | 2 |
| Validation: 40-centimeter and spread-out setups | 4 | 4 | 0 |

Holding out those setups probes a different distance condition and a spread-out arrangement while leaving all three colors in each split. This is a practical development choice, not a universal splitting recipe. File names describing distances are capture claims, not independent measurements.

**Limits:** the four validation images represent only two arrangements, share the room and session with training, and contain no empty backgrounds. They cannot establish general room reliability or background-only false-positive performance. Fresh varied captures would strengthen evaluation; the separate final test remains planned.

### 7. What will the measurements mean?

A **correct detection** identifies the right class and locates the object sufficiently well under the evaluator's matching rule. A **false detection** reports a target without a valid match. A **miss** is an actual target left undetected.

**Precision** is correct detections divided by all reported detections. **Recall** is correctly detected targets divided by all actual targets. These answer different questions: “Can I trust what was reported?” and “How much was missed?”

Our proposed final target is at least 80% precision and recall for each color, with separate live-speed checks. It is not a measured result. In the tiny current validation set, each color has only four cubes: detecting three gives `3 / 4 = 75%` recall. One additional correct detection changes recall by 25 percentage points. That illustrates why this set is useful for a first check but too small to justify a strong reliability claim.

### 8. What is verified, and what is still unknown?

Verified: Maher's approval of the selected annotations; exact image copies; complete image/label pairs; class IDs; valid box bounds; coordinate conversion; and no exact-image or setup overlap between the chosen splits.

Unknown: whether the new model will learn useful detection from this subset, how it will perform on fresh scenes, and whether the complete deployed pipeline will preserve its performance. No training result exists yet.

The immediate next step is verifying the general pretrained checkpoint and its compatibility with the intended training and deployment path. A small training run then checks that the data and training software work together. Actual robot performance is a later measurement.

### 9. Explain it in your own words

These questions are optional discussion prompts, not a completed assessment. Answers have not yet been evaluated.

1. What are the separate roles of the photograph and its annotation file?
2. Why would placing neighboring frames of the same setup into both splits give a misleadingly easy check?
3. If the model finds three of four actual red cubes, what is its recall, and why is one more image not automatically one more independent scene?

<details>
<summary>Worked answers for checking your explanation</summary>

The photograph supplies the visual input. The annotation file supplies the expected locations and classes used to teach or evaluate the detector. The visible gallery overlay is a review aid.

Neighboring frames often show nearly the same objects, positions, background, and lighting. Success on one after learning from another provides limited evidence of handling new arrangements.

Recall is three divided by four, or 75%. A second frame of an unchanged setup may add only a little visual variation; it is another observation of much the same scene.

</details>

### Evidence and further reading

- [Image-variety inspection](../../evaluation/robot_dataset_2026-09-09/variety-review.md)
- [Saved human review](../../evaluation/robot_dataset_2026-09-09/human_review.json)
- [Training preparation and limitations](../../evaluation/robot_dataset_2026-09-09/training-preparation.md)
- [Exact split manifest](../../evaluation/robot_dataset_2026-09-09/development_split.json)
- [Current teaching course](../learn/index.html) for deeper explanations and exercises

Future entries will describe training, evaluation, and deployment only after those steps occur. Human label approval is recorded here as completed project work; conceptual mastery remains unassessed until Maher explains or applies the ideas.


## 9 September — training environment preflight (partial)

**Purpose:** establish which software and starting model we can actually use before launching training. No training has run. The following records checks already performed and separates them from the planned next steps.

### Inputs and software responsibilities

The prepared dataset configuration is `evaluation/results/robot_training_2026-09-09/data.yaml`. It points to the image folders and maps IDs to the three cube colors. Each image has a corresponding text annotation file in the label folder.

The project has an existing Python virtual environment at `.venv-m2`. A **virtual environment** gives this project its own Python interpreter and installed packages. It does not provide a GPU or guarantee that the GPU driver is accessible.

**PyTorch** supplies tensor computation and automatic differentiation: calculating how a change in a learned parameter affects the training error. A **tensor** is an array of numerical values; model inputs and learned parameters are represented this way. **Ultralytics** supplies the detector implementation, dataset loading, training loop, validation, and export interfaces. Our code configures and checks these facilities; we are not implementing an optimizer or neural network from scratch.

### Exact check executed

From the project root, the interpreter and imports were checked with:

```sh
.venv-m2/bin/python -c 'import torch, ultralytics; print("torch",torch.__version__); print("ultralytics",ultralytics.__version__); print("cuda_available",torch.cuda.is_available())'
```

Observed output:

```text
torch 2.6.0+cu124
ultralytics 8.4.75
cuda_available False
```

**CUDA** is NVIDIA's GPU-computing platform. The installed PyTorch build reports CUDA 12.4 in its version suffix, but `torch.cuda.is_available()` checks whether this process can currently use CUDA. A CUDA-capable package and an accessible GPU are different conditions.

This first check ran in the restricted execution environment. It establishes only that this process did not see usable CUDA. It does not establish the cause, a broken graphics card, or the availability of CUDA in another execution context. Device/driver visibility must be checked before choosing the training device. No dependency upgrade or driver change has been made.

### Why the exact YOLO variant matters

The old run's saved arguments name `yolov5s.pt`. The current robot decoder reads an exported three-class output shaped `[1, 7, 8400]`. Here, 1 is the batch size, 7 is four box values plus three class scores, and 8400 is the number of candidate positions at the documented image size. These expectations are evidence about our code, not proof of a newly loaded checkpoint's behavior.

The official documentation distinguishes original YOLOv5 from the Ultralytics YOLOv5u implementation. It explicitly gives `yolov5su.pt` as a small-model starting checkpoint compatible with the Ultralytics library. This makes it the intended candidate to verify; it has not yet been downloaded or loaded by this preparation step. See [Ultralytics YOLOv5 documentation](https://docs.ultralytics.com/models/yolov5/).

We must verify the actual model structure and class adaptation, then later its exported output and score interpretation. A familiar filename alone is insufficient. The existing unrelated `yolo26n.pt` file is not authorization to switch architectures.

### Planned training mechanism — not executed yet

A **batch** is a group of training images processed together. An **epoch** is one pass through the training set. The data loader reads the original photographs and their separate labels, applies the configured resizing and any selected augmentation, and transforms the box coordinates consistently. **Augmentation** means deliberate variation of training inputs; any color-changing settings need particular care because color defines our classes.

During a **forward pass**, the model predicts locations and class scores. A **loss function** quantifies disagreement with training labels. **Backpropagation** calculates gradients: how sensitive that loss is to each learned parameter. An **optimizer** uses these gradients to update parameters. The actual optimizer, learning rate (update step size), augmentation settings, and number of epochs will be documented when selected, rather than guessed now.

Validation runs predictions without applying parameter updates from the validation labels. However, using validation to choose checkpoints or settings still influences model selection; that is why it is distinct from the final test. The training library saves logs, measurements, and model checkpoints. See [Ultralytics training documentation](https://docs.ultralytics.com/modes/train/).

A short smoke run will first check that data loading, computation, updates, validation, and saving succeed together. Successful execution alone does not mean adequate accuracy. A later controlled training experiment evaluates useful learning, and a later robot test evaluates the deployed system.

### Evidence and next action

Inspected the old run arguments, prepared dataset configuration, and the actual `_decode_yolov5_output` function in `recognition_of_different_colored_cubes/cube_detection_node.py`. Imported both training libraries and recorded their versions. GPU availability in the first checked process is unresolved. New checkpoint verification and training are pending.

**Explain-back:** Why can a CUDA-enabled PyTorch installation still report that CUDA is unavailable? Why do we check the actual model output rather than assuming two checkpoints with “YOLOv5” in their names are interchangeable?


## 9 September — GPU preflight and first training run completed

### Purpose and actual outcome

Verify that our reviewed images, label files, starting checkpoint, GPU training, validation, and checkpoint saving work together. The three-epoch run completed. This is a successful **software smoke test**, not a successful final detector: reported validation precision remains very poor. No robot deployment occurred.

### 1. GPU access: distinguish process restrictions from broken hardware

The same `nvidia-smi` check failed inside the restricted process and succeeded when run with approved host GPU access. A tiny PyTorch calculation also succeeded on the RTX 4070 Ti:

```python
assert torch.cuda.is_available()
x = torch.ones((2, 2), device="cuda")
print(x.sum().item())  # observed: 4.0
```

The comparison shows that usable host GPU access exists and that the initial result was specific to the restricted execution context. No graphics driver installation or system modification was required. The GPU has approximately 12 GB of memory, some already used by desktop applications; batch size was kept small.

### 2. Starting checkpoint and architecture verification

Downloaded `yolov5su.pt` from the official Ultralytics asset release into `models/pretrained/yolov5su.pt`. The source URL and file hash are saved in [training_preflight.json](../../evaluation/robot_dataset_2026-09-09/training_preflight.json).

The model loaded as a general detector with 80 original classes. Its architecture encodes small-model depth/width multipliers directly. Our first assertion mistakenly expected a newer `scale: s` field and stopped before training. Inspection of the checkpoint and installed architecture configuration established the equivalent values, 0.33 and 0.5. The check was corrected to verify those actual fields rather than bypass model verification.

The architecture was instantiated with three output classes and compatible pretrained parameters loaded. A forward pass at input `[1, 3, 640, 640]` produced finite predictions of shape `[1, 7, 8400]`. This checks the expected PyTorch output dimensions. ONNX/TensorRT numerical parity, score semantics in the deployed path, and live robot behavior still need separate checks.

### 3. Exact executed training entry point

From the project root, with approved GPU access:

```sh
.venv-m2/bin/python scripts/run_robot_training_smoke.py > evaluation/results/wednesday-training-smoke.log 2>&1
```

The redirection saves standard output and errors to a log. The [training script](../../scripts/run_robot_training_smoke.py) verifies the dataset review fingerprint and copied-image hashes, checks the model, calls Ultralytics training, and verifies the saved model classes. It refuses to overwrite an existing run. The first failed preflight log is retained separately as `evaluation/results/wednesday-training-preflight-first-attempt.log`.

### 4. Chosen settings and why

| Setting | Chosen value | Reason |
|---|---|---|
| Epochs | 3 | Exercise the complete loop cheaply; not intended for convergence |
| Input size | 640 | Match the existing intended detector input size |
| Batch size | 4 | Small GPU-memory footprint; 22 training images require six batches per epoch |
| Device | GPU 0 | Verified accessible RTX 4070 Ti |
| Data-loader workers | 0 | Load in the main process; avoid extra process complexity for this tiny check |
| Optimizer | AdamW | Explicit reproducible optimizer choice instead of automatic selection |
| Initial learning rate | 0.001 | Requested base update scale; actual scheduled rates are recorded separately |
| Warm-up | 0.5 epochs requested | Gradual startup; library minimum has an important effect described below |
| Mixed precision | Disabled | Use ordinary full-precision training for this first functional check |
| Hue and saturation augmentation | Both disabled | Avoid changing class-defining colors |
| Brightness augmentation | 0.1 | Modest brightness variation |
| Scale and translation augmentation | 0.1 and 0.05 | Modest size/position variation, with boxes transformed consistently |
| Horizontal/vertical flips | 0.5 / 0.0 | Allow left-right variation; avoid upside-down floor scenes |
| Mosaic and mixup | Disabled | Keep the first training images simple to inspect |
| Seed | 42 | Fix random choices where supported; not a claim of universal bitwise repeatability |

**Mixed precision** combines numerical precisions to reduce memory use or improve speed. **Mosaic** combines multiple images spatially; **mixup** blends images. They are not needed for this initial check. Full resolved options are saved by the library in the run's `args.yaml`; our explicitly requested options are in [smoke_requested_settings.json](../../evaluation/robot_dataset_2026-09-09/smoke_requested_settings.json).

**Warm-up detail discovered from the installed training code:** Ultralytics uses at least 100 warm-up iterations when warm-up is enabled. Our run has only 18 batches across three epochs, so it remains in warm-up throughout. Actual learning rates differ from the requested base rate and appear in `results.csv`. This is acceptable for exercising the training loop, but the next meaningful experiment needs an explicit warm-up decision appropriate to a tiny dataset. Do not present this short run as a completed optimization experiment.

### 5. Evidence from execution

The library reported 22 training images, including two empty backgrounds, and four validation images, with zero corrupt images. We inspected `train_batch0.jpg`: transformed photographs and boxes were aligned; the overlay is a diagnostic output rather than the image data fed as labels.

Across the three epochs, training box loss went from about 0.971 to 0.884, and classification loss from about 3.526 to 1.373. **Classification loss** measures error in class prediction; **box loss** measures localization error under the training implementation. Decreasing training loss indicates progress on the optimization objective, not guaranteed generalization.

The final library summary reported approximately **1.42% precision and 91.67% recall** on the tiny validation set. High recall alongside low precision means many reported candidates are wrong. These library-reported values are not a separately measured fixed-confidence 0.50 acceptance test and must not be compared directly with the old report as if the protocols matched. Four frames from two same-session setups are insufficient for strong reliability claims.

The saved checkpoint reload verified the three class names and a finite `[1, 7, 8400]` output. The smoke run is complete; no training job remains running.

### 6. Outputs and next engineering decision

- [Preflight evidence](../../evaluation/robot_dataset_2026-09-09/training_preflight.json): environment, checkpoint provenance, architecture, and adapted shape.
- [Smoke summary](../../evaluation/robot_dataset_2026-09-09/smoke_summary.json): saved model identity and library validation metrics.
- Run directory: `runs/robot_2026-09-09/smoke_3ep/`.
- Saved weights: `weights/best.pt` and `weights/last.pt` within that directory.
- `args.yaml`: resolved training configuration.
- `results.csv`: per-epoch losses, metrics, and learning rates.
- `train_batch0.jpg`: actual transformed training examples for inspection.
- `val_batch0_labels.jpg` and `val_batch0_pred.jpg`: reference and prediction previews.

Next, plan a controlled training experiment with an appropriate learning-rate/warm-up schedule and inspect validation predictions at a stated confidence threshold. We have not yet integrated the full earlier evaluator into this checkout; the smoke run used Ultralytics validation. The old robot engine has not been replaced.

**Explain-back:** What did the successful smoke run establish? Why do a decreasing training loss and high recall not establish that this is a dependable detector? Why should we inspect actual learning-rate logs rather than only the requested learning rate?


## 9 September — inspecting what the validation metrics hide

The saved `val_batch0_pred.jpg` montage showed no boxes. Inspection of the installed plotting code established a display cutoff of 0.25: weak predictions were omitted from the picture, while validation metrics consider lower scores. Saying only “many false detections” was incomplete without specifying the threshold.

We reran the saved smoke model on the four original validation images using CPU inference, `imgsz=640`, `rect=False` (square input), `conf=0.001`, NMS IoU 0.70, and at most 300 candidates per image. **NMS**, non-maximum suppression, removes sufficiently overlapping competing boxes according to its settings. This new review is distinct from the library's aggregate validation preprocessing/operating-point summary.

Stored predictions are in `evaluation/robot_dataset_2026-09-09/smoke_prediction_review.json`. For each cutoff we processed predictions from highest to lowest score, matched each to at most one unmatched reference box of the same color, and required IoU at least 0.50. **IoU**, intersection over union, is the overlapping area of two boxes divided by their combined area. Unmatched predictions count as false detections; unmatched reference cubes count as misses.

| Score cutoff | Correct | False detections | Missed cubes |
|---|---:|---:|---:|
| 0.001 | 6 | 648 | 6 |
| 0.01 | 2 | 20 | 10 |
| 0.25 | 0 | 0 | 12 |
| 0.50 | 0 | 0 | 12 |

The strongest prediction across these four images scored only about 0.075. On the first 40-centimeter image, the top candidates label the chair wheel blue and red and label the actual green cube blue. The comparison image draws only the top three to keep it readable; the counts include all predictions above each cutoff. Scores are model outputs, not established probabilities of correctness.

**Interpretation:** low cutoffs admit many false detections, while higher cutoffs miss every cube. Neither demonstrates acceptable performance. The small smoke run verified execution, not detection quality. We did not tune a deployment threshold or retrain during this inspection.

Visual review: `evaluation/results/wednesday-review/smoke-results.html`; shareable comparison: `evaluation/results/wednesday-review/smoke-comparison.jpg`.

**Explain-back:** Why can an empty prediction overlay coexist with poor reported precision? What happens to misses when the cutoff removes every prediction?

## Controlled training experiment — 60 epochs completed

**Purpose.** Give the model a substantive opportunity to learn from the approved own-camera data after the three-epoch execution check. This is one bounded development experiment, not a hyperparameter search or final acceptance test.

**Inputs.** The same official general COCO-pretrained `models/pretrained/yolov5su.pt` and `evaluation/results/robot_training_2026-09-09/data.yaml`: 22 training images and four held-out validation images. Training starts fresh from the general checkpoint, not from smoke weights. The script checks its SHA-256, the human-review manifest hash, copied image hashes, and label coverage. Whole validation setups remain excluded from training.

**Implementation.** [Training script](../../scripts/run_robot_training_experiment.py) uses the existing Python environment, PyTorch and Ultralytics. Actual executed command (host GPU access approved):

```bash
.venv-m2/bin/python scripts/run_robot_training_experiment.py > evaluation/results/wednesday-training-experiment.log 2>&1
```

Ultralytics loads batches, applies configured augmentations, predicts boxes/classes, computes box/class/distribution losses, backpropagates gradients, and updates weights with AdamW. Validation does not update weights; it influences checkpoint selection and early stopping.

**Optimizer schedule.** An epoch visits the training dataset once. With 22 images and batch size four, each epoch has six batches, including a final partial batch. The previous positive `warmup_epochs` activated a minimum 100 warm-up iterations in installed `ultralytics/engine/trainer.py`; all 18 smoke batches were within it. We set `warmup_epochs=0` for this experiment and use a modest initial learning rate of 0.001. Warm-up gradually introduces the optimizer settings; disabling it here is an experiment choice, not a general rule that warm-up is bad.

We also set `nbs=4`. The installed trainer calculates gradient accumulation as `max(round(nbs / batch_size), 1)`. Default `nbs=64` with batch four would accumulate 16 batches between optimizer steps outside warm-up. With `nbs=4`, it updates after every batch: 360 batch updates over 60 epochs. `nbs` also participates in weight-decay scaling; here the scale factor is one. The linear learning-rate schedule uses `lrf=0.1` (target final rate one tenth of the initial rate). `patience=15` permits early stopping after 15 epochs without fitness improvement; this run reached the 60-epoch limit. This changes duration and optimizer scheduling together, so improvement cannot be attributed exclusively to warm-up.

**Other settings.** `imgsz=640`, `batch=4`, GPU `device=0`, and `workers=0` retain the smoke setup. `amp=False` uses full precision. Seed 42 and deterministic mode aid repeatability. Hue and saturation augmentation remain zero to protect color-class meaning; brightness variation is 0.1. Scale variation 0.1, translation 0.05 and horizontal-flip probability 0.5 provide modest geometric variation. Vertical flipping, mosaic, and mixup are disabled. These augmentations do not create independent captured scenes. Caching is disabled; validation, plots and checkpoint saving are enabled. The complete requested settings are in [experiment_requested_settings.json](../../evaluation/robot_dataset_2026-09-09/experiment_requested_settings.json), and effective library settings are in the run's `args.yaml`.

**Outputs and checks.** Run directory: `runs/robot_2026-09-09/experiment_60ep/`. `results.csv` contains epoch metrics; `weights/last.pt` is the final epoch; `weights/best.pt` is selected using validation fitness (mAP50–95), so its metrics can differ from epoch 60. Reloading best weights verified class IDs 0 blue, 1 green, 2 red and finite PyTorch output `[1,7,8400]`. No ONNX export, TensorRT conversion or robot deployment occurred. The evidence summary stores the checkpoint hash: [experiment_summary.json](../../evaluation/robot_dataset_2026-09-09/experiment_summary.json).

The final library evaluation of best weights reported precision 0.9392, recall 0.9163, mAP50 0.9950 and mAP50–95 0.7571. These are library validation metrics, including its chosen operating point, not our fixed-confidence acceptance counts. The original training prediction montage was inspected: it shows detections on real cubes and misses the spread-out blue cube; its preprocessing and display cutoff differ from the explicit check below.

### Fixed-confidence development check

Before seeing the new results we specified confidence 0.50. Actual executed command:

```bash
.venv-m2/bin/python scripts/evaluate_robot_experiment.py
```

[Evaluation script](../../scripts/evaluate_robot_experiment.py) loads `best.pt`, verifies validation image hashes and predicts on the four images using CPU, `imgsz=640`, `rect=False` (square letterboxing), confidence 0.50, NMS IoU 0.70, and a maximum of 300 detections. It sorts predictions by confidence, requires the correct class and box IoU of at least 0.50, and matches each approved cube at most once. Duplicate-match and wrong-class sanity checks passed. Precision is TP/(TP+FP); recall is TP/(TP+FN). Undefined precision is recorded as null when no predictions exist.

| Color | Correct (TP) | False (FP) | Missed (FN) | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| Blue | 2 | 0 | 2 | 100% | 50% |
| Green | 3 | 0 | 1 | 100% | 75% |
| Red | 4 | 0 | 0 | 100% | 100% |
| Total | 9 | 0 | 3 | 100% | 75% |

Full boxes, scores and counts: [experiment_fixed_validation.json](../../evaluation/robot_dataset_2026-09-09/experiment_fixed_validation.json). Compared with the smoke review under the same square input and 0.50 cutoff (zero found, 12 missed), this is a substantial improvement. Blue and green recall remain below the proposed 80% per-color target at this cutoff. Do not interpret this as a final test: there are only four images from two same-session arrangements, and no background-only validation frames. They have also been used for model selection. We did not lower the threshold after seeing the result to declare a pass.

**Next, not yet performed:** review these predictions together, especially missed blue/green examples, before choosing a targeted data or configuration change. Fresh independent evaluation and robot/depth verification remain pending. No training job is running.

**Explain-back:** Why can the library's recall differ from the fixed-confidence count? Why does a successful 60-epoch run still not establish performance on new robot scenes? What does `nbs=4` change when batch size is four?

## Reviewing the three missed cubes — confidence diagnosis

**Question.** At the fixed 0.50 cutoff, did we miss cubes because of incorrect colors, inaccurate boxes, or low prediction scores?

**Executed command:**

```bash
.venv-m2/bin/python scripts/inspect_robot_experiment_misses.py
```

[Inspection script](../../scripts/inspect_robot_experiment_misses.py) reloads the same best checkpoint and verifies validation image hashes. It uses exactly the previous CPU square-input settings (`imgsz=640`, `rect=False`, NMS IoU 0.70, max 300 detections), but requests candidates down to confidence 0.001. No training occurs. For each approved cube it records overlapping candidates, their class, confidence and IoU. It also recomputes one-to-one counts at 0.001, 0.10, 0.25 and 0.50. An assertion verifies that the 0.50 counts reproduce the prior fixed-confidence evaluation. This is post-hoc diagnosis, not a new acceptance threshold.

**Observed findings.** All three misses occur in the two held-out spread-out frames. The two 40 cm images have all six cubes detected correctly at 0.50. The strongest correct-color overlapping candidates for the missed cubes are:

| Frame | Missed color | Confidence | Box IoU |
|---|---|---:|---:|
| `spread_out_0001.jpg` | Blue | 0.0092 | 0.7699 |
| `spread_out_0004.jpg` | Blue | 0.0310 | 0.8036 |
| `spread_out_0004.jpg` | Green | 0.4630 | 0.8900 |

These boxes meet the matching criterion and use the correct color. Their scores fall below the reporting cutoff. Confidence is a model score, not a calibrated probability or proof of correctness. The green score is relatively near 0.50; the blue scores are much lower.

| Diagnostic cutoff | Correct | False | Missed |
|---|---:|---:|---:|
| 0.001 | 12 | 7 | 0 |
| 0.10 | 10 | 0 | 2 |
| 0.25 | 10 | 0 | 2 |
| 0.50 | 9 | 0 | 3 |

Lowering to 0.25 recovers green but not blue. At 0.001 all true cubes have matches, but seven extra detections appear. The original 0.50 result remains unchanged; no deployment configuration was edited. Full reproducible evidence: [experiment_miss_review.json](../../evaluation/robot_dataset_2026-09-09/experiment_miss_review.json).

**Visual and dataset context.** Inspected the original `spread_out_0004.jpg`: blue is near the right edge, while green is farther away beside the curtain. The manifest's seven first-frame training setups containing blue have box centers at x=315–408 pixels; the held-out blue center is x=516 in a 640-pixel image. Its 30×25-pixel box is within the broad training size range (10×10 to 32×33). This establishes limited original training-position coverage, not a causal diagnosis: training includes geometric augmentation, and appearance, background and position vary together. We have not proved which factor caused low blue confidence.

**Decision and next physical step (not yet performed).** Keep this candidate and fixed evaluation unchanged. Prefer a small targeted capture batch over blind extra epochs: approximately 12–18 deliberately different arrangements with blue at left, center and right; vary distance, orientation and nearby background, and include green and red in some scenes. Capture a few empty scenes as well. Move cubes or viewpoint between pictures rather than saving repeated neighboring frames. Human-review the labels. Allocate whole new setups to training or development validation before fitting again, and reserve later independent test captures separately. Do not move the current spread-out validation frames into training to erase the observed failure.

This is a proposed capture task, not a claim that existing training images are useless or that more data guarantees improvement. Robot access is needed to execute it. No new captures, retraining, export or deployment occurred during this review.

**Explain-back:** How can a cube have a good predicted box but still count as missed? Why does recovering a cube by lowering confidence not automatically improve the detector overall? Why must new images vary in arrangement rather than only frame number?
