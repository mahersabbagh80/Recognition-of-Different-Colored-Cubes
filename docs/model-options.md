# M2 Model / Weights Options

Date: 2026-06-23

## Purpose / M2 decision context

M2 originally assumed that a Roboflow Universe project would provide a directly downloadable pretrained YOLOv5 `best.pt`. This research pass re-checks that assumption before any weights, datasets, exports, or training are downloaded/run.

The key finding is that the relevant Roboflow Universe projects do provide hosted trained detection models and downloadable datasets, but the public pages do not expose a simple unauthenticated YOLOv5 `best.pt` download. Roboflow's current docs say manual raw weight download is a paid/Core-or-Enterprise feature, while Roboflow Inference can automatically fetch/cache model weights for local Roboflow runtime use. That is not the same as having a project-owned YOLOv5 `.pt` that can follow the current `best.pt -> best.onnx -> best.engine` path.

Implementation access check update (2026-06-24): an implementer worker without Roboflow credentials could not access a raw compatible `.pt` from the original Jakub Slof project or the Ezhil same-class candidate. No `models/best.pt` was created. See the dated LOGBOOK entry for the exact evidence and handoff steps.

Therefore, M2 should not blindly proceed as "download public `best.pt` from Universe". The next step needs a short account/access check.

## JetRover constraints from M1

From the M1 hardware verification in `docs/LOGBOOK.md`:

- Robot/runtime: Jetson Orin Nano, aarch64, L4T R36.3.0, CUDA 12.2 user-space.
- Camera input: `/depth_cam/rgb/image_raw`, about 30 Hz, `sensor_msgs/Image`, `frame_id = depth_cam_color_optical_frame`, publisher `/depth_cam`.
- Runtime packages verified on Jetson: Python 3.10.12, torch 2.4.0 CUDA 12.2, onnxruntime-gpu 1.18.0 with TensorRT/CUDA providers, TensorRT 8.6.2, Ultralytics 8.3.97, torchvision 0.19.0a0.
- Output contract remains vendor-first but not vendor-modifying: consume the HiWonder camera topic, publish standard `/cube_detections` plus `/cube_detections/vendor_objects`, and do not modify `src/vendor`.
- Target deployment chain remains: PyTorch/YOLO weights -> ONNX -> TensorRT FP16 engine -> ROS 2 node.

These constraints favor a small YOLO-family detector with a reliable export path and locally owned artifacts.

## Candidate model / weights table

