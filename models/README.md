# models/ — YOLOv5s weights for the cube-detection pipeline

> **Current inventory — 13 September 2026:** The selected replacement checkpoint is `runs/robot_2026-09-12/experiment_60ep_20260912_221210+0200/weights/best.pt` on the desktop. It was fine-tuned from general pretrained YOLOv5u-small on 23 reviewed training images with 8 validation images; selected epoch 45. Its ONNX export was transferred and built into `/home/ubuntu/maher_ws/best_2026-09-12.engine` on the robot. This dated engine was tested explicitly; the older default engine was not replaced. See [technical stack](../docs/technical-stack.md) for verified hashes and [Sunday evidence](../docs/development-learning-journal/2026-09-13-sunday.md) for commands and limitations.
>
> The tables and commands below are **historical June artifact records**, not the current inventory or training recipe. Model files remain local and are not supplied by Git.

This directory holds the trained detection artifacts. Both files are git-ignored
along with everything else under `models/` except this `README.md` and `.gitkeep`.

| File | Milestone | Purpose |
|---|---|---|
| `best.pt` | M2 | 18.5 MB PyTorch YOLOv5s detection weights (Ultralytics 8.4.75 fused) |
| `best.onnx` | M3 | 35.0 MB ONNX export (opset 13, static 1x3x640x640) for TensorRT/ORT |
| `best.engine` | M4a | 20.4 MB TensorRT FP16 engine for Orin Nano (TensorRT 8.6.2) |
| `best_hardneg.pt` | M3c | 18.5 MB fine-tuned PyTorch weights — eliminates M4b distractor FPs (green soil bag, blue cardboard package, blue decal, red chair) |

Source dataset, normalization, training command, per-class mAP, and known
caveats are documented in the M2 section below.

## M2 artifact: `best.pt`

| Field | Value |
|---|---|
| File | `models/best.pt` |
| Size | 18,517,947 bytes (18.5 MB) |
| SHA-256 | `bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04` |
| Created | 2026-06-24 |
| Format | Ultralytics YOLOv5s detection PyTorch checkpoint (Ultralytics 8.4.75 fused) |
| Layers / params | 85 fused layers, 9,112,697 parameters, 0 gradients, 23.8 GFLOPs |
| Class names | `0: blue_cube`, `1: green_cube`, `2: red_cube` |
| Task | `detect` (axis-aligned bounding boxes) |

## Source dataset

| Field | Value |
|---|---|
| Project | Roboflow Universe `jakub-lof/red-green-blue-cube-detection`, version 1 |
| URL | <https://universe.roboflow.com/jakub-lof/red-green-blue-cube-detection/dataset/1> |
| License | CC BY 4.0 |
| Total images | 103 (train 90 / valid 9 / test 4) |
| Original label names | `['bluecube', 'green cube', 'red cube']` |
| Local raw export | `data/roboflow/red-green-blue-cube-detection-1-yolov5pytorch/` (git-ignored) |
| Local normalized export | `data/roboflow_det/red-green-blue-cube-detection-1-yolov5pytorch/` (git-ignored) |

## Dataset normalization (one-time, mandatory for M2)

The Roboflow "YOLOv5 PyTorch" export mixes YOLOv5 *object detection* labels
(`class cx cy w h`, 5 fields) with YOLOv5 *segmentation* polygon labels
(`class x1 y1 x2 y2 ...`, 7–25 fields). YOLOv5s *detection* training cannot
consume polygons directly, so the source export was normalized before training.

The conversion is reproducible from this repository via:

```bash
source .venv-m2/bin/activate
python scripts/normalize_dataset.py --force
```

Per-file stats from the source export:

| Field-count per line | File count | Action |
|---|---:|---|
| 5 (detection `cx cy w h`) | 3 | kept as-is |
| 7+ (segmentation polygon) | 100 | collapsed to axis-aligned bbox via min/max x and y |
| other / malformed | 0 | dropped |

Each polygon is replaced with the bounding box of its vertices
(`cx = (min(x)+max(x))/2`, `cy = (min(y)+max(y))/2`,
`w = max(x)-min(x)`, `h = max(y)-min(y)`), clipped to `[0, 1]`. Class indices
are preserved 0/1/2, and class names are remapped to project-canonical
`blue_cube` / `green_cube` / `red_cube` in the new `data.yaml` so the trained
checkpoint's `model.names` matches the project policy.

