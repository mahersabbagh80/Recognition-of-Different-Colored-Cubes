#!/usr/bin/env python3
"""Bounded own-data experiment with explicit small-dataset optimizer settings."""
import json
import math
import csv
import torch
from ultralytics import YOLO
from run_robot_training_smoke import ROOT, EVIDENCE, CHECKPOINT, DATA, RUNS, sha

RUN_NAME = 'experiment_60ep'

def main():
    run = RUNS / RUN_NAME
    if run.exists():
        raise FileExistsError(run)
    assert torch.cuda.is_available()
    assert sha(CHECKPOINT) == '054272ddbbb3035cea7ff6b97e5becea63d2cc57a4f06a2a8133f4d1a56e74ed'
    split = json.loads((EVIDENCE / 'development_split.json').read_text())
    assert sha(EVIDENCE / 'human_review.json') == split['review_sha256']
    data_root = ROOT / 'evaluation/results/robot_training_2026-09-09'
    for frame in split['frames']:
        assert sha(data_root / frame['image']) == frame['sha256']
        rows = (data_root / frame['label']).read_text().splitlines()
        assert len(rows) == len(frame['objects'])
        for row, obj in zip(rows, frame['objects']):
            values = list(map(float, row.split()))
            assert len(values) == 5 and all(math.isfinite(v) for v in values)
    torch.set_num_threads(4)
    settings = dict(data=str(DATA), epochs=60, imgsz=640, batch=4, nbs=4,
        device=0, workers=0, project=str(RUNS), name=RUN_NAME, exist_ok=False,
        seed=42, deterministic=True, optimizer='AdamW', lr0=0.001, lrf=0.1,
        warmup_epochs=0.0, patience=15, amp=False, pretrained=True,
        hsv_h=0.0, hsv_s=0.0, hsv_v=0.1, mosaic=0.0, mixup=0.0,
        scale=0.1, translate=0.05, fliplr=0.5, flipud=0.0,
        close_mosaic=0, cache=False, plots=True, save=True, val=True)
    (EVIDENCE / 'experiment_requested_settings.json').write_text(json.dumps(settings, indent=2)+'\n')
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
        limitation='Four same-session validation images; no independent test or robot acceptance.')
    (EVIDENCE/'experiment_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__ == '__main__':
    main()
