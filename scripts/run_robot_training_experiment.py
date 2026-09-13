#!/usr/bin/env python3
"""Bounded own-data experiment with explicit small-dataset optimizer settings."""
import json
import math
import csv
from pathlib import Path
import yaml
from datetime import datetime
import torch
from ultralytics import YOLO
from run_robot_training_smoke import ROOT, CHECKPOINT, sha

EVIDENCE = ROOT / "evaluation/robot_dataset_2026-09-12"
DATA = ROOT / "evaluation/results/robot_training_2026-09-12/data.yaml"
RUNS = ROOT / "runs/robot_2026-09-12"

def reserve_run_directory(parent, timestamp=None):
    """Atomically reserve a fresh directory, even for simultaneous launches."""
    stamp = timestamp or datetime.now().astimezone().strftime('%Y%m%d_%H%M%S%z')
    base = f'experiment_60ep_{stamp}'
    parent.mkdir(parents=True, exist_ok=True)
    suffix = 0
    while True:
        name = base if suffix == 0 else f'{base}_{suffix}'
        run = parent / name
        try:
            run.mkdir()  # No exist_ok: an existing run is never reused.
            return run
        except FileExistsError:
            suffix += 1


def main():
    assert torch.cuda.is_available()
    assert sha(CHECKPOINT) == '054272ddbbb3035cea7ff6b97e5becea63d2cc57a4f06a2a8133f4d1a56e74ed'
    split = json.loads((EVIDENCE / 'development_split.json').read_text())
    assert sha(EVIDENCE / 'human_review.json') == split['review_sha256']
    config = yaml.safe_load(DATA.read_text())
    data_root = Path(config['path'])
    image_folder = data_root / config['train']
    approved = {Path(frame['image']).name: frame for frame in split['frames']}
    assert len(approved) == len(split['frames']), "Duplicate approved filenames"
    assert image_folder.is_dir(), "Training image folder is missing"
    image_paths = sorted(image_folder.glob('*.jpg'))
    assert image_paths, "No training images found"
    for image_path in image_paths:
        assert image_path.name in approved, f"Unapproved image: {image_path.name}"
        frame = approved[image_path.name]
        assert sha(image_path) == frame['sha256']
        label_path = data_root / 'labels/train' / (image_path.stem + '.txt')
        rows = label_path.read_text().splitlines()
        assert len(rows) == len(frame['objects'])
        for row, obj in zip(rows, frame['objects']):
            values = list(map(float, row.split()))
            assert len(values) == 5 and all(math.isfinite(v) for v in values)
    torch.set_num_threads(4)
    run = reserve_run_directory(RUNS)
    print(f"New experiment directory: {run}", flush=True)
    settings = dict(data=str(DATA), epochs=60, imgsz=640, batch=4, nbs=4,
        device=0, workers=0, project=str(run.parent), name=run.name, exist_ok=True,
        seed=42, deterministic=True, optimizer='AdamW', lr0=0.001, lrf=0.1,
        warmup_epochs=0.0, patience=15, amp=False, pretrained=True,
        hsv_h=0.0, hsv_s=0.0, hsv_v=0.1, mosaic=0.0, mixup=0.0,
        scale=0.1, translate=0.05, fliplr=0.5, flipud=0.0,
        close_mosaic=0, cache=False, plots=True, save=True, val=True)
    # Ultralytics may use only the directory we just reserved, not an old run.
    (run / 'requested_settings.json').write_text(json.dumps(settings, indent=2)+'\n')
    model = YOLO(str(CHECKPOINT))
    metrics = model.train(**settings)
    best = run / 'weights/best.pt'
    trained = YOLO(str(best))
    assert trained.names == {0:'blue_cube',1:'green_cube',2:'red_cube'}
    with torch.inference_mode():
        output = trained.model.eval()(torch.zeros(1,3,640,640))
        tensor = output[0] if isinstance(output,tuple) else output
        assert list(tensor.shape) == [1,7,8400] and torch.isfinite(tensor).all()
    reported = {k:float(v) for k,v in metrics.results_dict.items()}
    assert all(math.isfinite(v) for v in reported.values())
    with (run / 'results.csv').open() as stream:
        epochs = len(list(csv.DictReader(stream)))
    summary = dict(status='completed', epochs_completed=epochs, run=str(run),
        checkpoint=str(best), checkpoint_sha256=sha(best), validation_metrics=reported,
        manifest_sha256=sha(EVIDENCE/'development_split.json'),
        output_shape=list(tensor.shape), class_names=trained.names,
        limitation=(
            'Eight same-room validation images from one capture session; '
            'live robot testing remains separate.'
        ))
    (run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__ == '__main__':
    main()