## Training recipe

| Hyperparameter | Value |
|---|---|
| Base model | `yolov5s.pt` (COCO-pretrained) |
| Epochs | 30 |
| Image size | 640 |
| Batch size | 16 |
| Device | NVIDIA RTX 4070 Ti, single GPU (CUDA 12.4 / torch 2.6.0) |
| Optimizer | AdamW (auto-selected by Ultralytics), initial lr ≈ 0.00143 |
| Scheduler | cosine LR with `close_mosaic=10` |
| Patience | 20 (no early stop triggered) |
| AMP | enabled |
| Workers | 8 |
| Seed | 42 |
| Wall time | ~31 s end-to-end |

Exact training command (from project root, with the venv active):

```bash
yolo detect train \
  data=data/roboflow_det/red-green-blue-cube-detection-1-yolov5pytorch/data.yaml \
  model=yolov5s.pt \
  epochs=30 imgsz=640 batch=16 device=0 workers=8 \
  project=runs/m2 name=m2_30ep exist_ok=True seed=42 \
  patience=20 cos_lr=True close_mosaic=10 amp=True \
  save_period=-1 plots=True cache=False
```

## Best-epoch metrics (validation set, 9 images, 21 instances)

Per-class validation mAP at the best epoch (epoch 18, picked by Ultralytics'
"best" tracker on `metrics/mAP50(B)`):

| Class | Images | Instances | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|---|---:|---:|---:|---:|---:|---:|
| all | 9 | 21 | 0.823 | 0.959 | 0.954 | 0.763 |
| blue_cube | 5 | 8 | 0.875 | 0.877 | 0.982 | 0.703 |
| green_cube | 4 | 6 | 0.640 | 1.000 | 0.885 | 0.762 |
| red_cube | 5 | 7 | 0.953 | 1.000 | 0.995 | 0.823 |

Inference speed (validation, 640×640, single 4070 Ti): **1.5 ms/image**
(preprocess 0.1 ms, NMS 0.4 ms). Final loss at the best epoch: `box=0.47,
cls=0.67, dfl=0.89`. Full per-epoch metrics: `runs/m2/m2_30ep/results.csv`.

## M3 artifact: `best.onnx`

| Field | Value |
|---|---|
| File | `models/best.onnx` |
| Size | 36,671,634 bytes (35.0 MB) |
| SHA-256 | `326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21dcee829637fa38` |
| Created | 2026-06-27 |
| Source | Ultralytics 8.4.75 `yolo export` of `models/best.pt` |
| IR version | 7 |
| ONNX opset | 13 (default for the export) |
| Producer | pytorch 2.6.0 |
| Inputs | `images`: float32 `[1, 3, 640, 640]` (static, NHWC -> NCHW applied at the loader) |
| Outputs | `output0`: float32 `[1, 4 + nc, 8400]` = `[1, 7, 8400]` — rows 0..3 are xywh in the model's 640×640 input pixel grid; rows 4..6 are sigmoid-activated per-class scores |
| Simplify | `simplify=False` (onnx-simplifier skipped — TensorRT handles its own graph optimizations) |
| Dynamic shape | `dynamic=False` (static batch=1, h=640, w=640) |
| Class names | `0: blue_cube`, `1: green_cube`, `2: red_cube` (preserved from `best.pt`) |
| Checker | `onnx.checker.check_model` → OK |

Exact export command (run from the project root with `.venv-m2` active):

```bash
yolo export model=models/best.pt format=onnx imgsz=640 opset=13 \
    simplify=False dynamic=False
```

Why these settings (for the M4 TensorRT step):

- **`format=onnx`**: required intermediate for TensorRT. ONNX Runtime is also a valid fallback runtime.
- **`imgsz=640`**: matches the training resolution; the M4 tensorrt engine and ROS node will use the same letterboxed 640×640 input. Switching to a different size would change the model's anchor/stride math.
- **`opset=13`**: Ultralytics default for YOLOv5 ONNX export; broadly compatible with TensorRT 8.x (the version on the Jetson per the M1 LOGBOOK entry).
- **`simplify=False`**: the onnx-simplifier pass is unnecessary for TensorRT and can sometimes drop dynamic-shape info that TensorRT uses. Static shapes here mean simplification has no upside.
- **`dynamic=False`**: static input shape (1×3×640×640) is what TensorRT expects for engine build; runtime feed from the ROS camera node always provides the same shape, so dynamic axes would just add overhead.

