# M2 — What the implementer did, and why it matters for M3+

> A reference document. Anchored to: kanban cards `t_83eec93d` (M2 Roboflow raw weights, done), `t_f6d3380d` (M2 fallback training, blocked — review-required), `t_4e0c409b` (M2 docs wording, done); review card `t_6fffb30b` (tester, todo, not started).
> Read time: ~10 min. Return here whenever M3–M5 work touches a question about the model itself.

---

## 1. The four-act story (chronological)

| When (CEST) | What | Card | Outcome |
|---|---|---|---|
| 2026-06-24 01:28 → 01:34 | Implementer tries to download raw `best.pt` from Roboflow Universe. No API key, no weights endpoint, Cloudflare 401s. | `t_83eec93d` | `done` — path ruled out, not M2-complete. |
| 2026-06-24 01:46 | You (Maher) confirm manually that no weights download is visible in the Roboflow UI. | comment on `t_83eec93d` | Confirms the easy path is closed for this account. |
| 2026-06-24 01:48 → 02:08 | Implementer tries Plan B: download the *dataset* (YOLOv5 export) and fine-tune. Hits the same auth wall. | `t_f6d3380d` run #20 | `blocked` — needs `ROBOFLOW_API_KEY` in worker env, or a manual dataset placement. |
| 2026-06-24 02:36 | You place the dataset manually at `data/roboflow/red-green-blue-cube-detection-1-yolov5pytorch/`. | comment on `t_f6d3380d` | Unblocks training. |
| 2026-06-24 02:37 → 04:02 | Implementer attempts to train. **Nine failed dispatcher runs** between 02:37 and 04:02, all with `worker exited cleanly (rc=0) without calling kanban_complete or kanban_block — protocol violation`. The training may have been succeeding but the worker wasn't phoning the kanban. | `t_f6d3380d` runs #21–#28 | `crashed` × 8 (dispatcher interpretation; work itself may have been fine). |
| 2026-06-24 04:02 → 04:16 | Run #29 succeeds: training completes in ~31 s on the RTX 4070 Ti, artifact and metadata produced. | `t_f6d3380d` run #29 | `blocked` — reason is `review-required`, not a real blocker. **This is the review request.** |

## 2. The artifact (`models/best.pt`)

| Field | Value |
|---|---|
| Path | `src/Recognition-of-Different-Colored-Cubes/models/best.pt` |
| Size | 18,517,947 bytes (18.5 MB) |
| SHA-256 | `bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04` |
| Class map | `0: blue_cube`, `1: green_cube`, `2: red_cube` |
| Task | `detect` (axis-aligned bounding boxes) |
| Parameters | 9,123,353 |
| Loads with | `ultralytics.YOLO("models/best.pt")` and `torch.load(...)` |
| Git | gitignored (`.gitignore` allows `models/README.md` only) |

## 3. How it was trained

- **Base:** `yolov5s.pt` (COCO-pretrained, auto-downloaded by Ultralytics).
- **Dataset:** Roboflow Universe `jakub-lof/red-green-blue-cube-detection/1` (CC BY 4.0, 103 images, 90/9/4 train/valid/test split). Placed manually at `data/roboflow/red-green-blue-cube-detection-1-yolov5pytorch/`.
- **Hyperparameters:** 30 epochs, 640×640, batch 16, AdamW (auto), cosine LR, `close_mosaic=10`, patience 20, AMP on, seed 42.
- **Wall time:** ~31 s on the RTX 4070 Ti.
- **Best epoch:** 18.
- **Validation metrics:**
  - mAP@0.5 = **0.954**
  - mAP@0.5:0.95 = 0.763
  - Per-class mAP@0.5: blue 0.982 / green 0.885 / red 0.995
- **Inference speed:** 1.5 ms/image at 640×640 on the 4070 Ti.

## 4. The non-obvious finding: the dataset was mixed

The Roboflow "YOLOv5 PyTorch" export contained **two label formats** in the same dataset:

| Format | Fields per line | File count |
|---|---|---|
| Object detection | `class cx cy w h` (5 fields) | 3 |
| Polygon segmentation | `class x1 y1 x2 y2 … xn yn` (7–25 fields) | 100 |

YOLOv5s *detection* training only reads 5-field lines. Polygon lines break the loader. The implementer wrote `scripts/normalize_dataset.py` (5.5 KB, tracked, idempotent) to:

1. Convert each polygon to an axis-aligned bbox:
   - `cx = (min_x + max_x) / 2`, `w = max_x - min_x` (same for y/h)
   - Clipped to [0, 1]
2. Remap class names to project-canonical form: `bluecube`, `green cube`, `red cube` → `blue_cube`, `green_cube`, `red_cube`.
3. Write the cleaned dataset to `data/roboflow_det/...` (gitignored, regenerable).

Source: 3 detection + 100 polygon files → 103 normalized detection files. **The mAP@0.5 = 0.954 figure comes from the normalized dataset, not the raw Roboflow export.** If `yolo train` had been run directly on the raw export, training would have either crashed or silently ignored ~97% of the data.