| Candidate | What is available now | Raw `.pt` / `best.pt` availability | Fit to JetRover YOLO -> ONNX -> TensorRT path | Timeline fit | Main risks | Verdict |
|---|---|---|---|---|---|---|
| Roboflow Universe: Jakub Slof `red-green-blue-cube-detection/1` | Public Roboflow hosted model + API; dataset v1 with YOLOv5-format export; classes `bluecube`, `green cube`, `red cube`; public page shows mAP@50 86.1%, precision 80.3%, recall 72.5%. | Public page shows `Deploy Model`, `Fork Dataset`, and `Download Dataset`, not public `Download Weights`. Manual raw weights download is account/plan-gated per Roboflow docs. | Dataset fits YOLOv5 training/export. Hosted Roboflow model does not directly satisfy the current local `best.pt` requirement unless Maher can export raw weights. | Good as dataset and API sanity check. Conditional as weights source. | Account/API requirement; raw weights may not be exportable; class labels have spaces/inconsistent `bluecube`; small dataset (103 images in v1 export page). | Best current project-aligned dataset; conditional/not guaranteed as pretrained `.pt` source. |
| Roboflow Universe: ezhil `red-green-blue-cube-detection-tkoml/1` | Public hosted model/API; same target classes; page shows higher metrics (mAP@50 99.5%, precision 98.2%, recall 100.0%); dataset listed as 461 images / browse 207 images. | Same Roboflow access issue: hosted API is visible; public raw `.pt` is not visible. | Similar to above if dataset can be exported in YOLOv5 format; hosted Roboflow 3.0 model is not guaranteed to be a YOLOv5 `.pt`. | Good candidate to compare through API or as dataset, if license/source acceptable. | No published description; unclear data provenance; possible derivative/duplicate of original; raw weights unavailable without account/plan. | Strong secondary Roboflow candidate, but not enough to replace the safer Jakub dataset without review. |
| Roboflow Universe: robotics25 `color-cube-identifier/4` | Public hosted model/API; larger color-cube dataset, classes include `blue-cube`, `green-cube`, `orange-cube`, `pink-cube`, `red-cube`, `yellow-cube`; model type shown as YOLOv11s model upload. | Public raw weights not visible; hosted/API access requires key. | Less aligned: YOLOv11s/uploaded model and six-class label set would require label mapping/filtering; vendor docs are currently YOLOv5-first. | Medium. Useful if project later expands color set, not ideal for current M2. | Extra classes, label mismatch, less vendor alignment, raw weights access uncertain. | Not recommended for current M2 primary path. |
| Public GitHub/Hugging Face YOLOv5 cube weights | Hugging Face API searches for colored/RGB cube YOLO models returned no direct matches. GitHub API search found `thohemp/cube_detector`, a YOLOv5 OBB cube detector with a referenced `m640rot.pt`. | `thohemp/cube_detector` appears to reference a weight file, but it is oriented bounding boxes/generic cube detection, not red/green/blue cube classification. No strong public RGB-cube `best.pt` source found. | Partial. YOLOv5 base helps, but OBB/custom repo and non-matching labels make it a poor drop-in for this ROS/TensorRT plan. | Poor-to-medium. Integration/debug time likely exceeds just training a small local model on the right labels. | Wrong task labels, OBB head/export differences, unknown weight availability/license/runtime assumptions. | Do not use as primary. Mention only as prior art. |
| Train/fine-tune YOLOv5s locally from Roboflow dataset | Download YOLOv5-format dataset from Roboflow Universe, start from COCO-pretrained YOLOv5s, train 20-30 epochs on dev PC, produce local `best.pt`. No custom robot data upfront. | Produces project-owned `best.pt`. | Best fit: YOLOv5 `.pt` -> ONNX -> TensorRT; aligns with vendor YOLOv5 reference. | Realistic for one week if training is short and dataset is small. | Adds training step to M2/M3; accuracy on JetRover camera still must be tested; class-name cleanup needed. | Recommended fallback if raw Roboflow weights are not accessible. In practice this may become the primary local-artifact path. |
| Fine-tune YOLOv8n/YOLO11n from available cube dataset | Roboflow datasets can export YOLOv8/YOLO11 formats; Ultralytics supports ONNX/TensorRT export. | Produces local `.pt`, but model family changes. | Technically good for Ultralytics/TensorRT, but weaker vendor alignment because current JetRover/vendor reference is YOLOv5. | Medium. Modern tooling is good, but changing model family adds integration risk. | May require docs/architecture changes; TensorRT/runtime wrapper differs from vendor YOLOv5 example. | Secondary fallback only if YOLOv5 path fails. |
| HSV/LAB color thresholding baseline | Vendor examples already include LAB color detection, color tracking, and color sorting patterns. | No weights involved. | Not applicable to M2 weights path. Useful as diagnostic/baseline only. | Fast to test later. | Lighting-sensitive; detects colored blobs, not learned cube objects; violates the current main detector intent if used as the main path. | Keep as fallback/baseline only, not M2 model source. |

## Source links and access notes

### Implementation access check: 2026-06-24

- Worker environment check: `ROBOFLOW_API_KEY` and `ROBOFLOW_WORKSPACE` were not set, and no local Roboflow config directory was present.
- Original Jakub Slof page inspected in browser: `https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection`
  - Visible public actions: `Deploy Model`, `Fork Dataset`, hosted inference/API snippets, and dataset links.
  - No public `Download Weights`, `weights.pt`, or `best.pt` action was visible while signed out.
  - `More model info` reports Roboflow 3.0 Object Detection (Fast), dataset `red-green-blue-cube-detection/1` with 103 images, COCO checkpoint, Aug 16 2023.
- Ezhil same-class candidate inspected in browser: `https://universe.roboflow.com/ezhil-sdu5m/red-green-blue-cube-detection-tkoml`
  - Visible public actions were also hosted inference/API and dataset/fork flows, not raw weights.
  - `More model info` reports Roboflow 3.0 Object Detection (Fast), dataset `red-green-blue-cube-detection-tkoml/1` with 461 images, COCO checkpoint, Mar 1 2025.
- Unauthenticated Roboflow API probes for likely model/weights endpoints returned HTTP 401 with "This method requires your API key". Dataset export endpoints are not equivalent to a raw weights download and did not provide a `.pt` artifact.
- Current decision: raw compatible Roboflow weights are not accessible to this worker. Do not force hosted API, Roboflow Inference cache, dataset export, ONNX, or any other incompatible artifact into `models/best.pt`.
- Required Maher action if the raw-weights path should continue: sign in to Roboflow, open the selected model version in the dashboard/model page, check for `Download Weights`, and confirm the exact file format/model family/license. If a PyTorch `.pt` is available, provide the downloaded file or a non-secret API-key setup path to the worker.
- Recommended fallback if no PyTorch `.pt` is available from Maher's account: create the next implementation card to train YOLOv5s from the approved Roboflow YOLOv5-format dataset and save the resulting project-owned `models/best.pt`.

### Roboflow Universe: current project reference

- Main model page: https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection
  - Public page shows a hosted Roboflow Detection API using model ID `red-green-blue-cube-detection/1`.
  - Visible classes: `bluecube`, `green cube`, `red cube`.
  - Visible metrics from the browser page: mAP@50 86.1%, precision 80.3%, recall 72.5%.
  - Visible actions: `Deploy Model`, `Fork Dataset`, hosted API snippets, interactive test images.
