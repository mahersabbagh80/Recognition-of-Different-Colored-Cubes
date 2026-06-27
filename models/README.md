# models/ — YOLOv5s weights for the cube-detection pipeline

This directory holds the trained detection artifacts. Both files are git-ignored
along with everything else under `models/` except this `README.md` and `.gitkeep`.

| File | Milestone | Purpose |
|---|---|---|
| `best.pt` | M2 | 18.5 MB PyTorch YOLOv5s detection weights (Ultralytics 8.4.75 fused) |
| `best.onnx` | M3 | 35.0 MB ONNX export (opset 13, static 1x3x640x640) for TensorRT/ORT |

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
the CPU provider, per-class confidence filtering, torchvision NMS, and undoes
the letterbox to map boxes back into the original image frame.

## Verification commands

```bash
# File integrity
sha256sum models/best.pt
# expect: bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04

sha256sum models/best.onnx
# expect: 326d5d62ebf7586f02a9fcacf36e1890f1db8b99953cfcef21dcee829637fa38

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

## Next milestones

- **M3 (ONNX export):** COMPLETE — see the M3 artifact section above. Run
  `yolo export model=models/best.pt format=onnx imgsz=640 opset=13
  simplify=False dynamic=False` from the project root (with `.venv-m2` active)
  to reproduce `models/best.onnx`. Validate with
  `onnx.checker.check_model` and run `scripts/m3_smoke_inference.py` for an
  ORT forward-pass sanity check on a saved validation image.
- **M4 (TensorRT engine on Jetson):** convert `best.onnx` → `models/best.engine`
  with FP16 on the Orin Nano and run `scripts/test_inference.py` against
  `/depth_cam/rgb/image_raw` snapshots.
- **M5 (ROS 2 node):** load the engine in `cube_detection_node` and publish
  `/cube_detections`, `/cube_detections/vendor_objects`,
  `/cube_detections/debug_image` as documented in
  `docs/technical-stack.md`.