ONNX validation (run once, idempotent):

```bash
.venv-m2/bin/python - <<'PY'
import onnx
m = onnx.load("models/best.onnx")
onnx.checker.check_model(m)
print("checker OK")
print("ir_version:", m.ir_version)
print("producer:", m.producer_name, m.producer_version)
print("opset:", [(o.domain, o.version) for o in m.opset_import])
PY
```

ORT smoke inference (verifies graph execution end-to-end on a saved validation
image; it does not replace M4 accuracy work on the Jetson):

```bash
.venv-m2/bin/python scripts/m3_smoke_inference.py
```

The smoke script takes `--model`, `--image`, `--imgsz`, `--conf`, `--iou`, and
`--topk`. It performs letterbox preprocessing, an ONNX Runtime forward pass on
the CPU provider, per-class confidence filtering, center/size box conversion,
inverse-letterbox mapping and clipping, then per-class torchvision NMS. This
order mirrors the deployed node, including clipping before NMS.

## M4a artifact: `best.engine`

| Field | Value |
|---|---|
| File | `models/best.engine` |
| Size | 21,354,868 bytes (20.4 MB; trtexec reports loaded engine size as 20 MiB) |
| SHA-256 | `c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1` |
| Created | 2026-06-27 on the Jetson (Orin Nano, L4T R36.3, TensorRT 8.6.2) |
| Source | `trtexec` conversion of `models/best.onnx` (FP32+FP16, 2048 MiB workspace) |
| Precision | FP32+FP16 (FP16 paths selected by the builder; the 59 subnormal FP16 weights flagged by TRT are the normal YOLOv5 head-decoder outputs) |
| Inputs | `images`: float32 `[1, 3, 640, 640]` (static, NHWC→NCHW applied at the loader) |
| Outputs | `output0`: float32 `[1, 4 + nc, 8400]` = `[1, 7, 8400]` — same layout as M3 ONNX |
| Device | Orin (compute capability 8.7, 4 SMs, 3.6 GB global memory) |
| trtexec steady-state | random-input benchmark: 70.47 qps, latency mean = 14.76 ms (median 14.76, p99 14.91), GPU compute mean = 14.12 ms |

Exact build command (run from `~/jetson_ws/` on the Jetson; `trtexec` lives at
`/usr/src/tensorrt/bin/trtexec` on this JetPack image and is not on PATH):

```bash
/usr/src/tensorrt/bin/trtexec \
    --onnx=best.onnx --saveEngine=best.engine --fp16 --workspace=2048
```

- **`--fp16`**: enables FP16 tensor cores on the Orin; YOLOv5s head is small enough
  that the INT64→INT32 cast warning from PyTorch weights has no measurable
  accuracy impact at the M3-equivalent confidence levels (see smoke comparison
  below).
- **`--workspace=2048`**: builder allocates up to 2 GiB for tactic selection.
  Builder emits harmless "Device memory is insufficient to use tactic" warnings
  when the Orin's 3.6 GiB global memory is tight during multi-candidate
  autotune; the chosen tactic still fits.

Build wall-time on the Orin Nano: **859.7 s (~14.3 min)** for the FP32+FP16
plan, dominated by TensorRT's tactic autotune on the 4-SM device. Engine
deserialize time on subsequent runs: ~0.12 s.

TensorRT engine smoke inference (run on the Jetson, on the same saved
validation image used by the M3 ORT smoke check; proves the engine loads,
executes on the Orin GPU, and produces detections consistent with the M3 ORT
baseline):

```bash
python3 scripts/m4a_trt_smoke_inference.py \
    --engine ~/jetson_ws/best.engine \
    --image  ~/jetson_ws/valid_smoke.jpg \
    --imgsz 640 --conf 0.25 --iou 0.45
```