- Dataset version page: https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection/dataset/1
  - Public page shows `Download Dataset`, not raw `Download Weights`.
  - v1 generated Aug 16, 2023; 103 total images; split 90 train / 9 validation / 4 test.
  - Popular dataset export formats include YOLOv5 (`/download/yolov5pytorch`), YOLOv8, YOLOv11, COCO, VOC, TFRecord, etc.
  - Preprocessing: auto-orient; resize/stretch to 640x640. Augmentations include rotation, shear, brightness, blur, and noise.

### Other Roboflow Universe candidates

- Ezhil RGB cube model: https://universe.roboflow.com/ezhil-sdu5m/red-green-blue-cube-detection-tkoml
  - Same visible classes: `bluecube`, `green cube`, `red cube`.
  - Browser page shows mAP@50 99.5%, precision 98.2%, recall 100.0%.
  - Public page exposes hosted API snippets; raw `.pt` not visible in the public flow.
- Robotics25 color cube identifier: https://universe.roboflow.com/robotics25/color-cube-identifier
  - Larger color-cube candidate with six cube color labels and model ID `color-cube-identifier/4`.
  - Model type reported as YOLOv11s Model Upload, which is less aligned with the current YOLOv5 vendor-first plan.
- Roboflow cube search results: https://universe.roboflow.com/search?q=class%3Acube+red
  - Search page states datasets can be exported into many formats and lists many cube-related datasets/models.

### Roboflow weights / dataset access documentation

- Roboflow manual weights docs: https://docs.roboflow.com/deploy/download-roboflow-model-weights
  - Roboflow Inference can automatically fetch/cache weights the first time a local inference request runs; future predictions use the local cache and images are not sent to the cloud.
  - Manual raw weights download is described as a premium feature for paid Core plans and certain Enterprise customers.
  - Python SDK example uses `model.download()` to download `weights.pt`, but this requires an API key and account/project access.
- Roboflow dataset export docs: https://docs.roboflow.com/developer/export-data
  - Dataset versions can be downloaded through the SDK or REST API in formats such as YOLOv5.
  - This is dataset export, not necessarily model-weight export.
- Roboflow community thread on Universe model downloads: https://discuss.roboflow.com/t/how-to-download-model-from-roboflow-universe/6355
  - A 2024 community-support thread says Roboflow did not support downloading a model file for Universe projects at that time. Treat this as lower authority than current docs, but it reinforces the need for an account/access check.

### YOLO / Jetson / export references

- Ultralytics YOLOv5 repository: https://github.com/ultralytics/yolov5
  - Mature YOLOv5 codebase with train/export scripts and supported ONNX/TensorRT deployment path.
- YOLOv5 export docs: https://docs.ultralytics.com/yolov5/tutorials/model_export/
  - YOLOv5 exports PyTorch `.pt` to ONNX and TensorRT (`.engine`), with TensorRT requiring a GPU.
- Ultralytics export docs: https://docs.ultralytics.com/modes/export/
  - Ultralytics YOLO export supports ONNX and TensorRT; docs claim TensorRT can provide up to 5x GPU speedup.
- Ultralytics TensorRT docs: https://docs.ultralytics.com/integrations/tensorrt/
  - TensorRT export supports FP16/INT8, dynamic shapes, batch settings, and NVIDIA GPU/Jetson deployment patterns.
- Ultralytics NVIDIA Jetson guide: https://docs.ultralytics.com/guides/nvidia-jetson/
  - Jetson deployment guide for Ultralytics YOLO and TensorRT.
- Prior-art GitHub repo found in search: https://github.com/thohemp/cube_detector
  - YOLOv5 OBB cube detector with ROS/ROS2-related material, but not a red/green/blue cube detector and not a drop-in M2 weights source.

## Export / deployment compatibility notes

1. The currently documented JetRover path expects a local YOLO-family PyTorch artifact, then ONNX, then TensorRT FP16.
2. Roboflow hosted model IDs such as `red-green-blue-cube-detection/1` are useful for quick API testing, but they do not automatically produce a local `best.pt` artifact.
3. Roboflow Inference local caching may run inference locally, but using Roboflow's runtime/cache is a different deployment architecture than the current vendor-aligned YOLOv5/TensorRT ROS node.
4. If Maher can access a raw weights download through Roboflow, the implementer must confirm:
   - exact file format (`.pt`, ONNX, TensorRT engine, or Roboflow-specific cache),
   - model family (YOLOv5 vs Roboflow 3.0 vs YOLOv11 upload),
   - class order and names,
   - whether the license permits local deployment in this portfolio project.
