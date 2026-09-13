# Tutor questions and suggested answers — v8

Use these as short spoken answers. Add detail only when the tutor asks a follow-up question.

## 1. What problem does the project address?

It aims to recognize red, green, and blue cubes from the JetRover camera and pass detections into the robot software. The live RGB detector works in the tested scenes; reliable depth-based localization is still unfinished.

## 2. What is the strongest live result so far?

With the geometry filter disabled and confidence threshold set to 0.25, I observed one live frame with all three cube colors correctly boxed. An empty view of that room produced no cube box. These are individual observations, not a reliability rate.

## 3. Is the complete depth-based pipeline finished?

No. The raw detector can produce boxes, but the current geometry filter rejected every candidate in the tested cube scene. I cannot yet claim reliable depth-based cube checks or final 3D locations.

## 4. What was your contribution, and what did you reuse?

I collected and reviewed project images, approved labels, chose the data split, ran the training and deployment steps, and inspected the results. I used the existing project exporter and ROS 2 detector, Ultralytics YOLO, and TensorRT; Codex helped guide the work, adapt parts of the workflow, and check outputs. I did not write the whole stack or train a model from random weights.

## 5. What did the pretrained weights contribute?

I initialized from the general pretrained `yolov5su.pt` checkpoint, not the earlier cube-specific model. Fine-tuning adapted those learned visual features to our reviewed cube images; the model therefore still benefits from general pretraining.

## 6. Why collect project-specific images?

They show the cubes through the intended robot camera, with our room, viewpoints, and empty backgrounds. That makes them relevant to this setup, but it does not by itself prove performance in other rooms or conditions.

## 7. How did you reduce same-scene leakage between training and validation?

Frames from the same arrangement can be almost duplicates, so I kept whole arrangements together instead of randomly splitting individual frames. The eight validation images use held-out arrangements, but they still come from the same room and capture session as the new training additions, so the split is not an independent new-scene test.

## 8. What is the difference between training, validation, and a final test?

Training examples update the model weights. Validation examples help compare checkpoints and settings. A final test must use fresh, untouched scenes after those choices are fixed; this project has not completed that independent test.

## 9. How much evidence supports the validation result?

The run used 23 training images (13 earlier images plus 10 new ones) and eight new validation images from the same room. The validation set is useful development evidence for held-out arrangements, but it is small and does not establish broad generalization or reliable robot performance.

## 10. Is confidence the same as accuracy?

No. Confidence is the model's score for an individual predicted box; it is not a guarantee that the box is correct or the model's overall accuracy. A confidence threshold decides which predictions are kept and changes the balance between missed cubes and extra boxes.

## 11. What does the 17-of-18 result mean?

In a human review of the eight saved validation views, 17 of 18 annotated cubes had a matching visible box. The red cube in V03 was missed, and no additional visible box was found. This is a count from those rendered predictions, not a general accuracy claim.

## 12. Why are 17/18 and the automated precision/recall different?

The automated report gives precision 0.982 and recall 0.964 at Ultralytics' smoothed maximum-F1 point on its confidence curve, using IoU 0.50 matching. The 17/18 count comes from visually checking the saved prediction views. They summarize predictions differently, so their numbers need not be identical.

## 13. What do mAP and the selected checkpoint tell us?

mAP50 summarizes the precision-recall curve with a 0.50 box-overlap requirement; mAP50–95 averages stricter overlap requirements too. This run selected epoch 45 as `best.pt` using validation mAP50–95 (about 0.707); that selects a candidate within development data, not a final accepted model.

## 14. What changed when the model was converted to TensorRT?

ONNX export and TensorRT FP16 conversion changed the runtime format and optimized execution for the Jetson; they did not retrain the model. One V03 smoke test preserved which two colors were detected, but one image is only an initial conversion check.

## 15. Can I quote the TensorRT engine benchmark as live camera FPS?

No. `trtexec` used random input and measured the warmed engine path, reporting about 70.9 queries per second, 14.45 ms mean host latency, and 13.79 ms mean GPU computation. It excludes the camera, image preparation, decoding, geometry filter, and ROS publication.

## 16. What latency did the live node show?

During the filter-disabled live diagnostic, the node logged roughly 57.7–59.1 ms median total processing time and 25.9 ms median TensorRT inference time. These are internal timings from that run, not output FPS or camera-to-browser latency.

## 17. Why does the system have a geometry filter, and what did the test show?

The filter uses depth and geometry after RGB detection to check whether a candidate resembles a raised cube before publishing it. With it disabled, cube boxes were visible; with the same engine enabled, about four candidates per frame were rejected as “flat,” and none were kept. That locates the observed failure at the filter stage.

## 18. Do we know why the geometry filter rejects the cubes?

Not yet. The evidence does not distinguish tight detector boxes, the raised-depth threshold, RGB-depth alignment, or another filter assumption. The next diagnostic is to save a synchronized RGB/depth pair and inspect the geometry values for cube and distractor candidates before changing the filter.
