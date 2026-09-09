#!/usr/bin/env python3
"""Inspect low-score candidates without changing the fixed evaluation threshold."""
import json
import torch
from ultralytics import YOLO
from evaluate_robot_experiment import match, iou
from run_robot_training_smoke import ROOT, EVIDENCE, RUNS, sha

def main():
    torch.set_num_threads(4)
    checkpoint = RUNS/'experiment_60ep/weights/best.pt'
    model = YOLO(str(checkpoint))
    manifest = json.loads((EVIDENCE/'development_split.json').read_text())
    frames=[]
    for frame in manifest['frames']:
        if frame['split']!='val':
            continue
        path=ROOT/'evaluation/results/robot_training_2026-09-09'/frame['image']
        assert sha(path)==frame['sha256']
        result=model.predict(str(path),device='cpu',imgsz=640,rect=False,conf=0.001,iou=0.7,max_det=300,verbose=False)[0]
        predictions=[dict(class_name=model.names[int(b.cls.item())],confidence=float(b.conf.item()),bbox_xyxy=b.xyxy[0].tolist()) for b in result.boxes]
        candidates=[]
        for gt in frame['objects']:
            nearby=[dict(p,iou=iou(p['bbox_xyxy'],gt['bbox_xyxy'])) for p in predictions if iou(p['bbox_xyxy'],gt['bbox_xyxy'])>=0.5]
            candidates.append(dict(ground_truth=gt,overlapping_candidates=sorted(nearby,key=lambda p:p['confidence'],reverse=True)))
        frames.append(dict(image_id=frame['image_id'],ground_truth=frame['objects'],predictions=predictions,candidates=candidates))
    counts={}
    for threshold in [0.001,0.1,0.25,0.5]:
        totals={name:dict(tp=0,fp=0,fn=0) for name in model.names.values()}
        for frame in frames:
            per_class=match([p for p in frame['predictions'] if p['confidence']>=threshold],frame['ground_truth'])
            for name in totals:
                for key in totals[name]:
                    totals[name][key]+=per_class[name][key]
        counts[str(threshold)]=totals
    baseline=json.loads((EVIDENCE/'experiment_fixed_validation.json').read_text())
    assert baseline['checkpoint_sha256']==sha(checkpoint)
    for name in counts['0.5']:
        for key in ['tp','fp','fn']:
            assert counts['0.5'][name][key]==baseline['per_class'][name][key]
    report=dict(checkpoint_sha256=sha(checkpoint),inference=dict(device='cpu',imgsz=640,rect=False,conf=0.001,iou=0.7,max_det=300),
        matching_iou=0.5,threshold_counts=counts,frames=frames,
        purpose='Post-hoc development diagnosis only; fixed 0.50 result remains unchanged.')
    (EVIDENCE/'experiment_miss_review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(counts,indent=2))
    for frame in frames:
        if frame['image_id'].startswith('spread_out'):
            print(frame['image_id'])
            for item in frame['candidates']:
                print(item['ground_truth']['class_name'],[(p['class_name'],round(p['confidence'],4),round(p['iou'],4)) for p in item['overlapping_candidates'][:3]])

if __name__=='__main__':
    main()