5. If raw weights are not available, training YOLOv5s on the Roboflow dataset is cleaner than trying to reverse-engineer a hosted Roboflow model into the current ROS/TensorRT pipeline.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Public Roboflow page does not provide `best.pt` | M2 cannot be completed as originally worded | Add an account/access gate before the implementer downloads anything; if no raw weights, switch M2 to producing `best.pt` by short YOLOv5 fine-tune from dataset. |
| Roboflow model family may be Roboflow 3.0, not YOLOv5 | May not export cleanly to YOLOv5 -> ONNX -> TensorRT | Verify model format before committing; prefer training YOLOv5s locally if format is unclear. |
| Class labels contain spaces / inconsistent style (`bluecube`, `green cube`, `red cube`) | ROS messages and downstream logic may need stable label IDs | Normalize labels in config/docs after selected source is approved; keep mapping explicit. |
| Dataset is small and may not match JetRover camera viewpoint/lighting | Poor M4 robot-camera accuracy | Start with no custom robot data, but keep fine-tune-on-robot-snapshots as a later fallback only if M4 fails. |
| Ezhil/other Universe projects may have high metrics but unclear provenance | Overfitting or duplicated dataset may hide real-world failure | Use metrics as weak evidence; inspect dataset samples/license before using. |
| Switching to YOLOv8/YOLO11 improves modern tooling but changes vendor alignment | More integration and documentation churn | Keep YOLOv8/YOLO11 as secondary fallback only. |
| HSV/LAB baseline may look simpler | Scope drift away from portfolio ML/TensorRT goal | Use only as diagnostic/baseline, not as the M2 weights path. |

## Recommendation

Primary recommendation for M2:

1. Perform a short Roboflow account/access check on the original Jakub Slof project and, optionally, the Ezhil same-class project.
2. If Roboflow exposes a raw downloadable weight file compatible with the current path (`.pt` that can be exported to ONNX and TensorRT), use that as the M2 artifact.
3. If Roboflow only exposes hosted API / dataset export / Roboflow Inference cache, do not force it into `best.pt`. Instead, revise M2 to: download the YOLOv5-format dataset, fine-tune YOLOv5s locally for 20-30 epochs from COCO-pretrained weights, and save the resulting project-owned `models/best.pt`.

### Fallback path: EXECUTED on 2026-06-24

Maher confirmed that the Roboflow Universe pages expose only `Deploy Model`
(no `Download Weights` / `weights.pt` / `best.pt` UI) and that the worker's
environment has no `ROBOFLOW_API_KEY` or `ROBOFLOW_WORKSPACE`. The fallback
path (item 3 above) was therefore selected and executed: the approved Roboflow
YOLOv5-format dataset for `jakub-lof/red-green-blue-cube-detection/1` (CC BY 4.0,
103 images) was used to fine-tune YOLOv5s from the COCO-pretrained
`yolov5s.pt`, 30 epochs, 640×640, batch 16, on the dev PC RTX 4070 Ti, producing
`models/best.pt` (18.5 MB, SHA-256
`bba833c25bd6cb51683b3b84dfb1160ed74e1c918a2d629087133ae2a5120b04`,
val mAP@0.5 = 0.954 at epoch 18, per-class mAP@0.5 = blue 0.982 / green 0.885 /
red 0.995). The Roboflow export mixed object-detection labels with polygon
segmentation labels, so a one-time polygon→bbox normalization step was added
in `scripts/normalize_dataset.py` and documented in `models/README.md` and the
2026-06-24 M2 LOGBOOK entry. **M2 verdict: COMPLETE. Next: M3 ONNX export.**

Practical recommended default if Maher wants the lowest implementation risk:

- Treat the original Jakub Slof Roboflow project as the dataset/license baseline because it is already cited in the project docs and matches the desired three classes.
- Treat the Ezhil same-class project as a secondary candidate to inspect, not an automatic replacement, because the public metrics are better but provenance/description are unclear.
- Keep the model family YOLOv5s for the first local artifact because that aligns with the Hiwonder vendor YOLOv5/TensorRT reference.

Fallback recommendation:

- If YOLOv5 training/export underperforms or fails, evaluate YOLOv8n/YOLO11n on the same dataset as a separate architecture decision.
- Use HSV/LAB/vendor color detection only as a baseline or lighting diagnostic.

## Decision checklist for Maher before download/use step

Before the implementer touches weights or datasets, Maher should decide:

- [ ] Is a Roboflow account/API key available for this project?
- [ ] On the selected Roboflow model page, is there a visible `Download Weights` button for the model version?
- [ ] If yes, what exact file is provided: `.pt`, `.onnx`, TensorRT `.engine`, or something Roboflow-runtime-specific?
- [ ] Is the model family compatible with the current YOLOv5 export path?
- [ ] Are the selected classes exactly acceptable, or should labels be normalized to `red_cube`, `green_cube`, `blue_cube` in project config?
- [ ] If raw weights are not available, approve changing M2 from "download pretrained `best.pt`" to "train a small YOLOv5s `best.pt` from the open Roboflow dataset; no custom robot images unless M4 fails."
- [ ] Confirm that the chosen source license is acceptable for a GitHub/portfolio robotics project.

