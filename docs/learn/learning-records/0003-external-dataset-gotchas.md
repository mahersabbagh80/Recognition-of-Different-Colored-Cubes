# External Roboflow dataset gotchas (relevant to this project)

The Roboflow "YOLOv5 PyTorch" export used for M2 (`jakub-lof/red-green-blue-cube-detection/1`) had two non-obvious quirks that, if you missed them, would have made the training silently fail or use a fraction of the data:

1. **Mixed label formats in one dataset.** The export combined object-detection labels (5 fields: `class cx cy w h`) with polygon segmentation labels (7–25 fields: `class x1 y1 x2 y2 …`). YOLOv5s *detection* training can only read 5-field lines. A naive `yolo train data=.../data.yaml` would have either crashed or silently ignored ~97% of the data. The implementer caught this in M2 by inspecting label files; the fix is in `scripts/normalize_dataset.py` (polygon→bbox + class-name remap).
2. **Class names were not project-canonical.** Roboflow exported `bluecube`, `green cube`, `red cube` (no underscores, one had a space). The project-canonical form is `blue_cube`, `green_cube`, `red_cube` (per `.cursorrules` Hard Constraints). The normalize script also handles this remap.

**Implications for future sessions:**
- When working with a new external dataset (any Roboflow project, not just this one), inspect a few label files *before* training. A `wc -l` per file plus a `head -1` showing field count is enough. Files with >5 fields are polygons, not detection labels.
- If you ever see "0 detections" on a dataset that visually has objects, the first thing to check is the label format — not the model.
- The class-name mismatch (`green cube` vs `green_cube`) will also show up in M3 ONNX export logs and M4 TensorRT engine metadata. If class names look wrong in any downstream artifact, the source is the original Roboflow export, not the model.

**Evidence:** M2 implementer handoff, kanban `t_f6d3380d` run #29 (2026-06-24). mAP@0.5 = 0.954 was achieved on the normalized dataset; the raw Roboflow export would not have produced that number. The normalize script is at `scripts/normalize_dataset.py` and is idempotent — safe to re-run on a fresh download.

**Status:** active.