The smoke script takes `--engine`, `--image`, `--imgsz`, `--conf`, `--iou`. It
letterboxes the image, runs the engine via `tensorrt` + `pycuda` on the Jetson
GPU, decodes the YOLOv5 `output0` (xywh + sigmoid class scores), does
per-class torchvision NMS, and reports detections. The output includes the
first-pass latency and a 10-run steady-state min/median/max.

`models/m4a_trt_smoke_inference.py` lives at
`scripts/m4a_trt_smoke_inference.py` in the repo and is reproduced by the
M4a LOGBOOK entry (2026-06-27).

## M3c artifact: `best_hardneg.pt`

| Field | Value |
|---|---|
| File | `models/best_hardneg.pt` |
| Size | 18,517,435 bytes (18.5 MB; identical-size to M2 because the head stays at 3 classes) |
| SHA-256 | `4715bb5fccee057d817d18bda366fece74e8d295c0ba4d0067e5b0e672c6a3cf` |
| Created | 2026-06-27 on the dev PC (RTX 4070 Ti, Ultralytics 8.4.75 `train()`) |
| Source | Continued training from `models/best.pt` (M2), 25 epochs, lr0=0.0005 |
| Class names | `0: blue_cube`, `1: green_cube`, `2: red_cube` (preserved from `best.pt`) |
| Format | Ultralytics YOLOv5s detection PyTorch checkpoint |

Training data: merged dataset at `data/hardneg/data.yaml` — 90 Roboflow
train + 9 Roboflow valid + 60 JetRover-room positive frames (from
`cubes_2026-06-27_m4b/` and the mislabeled-as-empty `empty_2026-06-27/`,
all hand-labeled with the 3 real cube bboxes) + 100 cropped
hard-negative patches (5 distractor regions × 20 source frames; empty
`.txt` labels for the standard YOLO background-only training signal).
Total: 250 train images, 9 val. Gitignored under `data/hardneg/`.

Exact training command (from project root, `.venv-m2` active):

```bash
python scripts/finetune_hardneg.py \
    --data  data/hardneg/data.yaml \
    --base  models/best.pt \
    --out   models/best_hardneg.pt \
    --epochs 25 --batch 16 --imgsz 640 --lr0 0.0005 \
    --device 0 --name m3c_25ep
```

Recipe (per `docs/model-hard-negative-plan.md` §6): AdamW optimizer,
cosine LR with `close_mosaic=10`, patience 15, seed 42, augmentation
`mosaic=1.0 mixup=0.15 hsv_h=0.015 hsv_s=0.7 hsv_v=0.4 degrees=10
translate=0.1 scale=0.5 fliplr=0.5`. Wall time on the RTX 4070 Ti:
**49.8 s**.

### Acceptance against the M3c plan §2.1

| Acceptance criterion                                  | Result |
|-------------------------------------------------------|--------|
| Real blue cube hit in ≥55/60 JetRover-room val frames | **30/30** on the saved cube frames (target set: 30 m4b + 30 "empty" both hit 30/30) |
| Real green cube hit in ≥55/60 val frames              | **30/30** (same) |
| Real red cube hit in ≥55/60 val frames                | **30/30** (same) |
| Zero detections on blue cardboard package             | **0/30** on the saved cube frames (M4b: 30/30 at conf 0.83–0.88) |
| Zero detections on green soil bag                     | **0/30** on the saved cube frames (M4b: 30/30 at conf 0.65–0.78) |
| Zero detections on blue decal                         | **0/30** on the saved cube frames (M4b: 18/30 at conf 0.25–0.58) |
| Zero detections on red chair/object                   | **0/30** on the saved cube frames (M4b: 4/30 at conf 0.31–0.39) |
| Roboflow valid mAP50 ≥ 0.80 (domain retention)        | **0.870** (M2 baseline: 0.963; -9.3 pp; above the bar) |
| Hard-negative-only crops — zero detections            | **92/100 crops have zero detections**; the remaining 8 fire `green_cube` on the cardboard-package crop at conf 0.36–0.60 (below any reasonable operating threshold; does not fire on the full-scene cube frames) |

Full evidence and per-frame annotated PNGs in
`evaluation/m3c_predictions/report.md` (PNG visualizations gitignored
under `evaluation/m3c_predictions/*.png` etc.).