## Next step after approval

Create a separate M2 implementer card to do one of the following, depending on Maher's checklist result:

- If raw compatible weights are available: download the selected weights, save as `models/best.pt`, record source/version/license, and verify the file exists locally.
- If raw compatible weights are not available: download only the approved YOLOv5-format dataset and run the planned short YOLOv5s fine-tune to create a local `models/best.pt`.

Do not run ONNX export, TensorRT conversion, ROS node implementation, or accuracy evaluation in that M2 download/training card unless the orchestrator explicitly creates separate follow-up work.

---

## Outside Roboflow addendum

Date: 2026-06-23

### Why this addendum exists

Maher asked for a broader check before M2 proceeds, specifically including Google's free/open vision models such as Gemma 3 / Gemma 4. This addendum searches outside the earlier Roboflow-focused path for downloadable weights, datasets, or model families that could produce the M2 artifact: a local detector that outputs `red_cube`, `green_cube`, and `blue_cube` bounding boxes and can realistically feed the existing `best.pt -> ONNX -> TensorRT -> ROS 2 node` plan.

### Short answer

The recommendation should **not** change yet. Keep the current YOLOv5s path as the lowest-risk M2 route:

1. Use raw compatible Roboflow weights only if Maher's account exposes them and the file is actually compatible with the YOLOv5/export path.
2. Otherwise create a project-owned YOLOv5s `models/best.pt` from an approved detection dataset.
3. Treat Google Gemma / Gemma vision as a research reference, not the M2 weights artifact.

The best non-Roboflow addition is not Gemma; it is the Apache-2.0 Kaggle/Edge Impulse **Cubes on conveyor belt** dataset as a possible small supplemental dataset to inspect, because it has red/green/blue/yellow cube bounding boxes. It still does not provide a ready `best.pt`.

### Non-Roboflow candidates reviewed

