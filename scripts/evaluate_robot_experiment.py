#!/usr/bin/env python3
"""Count detections at a declared fixed threshold on the development split."""
import json
import torch
from ultralytics import YOLO
from run_robot_training_smoke import ROOT, EVIDENCE, RUNS, sha

def iou(a,b):
    intersection = max(0,min(a[2],b[2])-max(a[0],b[0])) * max(0,min(a[3],b[3])-max(a[1],b[1]))
    union = (a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-intersection
    return intersection / union if union else 0.0

def match(predictions, truth):
    counts = {name:dict(tp=0,fp=0,fn=0) for name in ['blue_cube','green_cube','red_cube']}
    used = set()
    for pred in sorted(predictions,key=lambda p:p['confidence'],reverse=True):
        candidates = [(iou(pred['bbox_xyxy'],gt['bbox_xyxy']),i) for i,gt in enumerate(truth)
                      if i not in used and gt['class_name']==pred['class_name']]
        score,index = max(candidates,default=(0,-1))
        if score >= 0.5:
            used.add(index)
            counts[pred['class_name']]['tp'] += 1
        else:
            counts[pred['class_name']]['fp'] += 1
    for i,gt in enumerate(truth):
        if i not in used:
            counts[gt['class_name']]['fn'] += 1
    return counts

def main():
    # Guard the two important counting rules: no duplicate matches and correct color.
    gt = [{'class_name':'red_cube','bbox_xyxy':[0,0,10,10]}]
    p = dict(gt[0],confidence=0.9)
    assert match([p,p],gt)['red_cube']==dict(tp=1,fp=1,fn=0)
    assert match([dict(p,class_name='blue_cube')],gt)['red_cube']['fn']==1
    assert iou([0,0,10,10],[20,20,30,30])==0
    torch.set_num_threads(4)
    checkpoint = RUNS/'experiment_60ep/weights/best.pt'
    model = YOLO(str(checkpoint))
    manifest = json.loads((EVIDENCE/'development_split.json').read_text())
    frames = []
    totals = {name:dict(tp=0,fp=0,fn=0) for name in model.names.values()}
    for frame in manifest['frames']:
        if frame['split']!='val':
            continue
        path = ROOT/'evaluation/results/robot_training_2026-09-09'/frame['image']
        assert sha(path)==frame['sha256']
        result = model.predict(str(path),device='cpu',imgsz=640,rect=False,conf=0.5,iou=0.7,max_det=300,verbose=False)[0]
        predictions = [dict(class_name=model.names[int(box.cls.item())],confidence=float(box.conf.item()),bbox_xyxy=box.xyxy[0].tolist()) for box in result.boxes]
        counts = match(predictions,frame['objects'])
        for name in totals:
            for key in totals[name]:
                totals[name][key] += counts[name][key]
        frames.append(dict(image_id=frame['image_id'],ground_truth=frame['objects'],predictions=predictions,counts=counts))
    for count in totals.values():
        count['precision'] = count['tp']/(count['tp']+count['fp']) if count['tp']+count['fp'] else None
        count['recall'] = count['tp']/(count['tp']+count['fn']) if count['tp']+count['fn'] else None
    report = dict(checkpoint_sha256=sha(checkpoint),confidence=0.5,nms_iou=0.7,matching_iou=0.5,
        preprocessing='CPU, imgsz=640, rect=False',per_class=totals,frames=frames,
        limitation='Development validation only; two arrangements, same session, no background-only frames.')
    (EVIDENCE/'experiment_fixed_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(totals,indent=2))

if __name__=='__main__':
    main()
