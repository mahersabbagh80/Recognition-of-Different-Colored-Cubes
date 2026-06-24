# models/best.pt — M2 trained YOLOv5s weights

This directory holds the M2 model artifact. The single deliverable is `best.pt`
(18.5 MB PyTorch YOLOv5s detection weights). It is git-ignored along with
everything else under `models/` except this `README.md` and `.gitkeep`.

## Artifact

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

## Verification commands

```bash
# File integrity
sha256sum models/best.pt
# expect: bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04

# Ultralytics load check (no inference)
python -c "from ultralytics import YOLO; m = YOLO('models/best.pt'); \
print(m.task, m.names)"

# One-image inference sanity check
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
6. **Venv is local.** A small `.venv-m2/` virtualenv is created at the project
   root with `torch`, `torchvision`, `ultralytics`, `onnx`, `numpy`, `pillow`,
   `pyyaml`. It is **not** in `.gitignore` — add it if you don't want it
   tracked, or `rm -rf .venv-m2` to free ~5 GB.

## Next milestones

- **M3 (ONNX export):** `yolo export model=models/best.pt format=onnx imgsz=640`
  → `models/best.onnx`.
- **M4 (TensorRT engine on Jetson):** convert `best.onnx` → `models/best.engine`
  with FP16 on the Orin Nano and run `scripts/test_inference.py` against
  `/depth_cam/rgb/image_raw` snapshots.
- **M5 (ROS 2 node):** load the engine in `cube_detection_node` and publish
  `/cube_detections`, `/cube_detections/vendor_objects`,
  `/cube_detections/debug_image` as documented in
  `docs/technical-stack.md`.