| Candidate | Source / license | Model type | Raw weights downloadable? | Detector vs classifier vs VLM | Boxes + classes? | Jetson / ONNX / TensorRT fit | Expected latency / risk | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Google Gemma 3** | Google AI model card and Hugging Face `google/gemma-3-27b-it`; Gemma Terms, not Apache for Gemma 3. Sources: https://ai.google.dev/gemma/docs/core/model_card_3, https://huggingface.co/google/gemma-3-27b-it, https://ai.google.dev/gemma/terms | Multimodal VLM / image-text-to-text model | Yes, open weights exist, but Hugging Face access requires accepting Google's terms. | VLM, not a conventional detector. | Can reason about images and may emit textual localization if prompted/fine-tuned, but it does not provide a fixed detector head with stable `red_cube`/`green_cube`/`blue_cube` classes for ROS. | Poor fit for current M2: safetensors/Transformers VLM path, not YOLO `.pt -> ONNX -> TensorRT`; large 4B/12B/27B variants are not the right real-time detector primitive for 30 Hz camera processing. | High latency/integration risk on Jetson; output parsing risk; no direct TensorRT detector pipeline. | **Do not use for M2.** Interesting later VLM/semantic assistant candidate only. |
| **Google Gemma 4 / Gemma vision docs** | Google AI image guide and model card; Apache 2.0 for Gemma 4. Sources: https://ai.google.dev/gemma/docs/capabilities/vision/image, https://ai.google.dev/gemma/docs/core/model_card_4, https://ai.google.dev/gemma/apache_2 | Multimodal VLM / image-text-to-text model | Yes, Google documents open-weight Gemma 4 variants such as `google/gemma-4-E2B-it`, `google/gemma-4-E4B-it`, `google/gemma-4-12B-it`, `google/gemma-4-26B-A4B-it`, `google/gemma-4-31B-it`. | VLM with image understanding, not a purpose-built robotics detector. | Google documents object-detection-style bounding box prompting, but the output is generated text/structured text, not a fixed low-latency detection tensor/class head. | Poor fit for current M2 artifact: it would require a new VLM inference wrapper and output parser, not the existing YOLOv5/TensorRT ROS path. | Even E2B/E4B are much heavier than a small YOLO detector; latency and determinism are risky for live robot perception. | **No: Gemma 4 should not replace YOLOv5s for M2.** Use only as a later architecture experiment if the project scope changes. |
| **Google Gemini / cloud vision APIs** | Google AI Studio / hosted API family, not local open weights. | Cloud VLM/API | No local weights for Jetson/TensorRT deployment. | VLM/API. | May answer visual questions; not a local ROS detector artifact. | Fails offline/local deployment constraint and introduces network/API-key dependency. | Unsuitable for robot real-time loop; privacy/connectivity risk. | **Do not use for M2.** Mention only as contrast. |
| **MediaPipe Object Detector + EfficientDet-Lite0** | Google AI Edge docs; page/code Apache/CC docs; COCO-trained EfficientDet-Lite recommended. Sources: https://developers.google.com/edge/mediapipe/solutions/vision/object_detector, https://developers.google.com/edge/litert/libraries/modify/object_detection | TFLite object detector | Yes, TFLite detector models are downloadable; Model Maker can train a custom `.tflite`. | Detector. | Yes: MediaPipe returns category, score, and bounding box coordinates. But the recommended pretrained models are COCO 80-class, not `red_cube`/`green_cube`/`blue_cube`. | Medium-to-poor fit: good edge detector stack, but it changes runtime from YOLO/TensorRT to MediaPipe/TFLite. TensorRT integration is not the current path. | EfficientDet-Lite0 docs show small model size and mobile latency, but Jetson GPU/TensorRT benefit is not direct. | **Not primary.** Viable only as separate architecture decision if YOLO path fails or if TFLite/MediaPipe becomes acceptable. |
| **TensorFlow / Kaggle EfficientDet** | Kaggle model `tensorflow/efficientdet`; source page says COCO 2017 object detector. Source: https://www.kaggle.com/models/tensorflow/efficientdet | COCO object detector | Yes, model artifacts are downloadable through Kaggle model flow. | Detector. | Yes for COCO classes, not cube-color classes. | Poor for this M2 unless retrained. TensorFlow -> ONNX -> TensorRT is possible in theory but not the already documented project path. | Integration risk higher than YOLOv5s for no direct class benefit. | **Do not use as M2 artifact.** |
| **OWL-ViT** | Google/Kaggle model Apache 2.0; Hugging Face Transformers support. Sources: https://www.kaggle.com/models/google/owl-vit, https://huggingface.co/docs/transformers/en/model_doc/owlvit | Open-vocabulary detector | Yes, JAX/TF/PyTorch weights are available. | Detector, open-vocabulary. | Yes: text queries produce boxes/scores for phrases such as `red cube`. | Weak fit for current M2: boxes are available, but deployment is Transformer/PyTorch/JAX/TF, not YOLOv5 `.pt -> ONNX -> TensorRT`. | Likely slower and less deterministic than small YOLO for live 30 Hz Jetson camera. Prompt sensitivity may make stable color labels hard. | **Useful baseline/autolabeling idea, not M2 primary.** |
| **Grounding DINO** | IDEA-Research official repo Apache 2.0; Hugging Face Transformers support; NVIDIA NGC commercial trainable/deployable variants under NVIDIA Open Model License. Sources: https://github.com/IDEA-Research/GroundingDINO, https://huggingface.co/docs/transformers/en/model_doc/grounding-dino, https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/grounding_dino | Open-set / open-vocabulary detector | Yes. | Detector, open-vocabulary. | Yes: image + text prompts output bounding boxes and scores. NVIDIA NGC variant documents `pred_boxes` and `pred_logits`. | Better Jetson story than OWL-ViT if using NVIDIA TAO/NGC, but still a different architecture and tokenizer/model pipeline. Not YOLOv5-compatible. | NVIDIA documents Jetson/TensorRT support, but setup is heavier than YOLOv5s and prompt/label determinism remains a risk. | **Architecture-decision candidate only.** Do not silently substitute it for M2. |
| **RT-DETR / RTDETRv2** | Baidu/PaddleDetection pretrained models; Ultralytics wrapper. Sources: https://github.com/PaddlePaddle/PaddleDetection/tree/develop/configs/rtdetr, https://docs.ultralytics.com/models/rtdetr/ | Real-time object detector | Yes, COCO pretrained `.pdparams` / Ultralytics `.pt` weights are available. | Detector. | Yes for COCO classes; not red/green/blue cube unless fine-tuned. | Good detector family and TensorRT-friendly, but it changes model family and wrapper from YOLOv5. | Potentially fast on T4/TensorRT, but unnecessary integration churn for this small project. | **Secondary fallback only if YOLOv5 fails.** Requires architecture approval. |
| **RF-DETR** | Roboflow open repository; Apache 2.0 for package and Nano-Large detection models, PML 1.0 for Plus/XL models. Sources: https://github.com/roboflow/rf-detr, https://rfdetr.roboflow.com/ | Real-time DETR-style detector | Yes for open RF-DETR models, but this is still a Roboflow-developed path. | Detector. | Yes after fine-tuning; pretrained models are generic COCO/RF100-style, not cube-color-specific. | Strong modern candidate with TensorRT benchmark claims, but it is not the existing YOLOv5 vendor-first path. | Likely more integration work than short YOLOv5s fine-tune. | **Do not switch now.** Consider only as a future architecture experiment. |
| **Kaggle / Edge Impulse: Cubes on conveyor belt** | Kaggle dataset by Edge Impulse, Apache 2.0. Source: https://www.kaggle.com/datasets/edgeimpulse/cubes-on-conveyor-belt | Dataset, not weights | No model weights; dataset archive is downloadable. | Object-detection dataset. | Yes: bounding boxes for `blue`, `green`, `red`, `yellow` cubes. | Good supplemental dataset candidate; labels need mapping to `*_cube`; not a model artifact. | Small dataset: 70 images; conveyor-belt domain may not match JetRover camera. | **Promising non-Roboflow dataset to inspect.** Could supplement/replace dataset only after Maher approves source/license. |
| **Kaggle: Cubes, craters and cylinder detection** | Kaggle dataset, CC0 public domain. Source: https://www.kaggle.com/datasets/saikatpanda/cubes-craters-and-cylinder | YOLOv8-format dataset, not weights | No ready `best.pt` confirmed. | Object-detection dataset. | Yes, but labels are not the project labels: yellow cube, green cube, craters, red cylinder. | Useful robotics/YOLO dataset prior art, poor direct label match. | Large dataset; many irrelevant classes; would require filtering/relabeling. | **Do not use for current M2 primary.** |
| **GitHub: `thohemp/cube_detector`** | Public GitHub repo; license not confirmed in the page extract. Source: https://github.com/thohemp/cube_detector | YOLOv5 OBB cube detector with ROS/ROS2-related material | README references `m640rot.pt`; availability/license must be verified before use. | Detector with oriented bounding boxes. | Boxes yes, but not stable red/green/blue cube class labels. | Closer than VLMs because it is YOLOv5-based, but OBB head/custom fork and label mismatch make it a poor drop-in. | Integration risk from OBB/export/class mismatch. | **Prior art only.** Do not use as M2 artifact. |
| **GitHub: `ThatLinuxGuyYouKnow/rubik-yolo`** | Public GitHub repo; license not confirmed in page extract. Source: https://github.com/ThatLinuxGuyYouKnow/rubik-yolo | YOLOv8n-OBB Rubik's cube color/face detector | Yes, repo includes `best.pt` and `yolov8n-obb.pt`. | Detector with oriented bounding boxes. | Detects Rubik sticker colors and cube face, not the project's free-standing red/green/blue cubes. | Poor fit: YOLOv8 OBB model and class semantics differ from YOLOv5s axis-aligned cube detector. | High false-positive/domain risk; tiny validation warning in README. | **Do not use for M2.** Useful only as color-cube prior art. |
| **Hugging Face colored-cube search** | Hugging Face model API search, queried 2026-06-23 for `colored cube detection`, `red green blue cube detection`, `cube detection yolo best.pt`, and `rubik cube yolo`. | Search result, not a model. | No direct object-detection models returned for those queries. | N/A | N/A | No candidate found. | N/A | **No direct HF colored-cube `best.pt` source found.** |