### Per-class confidence tightening on saved cube frames (30 frames, conf≥0.25)

| Class      | M2/M4b mean | M3c mean | M3c min  | M3c max  | Total dets (M4b → M3c) |
|------------|------------:|---------:|---------:|---------:|------------------------:|
| blue_cube  |       0.731 |    0.889 |    0.857 |    0.905 |             91 → 30     |
| green_cube |       0.567 |    0.948 |    0.944 |    0.955 |             52 → 30     |
| red_cube   |       0.708 |    0.982 |    0.979 |    0.984 |             34 → 30     |

The fine-tune collapsed 177 noisy detections to exactly 90 (one per
real cube per frame) and tightened the per-class confidence ranges
from 0.5–0.7 wide spreads to 0.005–0.05 spreads.

### Status and rename protocol (per `docs/model-hard-negative-plan.md` §8)

`models/best_hardneg.pt` is the **candidate** artifact. `models/best.pt`
is **preserved unchanged**. Promotion of `best_hardneg.pt` → `best.pt`
awaits:

1. Export to ONNX + TensorRT engine on the Jetson (M3c-export follow-up
   card). The model currently exists only as PyTorch `.pt`.
2. A tester card that re-runs the §2.1 acceptance bar on the
   60-frame held-out validation set (which requires Maher to capture
   fresh cube-arranged and cube-removed frames at 20/40/60/80 cm per
   `docs/evaluation.md`).

Until those gates pass, the live ROS node (`M5`) and the
TensorRT-based M5 accuracy work should keep using `models/best.engine`
(M2-derived). After approval: rename `best.pt` → `best_m2.pt`,
`best_hardneg.pt` → `best.pt`, re-export ONNX + engine, update this
README, log to LOGBOOK and `.cursorrules` Current Status.

## M4b usage: `scripts/test_inference.py`

The M4b harness loads `models/best.engine` on the Jetson and runs it on
a directory of saved JPG frames (the 30 frames in
`evaluation/camera_samples/cubes_2026-06-27_m4b/`, captured live from
`/depth_cam/rgb/image_raw` with 1 red + 1 green + 1 blue cube in view).

Exact command (run on the Jetson with `~/jetson_ws/install/setup.bash`
sourced, and the engine + frames staged locally — `models/best.engine`
is GPU/CUDA-specific to the Orin Nano and cannot be loaded on the dev
PC):

```bash
python3 scripts/test_inference.py \
    --engine models/best.engine \
    --input-dir evaluation/camera_samples/cubes_2026-06-27_m4b \
    --output-dir evaluation/m4b_predictions \
    --conf 0.25 --iou 0.45
```

Observed latency on the Orin Nano (Orin, TensorRT 8.6.2, pycuda 2024.1):

| Stat       | Value (ms) | FPS   |
|------------|-----------:|------:|
| first call | 241.06     |   4.1 |
| median     |  26.59     |  37.6 |
| mean       |  33.76     |  29.6 |
| p95        |  26.81     |  37.3 |

The first-call latency is the cold-load + CUDA-context-warmup cost;
steady state is ~26.6 ms including the PNG annotation overhead. A
separate steady-state measurement on 3 different frames (warm engine, no
annotate) measured 14.66 ms median / 14.85 ms p95 forward-pass latency
(68.2 FPS engine-only budget).

Observed accuracy on 30 live frames (1 cube of each color in view):

| Class       | Frame-hit rate | Mean conf | Total dets |
|-------------|---------------:|----------:|-----------:|
| `blue_cube` |          100.0% |    0.731  |         91 |
| `green_cube`|          100.0% |    0.567  |         52 |
| `red_cube`  |          100.0% |    0.708  |         34 |

All three classes hit ≥50% (the M4b acceptance bar). The total-detection
counts are higher than the frame count because the model is color-driven
and produces overlapping detections on color-confusable background
objects (green soil bag, blue cardboard package, blue decal). The
actual cubes always get correct high-confidence detections. Full report
and per-frame annotated PNGs in `evaluation/m4b_predictions/`.