## 5. The verification the implementer ran

- `ls -la`, `file`, `sha256sum` on `models/best.pt`.
- `ultralytics.YOLO("models/best.pt").task == "detect"`, `.names == {0: 'blue_cube', 1: 'green_cube', 2: 'red_cube'}`.
- `torch.load(...)` reads the raw checkpoint; 9,123,353 parameters.
- One-image inference on a `valid/images/...jpg` (all 3 classes present in the labels) → 8 detections, confidences 0.32–0.96, all three class names correct.
- `git diff --check` clean.
- `git check-ignore` confirms `data/roboflow/`, `data/roboflow_det/`, `runs/`, `models/best.pt`, `.venv-m2/`, stray `*.pt` are all properly ignored.

## 6. Scope discipline (what the implementer explicitly did NOT do)

- Did NOT export ONNX → M3.
- Did NOT convert TensorRT → M4.
- Did NOT integrate inference into ROS → M5.
- Did NOT evaluate on robot camera → M6.
- Did NOT modify `src/vendor/`.

This matches `.cursorrules` ("Implement incrementally — one step at a time. Never build ahead of the current milestone.").

## 7. What was changed in the repo (NOT committed — manual commits per `.cursorrules`)

```
M  .cursorrules                       (M2 status updated)
M  .gitignore                         (added .venv-m2/, .yolo_config/, data/roboflow/, data/roboflow_det/, *.pt; allowed models/README.md)
M  docs/LOGBOOK.md                    (new 2026-06-24 M2 training entry)
M  docs/milestones.md                 (M2 checkboxes all [x], verdict line)
M  docs/model-options.md              (added "Fallback path: EXECUTED on 2026-06-24" block)
?? models/best.pt                     (18.5 MB, gitignored)
?? models/README.md                   (7 KB, tracked — artifact metadata)
?? scripts/normalize_dataset.py       (5.5 KB, tracked — polygon→bbox + class name remap)
```

## 8. Side artifacts (not in repo, regenerable)

- `.venv-m2/` (~5.9 GB) — local training venv (torch+ultralytics+onnx).
- `runs/m2/m2_30ep/` (~79 MB) — full Ultralytics run output (results.csv, PR curve, confusion matrix, sample predictions, args.yaml).
- `data/roboflow_det/...` (~9 MB) — normalized YOLOv5 detection dataset.

## 9. The two review questions, in order

The implementer's handoff names two things worth human attention:

1. **Approve `models/best.pt` as the M2 deliverable.** Load it, run a quick inference, confirm classes and confidences look right. The `models/README.md` has a one-image sanity-check command.
2. **Approve `scripts/normalize_dataset.py`.** 5.5 KB, idempotent. Verify the polygon→bbox math is what you want. The only non-trivial code he wrote.

Plus a third question that nobody asked but matters: **0.954 mAP@0.5 is computed on 9 validation images.** That's noisy. The project plan accepts this and defers the "fine-tune with robot camera images" branch until M4 standalone inference proves out. So no action needed now, but it's the first thing to revisit if M4 accuracy is poor.

## 10. The kanban dispatcher quirk (worth knowing, not worth a learning record)

If a card ever shows repeated `crashed` runs with the error `worker exited cleanly (rc=0) without calling kanban_complete or kanban_block — protocol violation`, the work itself may have succeeded — the worker just didn't signal the kanban on exit. Inspect the actual work (file system, side artifacts) before retrying. The orchestrator owns the protocol; the implementer worked around it by retrying until the timing landed.

## 11. Implications for M3–M5 (cheat sheet)

When you start M3 (ONNX export), the things from this story that matter:

- **Class names:** `blue_cube`, `green_cube`, `red_cube` (the project-canonical form, already in the model). The normalize script is the reason the model uses these names and not Roboflow's exported `bluecube` / `green cube` / `red cube`.
- **Input shape:** 640×640. The model was trained at this resolution; `yolo export ... imgsz=640` will preserve it.
- **Confidence threshold:** 0.5 is the current default in `cube_detection_node.py`. The 8-detection test image had confidences 0.32–0.96, so 0.5 will keep most true positives. If you see misses on dim cubes, lowering to 0.3 might recover them — but it'll also keep more false positives, so check the per-class mAP first (green is the weakest at 0.885).
- **Dataset small-print:** 103 images is small. If M4 standalone inference on robot camera is poor, the next step is "add robot camera images" per the M2 fallback plan, not "retrain with different hyperparameters."

When you start M5 (ROS integration):

- The `CubeDetection` dataclass in `cube_detection_node.py` already has the right shape (`class_name: str`, `score: float`, `box: Sequence[float]`). The post-NMS conversion from the raw `(1, 25200, 8)` tensor to this dataclass is the function you'll write — Ultralytics' `model.predict()` does it for you on the dev PC; on the Jetson under TensorRT, you do it by hand.