### Can Google Gemma / Gemma vision be used for this M2 weights artifact?

**No, not as the M2 artifact for this project.**

What is true:

- Gemma 3 has open weights and multimodal text+image input; Hugging Face lists `google/gemma-3-27b-it` as an image-text-to-text model with access gated by acceptance of Google's Gemma terms.
- Google Gemma 4 documentation now lists multimodal open-weight models such as `google/gemma-4-E2B-it`, `google/gemma-4-E4B-it`, `google/gemma-4-12B-it`, `google/gemma-4-26B-A4B-it`, and `google/gemma-4-31B-it`.
- Google documents image-understanding workflows for Gemma 4, including object-detection-style bounding boxes in generated output.
- Gemma 4 is under Apache 2.0; Gemma 3 remains under the separate Gemma Terms.

Why it is not the M2 path:

- M2 needs a local detector artifact that can become `models/best.pt`, then `best.onnx`, then a TensorRT engine, and finally publish deterministic ROS bounding boxes/classes.
- Gemma is a VLM that generates text. Even when prompted for boxes, the boxes are generated tokens, not a compact detector head output with fixed class IDs, NMS, confidence thresholds, and stable latency.
- A Gemma-based pipeline would require a new architecture: VLM runtime, prompt design, output parsing, real-time scheduling, failure handling, and likely quantization work. That belongs in an architecture card, not a model-download card.
- The smallest Gemma 4 variants may be edge-oriented, but they are still much heavier and less deterministic than a YOLOv5s-style detector for a 30 Hz robot camera.

Decision: **Do not use Gemma 3 or Gemma 4 to satisfy M2.** If Maher wants a future VLM experiment, create a separate architecture/research card after the YOLO/TensorRT path is working.

### Strongest outside-Roboflow options

1. **Keep YOLOv5s and use another dataset only if needed.**
   - The Edge Impulse / Kaggle conveyor cube dataset is the most relevant non-Roboflow dataset found because it has red/green/blue/yellow cube bounding boxes and Apache 2.0 licensing.
   - It is small and domain-specific, so it should be inspected visually before use.