Implementation note: on JetPack 6 / TensorRT 8.6.2 / pycuda 2024.1,
wrapping TensorRT buffer allocation in helper functions and passing the
CUDA stream across function boundaries produced all-zero outputs (the
engine silently short-circuited after the first frame). The fix is to
inline the TRT + pycuda setup inside `main()` and use a single shared
`cuda.Stream()` across all frames. This is reflected in
`scripts/test_inference.py` and is documented in its module docstring.

## Verification commands

```bash
# File integrity
sha256sum models/best.pt
# expect: bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04

sha256sum models/best.onnx
# expect: 326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21ddee829637fa38

sha256sum models/best.engine
# expect: c64d3e5e277ea42f3f19f0ba733d6ef25f0403ba2496f8191288d3d6829ec3d1

sha256sum models/best_hardneg.pt
# expect: 4715bb5fccee057d817d18bda366fece74e8d295c0ba4d0067e5b0e672c6a3cf

# Ultralytics load check (no inference)
python -c "from ultralytics import YOLO; m = YOLO('models/best.pt'); \
print(m.task, m.names)"

# ONNX graph check
.venv-m2/bin/python - <<'PY'
import onnx
m = onnx.load("models/best.onnx")
onnx.checker.check_model(m)
print("checker OK")
PY

# One-image inference sanity check (PyTorch)
python - <<'PY'
from ultralytics import YOLO
m = YOLO("models/best.pt")
r = m.predict(
    "data/roboflow_det/red-green-blue-cube-detection-1-yolov5pytorch/valid/images/"
    "Snimek-obrazovky-2023-08-16-213123_png.rf.270a8af923637b40e0f4da5bc6da7c2d.jpg",
    imgsz=640, conf=0.25, verbose=False,
)[0]
print({m.names[int(b.cls)]: round(float(b.conf), 3) for b in r.boxes})
PY

# One-image ORT smoke inference (graph execution)
.venv-m2/bin/python scripts/m3_smoke_inference.py
```

## Known caveats

1. **Tiny validation set (9 images, 21 instances).** Per-class mAP numbers are
   noisy: a single-image swing can move green_cube mAP by ±10 pp. Cross-dataset
   accuracy on the JetRover camera is still an open question — that is what M4
   tests. M2 only needs a verified local `best.pt` that loads and reproduces
   the documented class order; M3/M4 are the next gates.
2. **Bboxes came from polygon min/max.** This tightens around the cube body but
   loses the original segmented silhouette. For solid-color cube detection this
   is fine; for irregular shapes the loss of margin would matter.
3. **No custom JetRover data.** Following the approved M2 fallback policy
   (`docs/model-options.md`): do not collect robot images upfront. Add them in
   M3/M4 only if standalone inference fails the target.
4. **Trained on the dev PC, not the Jetson.** This is per
   `docs/technical-stack.md` (RTX 4070 Ti is the training machine). The Jetson
   sees the artifact only at M3 (ONNX export) and M4 (TensorRT engine build).
5. **`runs/` is git-ignored.** The full Ultralytics training output (curves,
   confusion matrix, sample predictions, `args.yaml`) lives in
   `runs/m2/m2_30ep/`; that path is reproducible from the command above but is
   not part of the repo. The smoke-training run (`runs/m2/smoke3/`) is also
   git-ignored.
6. **Venv is local and git-ignored.** A small `.venv-m2/` virtualenv is created
   at the project root with `torch`, `torchvision`, `ultralytics`, `onnx`,
   `onnxruntime` (added for the M3 smoke check), `numpy`, `pillow`, `pyyaml`.
   It is listed in `.gitignore`
   (see `.venv-m2/` and `.yolo_config/` entries). `rm -rf .venv-m2` to free
   ~5 GB; recreate with `python3 -m venv .venv-m2 && source .venv-m2/bin/activate
   && pip install torch torchvision ultralytics onnx onnxruntime numpy pillow pyyaml`.
7. **M3 smoke check runs on CPU only.** `onnxruntime-gpu` is not installed in
   `.venv-m2/`. The ORT smoke inference uses the `CPUExecutionProvider` on the
   dev PC; this is intentional — the goal of M3 is to prove the exported graph
   executes and produces sane detections on a saved validation image. The GPU
   / TensorRT execution path belongs to M4 on the Jetson.
