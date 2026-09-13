# Speaker notes

These notes match `colored-cube-detection-presentation-v5.pptx`. They are written as a speaking guide rather than a script that must be memorized.

## Slide 1 — Colored Cube Detection on NVIDIA Jetson Hardware

My project goal is to recognize red, green, and blue cubes from a live robot camera. The detector runs on NVIDIA Jetson edge hardware. I will explain the complete path from collecting my own images to running the trained model through TensorRT and ROS 2.

## Slide 2 — Goal and verified outcome

The target behavior is live recognition while the camera view changes. In today's live test, the detector recognized red, green, and blue cubes together. When I removed all cubes, one stable empty-room scene produced no visible detection. These observations prove that the new model runs on the live camera stream, but they do not establish a general reliability percentage.

## Slide 3 — System architecture

The RGB camera provides the visible image. ROS 2 synchronizes the image with depth data and converts it into arrays the detector can process. The image is resized and normalized for the model. YOLO predicts a class, confidence, and bounding box for each candidate. TensorRT executes this model on the Jetson GPU. The optional geometry filter then uses depth measurements to reject shapes that do not look like raised cubes. The node publishes structured detections and an annotated debug image.

## Slide 4 — The starting problem

The first three-epoch smoke run proved that the software path worked, but the detector was unusable. At confidence 0.01 it produced 2 correct detections, 20 false detections, and 10 misses across the four development images. At confidence 0.25 and 0.50 it produced no detections and missed all 12 cubes. The run used too little training and every batch remained inside the library's minimum warm-up period. We therefore changed the training schedule and later added targeted robot-camera images.

## Slide 5 — Self-collected dataset

I arranged and captured the scenes with the robot camera. I reviewed every selected image and approved the bounding boxes and color labels. The final export has 23 training images and 8 separate validation images. Training contains 13 labeled instances of each cube color; validation contains 6 of each. Both splits include background-only images so the model also sees scenes where it should produce no cube detection. The data still comes from one room, so it does not represent every possible environment.

## Slide 6 — Fine-tuning the detector

I started from a pretrained YOLOv5u-small checkpoint. Pretraining means the weights already encode general visual patterns. Fine-tuning adjusts those weights using my cube images. The run used 60 epochs, a batch size of 4, 640 by 640 input images, and AdamW with a learning rate of 0.001. Training selected epoch 45 as `best.pt` because it achieved the strongest validation result. The final epoch remains available separately as `last.pt`.

## Slide 7 — Validation on separate scenes

Training images teach the model. Validation images test whether the learned behavior transfers to arrangements that were not used for weight updates. The approved annotations are the expected answers, and the saved predictions are the model output. A true positive has the correct color and enough box overlap. A false positive is an additional incorrect box. A false negative is a cube the model misses.

## Slide 8 — Validation result

In our joint visual review, the model detected 17 of the 18 visible validation cubes. It missed the red cube in V03 while correctly detecting blue and green. We saw no additional box in the eight saved prediction views. The automated best-checkpoint metrics were precision 0.982, recall 0.964, mAP50 0.995, and mAP50–95 0.707. These metrics describe this small eight-image validation set and should not be presented as universal robot accuracy.

## Slide 9 — Deployment on NVIDIA Jetson

Training saved a PyTorch checkpoint. I exported that checkpoint to ONNX, which represents the computation graph in a portable format. I transferred the ONNX file to the Jetson and built a TensorRT FP16 engine there. The conversion changed the runtime format and optimized execution for the Jetson GPU; it did not retrain the detector. A smoke comparison on V03 found blue and green and missed red in both PyTorch and TensorRT, which gave initial evidence that the conversion preserved the relevant output behavior.

## Slide 10 — Live ROS 2 detection

The live node loaded the new TensorRT engine with confidence 0.25 and the geometry filter disabled. The screenshot shows a real red cube detected at confidence 0.78. In a later live scene, the debug view showed exactly three boxes: blue at about 0.85, green at about 0.86, and red at about 0.74. After removing all cubes, the stable empty scene reported `keep=0`. This is direct live evidence from the new detector under the tested room conditions.

## Slide 11 — Geometry filter limitation

The geometry filter produced the clearest remaining problem. With the filter enabled, the model still generated about four candidates per frame, but the filter kept none of them. Every recorded rejection entered the `flat` category. This means the trained detector was still working and the downstream depth-based filter removed the valid cubes. I did not guess new thresholds before the presentation. The correct next diagnosis needs synchronized RGB and depth values for the same candidates.

## Slide 12 — Conclusion and next engineering step

The system now detects red, green, and blue cubes live with a fine-tuned YOLO model running through TensorRT on NVIDIA Jetson hardware. The next engineering step is to capture synchronized RGB and depth evidence, correct the geometry filter, and then verify the complete 3D location output. Through this work I learned how dataset design, fine-tuning, validation, model conversion, and ROS 2 deployment connect in one practical perception system.