2. **Use open-vocabulary detectors only as baselines or labeling aids.**
   - OWL-ViT and Grounding DINO can output boxes from text prompts like `red cube`, `green cube`, `blue cube`.
   - They are useful for experiments or assisted annotation, but prompt-conditioned VLM/detector outputs are riskier than a trained small detector in a robot control loop.

3. **Use RT-DETR/RF-DETR only if the project intentionally changes architecture.**
   - These are stronger modern detectors than old YOLOv5 in general benchmarks, but they do not solve the immediate cube-label artifact problem without fine-tuning.
   - Switching would change implementation, export, inference wrapper, and documentation assumptions.

### Updated recommendation

Do **not** change the primary recommendation from the previous Roboflow/YOLOv5s plan.

Recommended M2 decision order:

1. Check whether Maher's chosen Roboflow model exposes raw compatible weights.
2. If not, approve local training of YOLOv5s to produce a project-owned `models/best.pt`.
3. Before training, choose the dataset source explicitly:
   - original Roboflow dataset if license/account access is acceptable;
   - Edge Impulse / Kaggle conveyor dataset as a non-Roboflow supplemental/alternative only after sample inspection;
   - do not use Gemma/Gemini as the detector artifact.
4. Keep labels normalized to `red_cube`, `green_cube`, `blue_cube` regardless of source labels.

### Maher decision checklist before the actual M2 download/use card

- [ ] Is the M2 goal still a YOLOv5-compatible local `models/best.pt`? If yes, reject Gemma/Gemini as M2 artifacts.
- [ ] If Roboflow raw weights are unavailable, approve whether M2 should train YOLOv5s from a dataset now instead of waiting until M4.
- [ ] Choose the dataset source: Roboflow original, Edge Impulse/Kaggle conveyor cubes, or a merged dataset after visual/license review.
- [ ] Confirm whether yellow-cube examples should be ignored, remapped, or retained only as negatives/supplemental data.
- [ ] Confirm label normalization: source labels such as `blue`, `green cube`, or `bluecube` must become `blue_cube`, `green_cube`, `red_cube` in project config/output.
- [ ] If Maher wants to pursue Grounding DINO, RT-DETR, RF-DETR, MediaPipe, or Gemma, create a separate architecture decision card rather than changing M2 silently.

### Addendum sources consulted

- Google Gemma image understanding: https://ai.google.dev/gemma/docs/capabilities/vision/image
- Google Gemma 4 model card: https://ai.google.dev/gemma/docs/core/model_card_4
- Google Gemma 4 Apache 2.0 license page: https://ai.google.dev/gemma/apache_2
- Google Gemma 3 model card: https://ai.google.dev/gemma/docs/core/model_card_3
- Gemma Terms: https://ai.google.dev/gemma/terms
- Hugging Face Gemma 3 27B IT: https://huggingface.co/google/gemma-3-27b-it
- MediaPipe Object Detector: https://developers.google.com/edge/mediapipe/solutions/vision/object_detector
- TensorFlow Lite Model Maker object detection: https://developers.google.com/edge/litert/libraries/modify/object_detection
- Kaggle TensorFlow EfficientDet: https://www.kaggle.com/models/tensorflow/efficientdet
- OWL-ViT Hugging Face docs: https://huggingface.co/docs/transformers/en/model_doc/owlvit
- OWL-ViT Kaggle model: https://www.kaggle.com/models/google/owl-vit
- Grounding DINO Hugging Face docs: https://huggingface.co/docs/transformers/en/model_doc/grounding-dino
- Grounding DINO official repo: https://github.com/IDEA-Research/GroundingDINO
- NVIDIA NGC Grounding DINO: https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/grounding_dino
- PaddleDetection RT-DETR configs: https://github.com/PaddlePaddle/PaddleDetection/tree/develop/configs/rtdetr
- Ultralytics RT-DETR docs: https://docs.ultralytics.com/models/rtdetr/
- RF-DETR GitHub: https://github.com/roboflow/rf-detr
- Edge Impulse / Kaggle cubes on conveyor belt dataset: https://www.kaggle.com/datasets/edgeimpulse/cubes-on-conveyor-belt
- Kaggle cubes/craters/cylinder YOLOv8 dataset: https://www.kaggle.com/datasets/saikatpanda/cubes-craters-and-cylinder
- GitHub `thohemp/cube_detector`: https://github.com/thohemp/cube_detector
- GitHub `ThatLinuxGuyYouKnow/rubik-yolo`: https://github.com/ThatLinuxGuyYouKnow/rubik-yolo
- Ultralytics YOLOv5 repo: https://github.com/ultralytics/yolov5
- Ultralytics YOLOv5 export docs: https://docs.ultralytics.com/yolov5/tutorials/model_export/