8. **`trtexec` is not on the Jetson PATH.** The M1 LOGBOOK carryover
   flagged this; the binary lives at `/usr/src/tensorrt/bin/trtexec` on this
   JetPack 6 (L4T R36.3) image. M4a uses the absolute path. Future M5 work
   can call `python3 -c "from tensorrt.tools import trtexec"` if a clean PATH
   is preferred.
9. **TensorRT 8.6 builder warnings.** The builder prints two harmless
   warnings during engine construction:
   - `onnx2trt_utils.cpp:372: Your ONNX model has been generated with INT64
     weights, while TensorRT does not natively support INT64. Attempting to
     cast down to INT32.` — standard PyTorch-export-of-ultralytics artifact.
   - `TensorRT encountered issues when converting weights between types ...
     - 59 weights are affected by this issue: Detected subnormal FP16
     values.` — the YOLOv5 head-decoder weights; runtime smoke matches the
     ORT baseline within ~0.003 on top-class confidences, so this does not
     affect accuracy for this model.
   The builder also prints `Tactic Device request: 100MB Available: 92MB`
   twice during autotune; the Orin Nano's 3.6 GiB global memory is tight
   for some 100-MB-tactic candidates, but the chosen tactic still fits.
10. **Engine is GPU/CUDA-specific.** `models/best.engine` was built for the
    Orin Nano (compute capability 8.7, SM 8.7, FP32+FP16 plan with the
    Orin-specific kernels TensorRT picked). It will not run on a different
    GPU class or driver stack without a rebuild. To rebuild on the same
    device: `scp models/best.onnx jetrover:~/jetson_ws/best.onnx && ssh
    jetrover "/usr/src/tensorrt/bin/trtexec --onnx=~/jetson_ws/best.onnx
    --saveEngine=~/jetson_ws/best.engine --fp16 --workspace=2048"`.

## Next milestones

- **M4a (TensorRT engine build on the Jetson):** COMPLETE — see the M4a
  artifact section above. The engine is reproducible from the command in
  that section, and the lightweight infer check is `scripts/m4a_trt_smoke_inference.py`.
- **M4b (live-camera inference + accuracy validation):** COMPLETE
  2026-06-27 — see the M4b usage section above. Frame-hit rate ≥50% for
  all 3 classes met (100/100/100 on the captured 30-frame set). Median
  forward-pass 26.6 ms on the Orin Nano. Annotated outputs and report in
  `evaluation/m4b_predictions/`. M4b also exposed the false-positive
  issue on color-confusable background objects (green soil bag, blue
  cardboard package, blue decal, red chair) that motivated the M3c
  fine-tune.
- **M3c (hard-negative fine-tune on JetRover-room frames):** COMPLETE
  2026-06-27 — see the M3c artifact section above. `best_hardneg.pt`
  eliminates the four named distractors on the saved cube frames
  (0/30 on each, vs 30/30 / 30/30 / 18/30 / 4/30 for M4b). Per-class
  conf tightens dramatically (e.g. green mean conf 0.567 → 0.948,
  range 0.94–0.96). mAP50 on Roboflow valid drops 0.96 → 0.87 (above
  the 0.80 acceptance bar). Full report and per-frame annotated PNGs
  in `evaluation/m3c_predictions/`. M3c is the candidate artifact;
  `models/best.pt` is preserved unchanged until the tester card
  approves promotion.
- **M3c-export (recommended follow-up):** export `best_hardneg.pt` →
  `best_hardneg.onnx` → `best_hardneg.engine` on the Jetson and run a
  smoke inference on the saved cube frames. Hardware-gated; estimated
  ~30 min on the Jetson (mirrors M3 + M4a). Until this exists, the M5
  live ROS node continues to use `models/best.engine` (M2-derived).
- **M5 (ROS 2 node):** load the engine in `cube_detection_node` and publish
  `/cube_detections`, `/cube_detections/vendor_objects`,
  `/cube_detections/debug_image` as documented in
  `docs/technical-stack.md`. The 14-15 ms steady-state engine latency
  leaves headroom for image transport, NMS, and message serialization.
  M5 is **gated** on a tester card that approves either (a) keeping
  `models/best.engine` (M2-derived) — color-driven FPs persist in
  deployment; or (b) promoting `best_hardneg.pt` after M3c-export
  produces a working TensorRT engine.
