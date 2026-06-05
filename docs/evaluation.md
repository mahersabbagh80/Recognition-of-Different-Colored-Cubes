# Evaluation

> **Status:** Placeholder — to be completed in Milestone 6.

---

## Test Protocol

Structured 50-frame evaluation with cubes placed at known distances within the 20–80 cm operating range.

### Setup

1. Place one cube of each color (`red_cube`, `green_cube`, `blue_cube`) in the camera field of view
2. Vary distance: 20 cm, 40 cm, 60 cm, 80 cm
3. Capture 50 frames per test run using `evaluation/evaluate.py`
4. Record ground-truth labels for each frame manually

### Metrics

| Metric | Target | Result |
|--------|--------|--------|
| Color classification accuracy | ≥ 80% | TBD |
| Inference frame rate | ≥ 5 fps | TBD |
| Operating distance (min) | 20 cm | TBD |
| Operating distance (max) | 80 cm | TBD |

### Per-Class Breakdown

| Class | Correct | Total | Accuracy |
|-------|---------|-------|----------|
| `red_cube` | — | — | — |
| `green_cube` | — | — | — |
| `blue_cube` | — | — | — |

---

## Results

_To be filled after Milestone 6._

### Environment

- Jetson Orin Nano, JetPack version: TBD
- Model: YOLOv5s, TensorRT FP16
- Input resolution: TBD
- Confidence threshold: TBD

### Notes

_Record failure cases, lighting conditions, and distance-specific observations here._
