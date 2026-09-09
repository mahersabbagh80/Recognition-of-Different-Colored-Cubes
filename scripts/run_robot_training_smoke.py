#!/usr/bin/env python3
"""Verify the intended checkpoint and run a bounded, three-epoch data check."""

import hashlib
import json
import math
from pathlib import Path

import torch
import ultralytics
from ultralytics import YOLO
from ultralytics.nn.tasks import DetectionModel


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evaluation/robot_dataset_2026-09-09"
CHECKPOINT = ROOT / "models/pretrained/yolov5su.pt"
DATA = ROOT / "evaluation/results/robot_training_2026-09-09/data.yaml"
RUNS = ROOT / "runs/robot_2026-09-09"
RUN_NAME = "smoke_3ep"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if (RUNS / RUN_NAME).exists():
        raise FileExistsError("Smoke run exists; inspect it rather than overwrite")
    assert torch.cuda.is_available(), "This run requires confirmed CUDA access"
    split = json.loads((EVIDENCE / "development_split.json").read_text())
    assert sha(EVIDENCE / "human_review.json") == split["review_sha256"]
    data_root = Path(split["output_root"])
    for frame in split["frames"]:
        assert sha(data_root / frame["image"]) == frame["sha256"]
        lines = (data_root / frame["label"]).read_text().splitlines()
        assert len(lines) == len(frame["objects"])
    torch.set_num_threads(4)
    torch.manual_seed(42)
    model = YOLO(str(CHECKPOINT))
    assert model.task == "detect"
    assert len(model.names) == 80, "Expected general COCO-pretrained checkpoint"
    assert "yolov5" in str(model.model.yaml.get("yaml_file", ""))
    # This official checkpoint encodes small-model multipliers directly,
    # rather than the newer shorthand `scale: s` configuration field.
    assert model.model.yaml.get("depth_multiple") == 0.33
    assert model.model.yaml.get("width_multiple") == 0.5
    # Confirm adapted inference output before allocating a training run.
    adapted = DetectionModel(model.model.yaml, ch=3, nc=3, verbose=False)
    adapted.load(model.model)
    adapted.eval()
    with torch.inference_mode():
        result = adapted(torch.zeros(1, 3, 640, 640))
        predictions = result[0] if isinstance(result, tuple) else result
    assert list(predictions.shape) == [1, 7, 8400], predictions.shape
    assert torch.isfinite(predictions).all()
    preflight = {
        "torch": torch.__version__, "ultralytics": ultralytics.__version__,
        "gpu": torch.cuda.get_device_name(0),
        "checkpoint": str(CHECKPOINT), "checkpoint_sha256": sha(CHECKPOINT),
        "checkpoint_source": "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolov5su.pt",
        "model_yaml": model.model.yaml,
        "original_classes": len(model.names),
        "adapted_output_shape": list(predictions.shape),
        "scope": "PyTorch shape compatibility only; no ONNX/TensorRT/robot parity claim",
        "dataset_manifest_sha256": sha(EVIDENCE / "development_split.json"),
    }
    (EVIDENCE / "training_preflight.json").write_text(json.dumps(preflight, indent=2) + "\n")
    del adapted, result, predictions
    settings = dict(
        data=str(DATA), epochs=3, imgsz=640, batch=4, device=0, workers=0,
        project=str(RUNS), name=RUN_NAME, exist_ok=False, seed=42,
        deterministic=True, optimizer="AdamW", lr0=0.001, lrf=0.1,
        warmup_epochs=0.5, patience=10, amp=False, pretrained=True,
        hsv_h=0.0, hsv_s=0.0, hsv_v=0.1, mosaic=0.0, mixup=0.0,
        scale=0.1, translate=0.05, fliplr=0.5, flipud=0.0,
        close_mosaic=0, cache=False, plots=True, save=True, val=True,
    )
    (EVIDENCE / "smoke_requested_settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    metrics = model.train(**settings)
    best = RUNS / RUN_NAME / "weights/best.pt"
    assert best.is_file()
    trained = YOLO(str(best))
    assert trained.names == {0: "blue_cube", 1: "green_cube", 2: "red_cube"}
    reported = {k: float(v) for k, v in metrics.results_dict.items()}
    assert all(math.isfinite(v) for v in reported.values())
    summary = {
        "status": "training smoke completed", "epochs": 3,
        "run": str(RUNS / RUN_NAME), "checkpoint": str(best),
        "checkpoint_sha256": sha(best), "class_names": trained.names,
        "validation_metrics": reported,
        "limitations": "Four same-session validation frames from two setups; pipeline smoke only, not final detector acceptance or robot performance",
    }
    (EVIDENCE / "smoke_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
