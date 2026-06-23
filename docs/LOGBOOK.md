# Logbook

Development notes and session records for this project.

This logbook is a chronological record of what I worked on, what I found, and what I will do next. It complements the [`README.md`](../README.md) (what the project is and how to run it) and [`milestones.md`](milestones.md) (the plan).

---

## How to use this logbook

- Add **one entry per work day** (or per meaningful session if you work twice in one day).
- Keep entries short and factual — bullet points, not essays.
- Link to evidence where possible: terminal output, screenshot filenames, model files, commit hashes.
- When you finish a milestone step, record the **exact command or config** so it is reproducible.
- At the end of each day, fill in every section of the template below — even if the answer is "none" for Blockers.

Copy the template block for each new entry. Replace `YYYY-MM-DD` with the session date and `M?` with the active milestone.

---

## Legend

| Field | What to write |
|-------|---------------|
| **Milestone** | Which milestone you were working toward (M1–M7). |
| **Goal** | What you intended to achieve in this session. |
| **Work done** | Commands run, files changed, decisions made. |
| **Results** | What worked or failed; include numbers (fps, accuracy, topic hz) when available. |
| **Evidence** | Screenshots, log files, model paths, terminal snippets, git commits. |
| **Blockers** | Anything stopping progress — or "None." |
| **Next** | The very next action to take (one or two items max). |

---

## Entry template

```markdown
## YYYY-MM-DD — Short session title

- **Milestone:** M? — milestone name
- **Goal**
  -

- **Work done**
  -

- **Results**
  -

- **Evidence**
  -

- **Blockers**
  - None.

- **Next**
  -
```

---

## Entries

<!-- New entries go below this line, newest at the top. -->

## 2026-06-23 — M2 outside-Roboflow model-source addendum

- **Milestone:** M2 — Model weights ready
- **Goal**
  - Search outside Roboflow for free/open model weights or model options, including Google's Gemma/Gemma-vision models, before creating any download/training card.

- **Work done**
  - Reviewed Google Gemma 3 and Gemma 4 primary docs, Google AI Edge / MediaPipe detector docs, TensorFlow/Kaggle EfficientDet, OWL-ViT, Grounding DINO, RT-DETR, RF-DETR, Kaggle cube datasets, GitHub cube-detector repos, Hugging Face model search results, and GitHub repository search results.
  - Added an "Outside Roboflow addendum" to `docs/model-options.md` with a comparison table, Google Gemma viability answer, recommendation, and Maher decision checklist.

- **Results**
  - Gemma 3 / Gemma 4 are local/open-weight VLMs, not appropriate M2 detector artifacts for the current YOLOv5 `best.pt -> ONNX -> TensorRT -> ROS 2` pipeline.
  - No direct non-Roboflow colored-cube `best.pt` source was found. The strongest non-Roboflow find is the Apache-2.0 Edge Impulse / Kaggle conveyor-cubes dataset as a possible dataset supplement, not a ready model.
  - Recommendation remains: keep the Roboflow/YOLOv5s decision path unless Maher explicitly approves a separate architecture change.

- **Evidence**
  - `docs/model-options.md` — "Outside Roboflow addendum" section.
  - Sources are cited in that addendum.

- **Blockers**
  - None for research. M2 implementation still depends on Maher choosing raw Roboflow weights vs local YOLOv5s training and approving the dataset source.

- **Next**
  - Orchestrator should create the actual M2 implementer card only after Maher's dataset/source decision.

## 2026-06-23 — M2 model-source research

- **Milestone:** M2 — Model weights ready
- **Goal**
  - Re-check whether a pretrained colored-cube `best.pt` is actually available before downloading anything.

- **Work done**
  - Reviewed the current Roboflow Universe project, related Roboflow cube models, Roboflow weight/download docs, Ultralytics YOLO/TensorRT docs, GitHub/Hugging Face search results, and the M1 Jetson constraints.
  - Created `docs/model-options.md` with candidate comparison, source links, access notes, risks, recommendation, and Maher's decision checklist.
  - Linked the M2 research decision from `docs/technical-stack.md` and updated the strategy wording in `docs/Concept-and-Approach.md`.

- **Results**
  - Current evidence does not support assuming a public unauthenticated Roboflow Universe YOLOv5 `best.pt` download. Public pages expose hosted model/API access and dataset export; raw weights appear account/plan-gated.
  - Recommended path: first check Roboflow raw-weights access; if unavailable, use the approved Roboflow YOLOv5-format dataset to fine-tune YOLOv5s locally and create a project-owned `models/best.pt`.

- **Evidence**
  - `docs/model-options.md`
  - Roboflow project pages and docs cited inside `model-options.md`.

- **Blockers**
  - None for research. M2 implementation depends on Maher's Roboflow account/access decision.

- **Next**
  - Create a separate M2 implementer card after Maher chooses either raw-weight download (if available) or local YOLOv5s fine-tune from dataset.

## 2026-06-23 — M1 verification on real Jetson (complete)

- **Milestone:** M1 — Environment ready
- **Goal**
  - Verify M1 end-to-end on real Jetson hardware (camera topic live + ML/runtime versions confirmed) and unblock M2.

- **Work done**
  - SSH to Jetson (`ubuntu@192.168.2.138`) using the existing `~/.ssh/jetrover` key alias — verified whoami + hostname.
  - Set the six mandatory vendor env vars: `need_compile=True`, `MACHINE_TYPE=JetRover_Mecanum`, `LIDAR_TYPE=LD19`, `HOST=/`, `MASTER=`, `DEPTH_CAMERA_TYPE=Dabai`.
  - Refreshing the OSRF GPG key on Jetson (`curl -sSf https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg`, rewrote `/etc/apt/sources.list.d/ros2.list` to use `[signed-by=...]`) fixed the expired-key error (`EXPKEYSIG F42ED6FBAB17C654`) and allowed `sudo apt install ros-humble-vision-msgs` to succeed.
  - `source /opt/ros/humble/setup.bash` + `source /home/ubuntu/ros2_ws/install/setup.bash` (vendor overlay), then rsynced the scaffold into `~/jetson_ws/src/Recognition-of-Different-Colored-Cubes/`.
  - `colcon build --packages-select recognition_of_different_colored_cubes --symlink-install` on Jetson; verified `ros2 pkg executables recognition_of_different_colored_cubes` lists `cube_detection_node`; verified `python3 -c "from recognition_of_different_colored_cubes.cube_detection_node import main"` succeeds (vision_msgs.msg now resolves).
  - Live launch smoke test: `ros2 launch recognition_of_different_colored_cubes detection.launch.py` for 6 s against the live vendor bringup; node `/cube_detection_node` joined the live graph alongside `/ekf_filter_node`, `/depth_cam/camera_container`, `/arm_controller`. Topics `/cube_detections`, `/cube_detections/vendor_objects`, `/cube_detections/debug_image` all advertised.
  - Updated `docs/milestones.md` M1 camera-topic and ML-version checkboxes from `[ ]` to `[x]` with verified numbers; collapsed the verbose retry-2/retry-3 narrative into a pointer to this logbook entry.

- **Results**
  - **Camera (`/depth_cam/rgb/image_raw`):** publishing at ~30 Hz sustained (`ros2 topic hz` reported `average rate: 29.94–30.45 Hz`, `min: 0.006s, max: 0.049s, std dev: 0.0046s` over a 5 s window). Bandwidth `20.65 MB/s` over 100 messages, mean frame size **0.69 MB**. QoS RELIABLE / VOLATILE / KEEP_LAST. `frame_id = depth_cam_color_optical_frame`. Publisher = node `/depth_cam`. 13 `/depth_cam/*` topics visible (RGB + depth + IR + compressed variants).
  - **Jetson hardware/runtime:** Orin Nano, aarch64, L4T **R36.3.0**, JetPack user-space libs (`lib/aarch64-linux-gnu/nvidia`), `nvidia-smi` reports `GPU 0 Orin (nvgpu), Driver Version: N/A, CUDA Version: 12.2`. Python **3.10.12** (`/usr/bin/python3`). torch **2.4.0**, `torch.cuda.is_available() = True`, `torch.version.cuda = 12.2`, device name `Orin`. onnxruntime-gpu **1.18.0** with providers `['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']`. tensorrt **8.6.2**. ultralytics **8.3.97**. torchvision **0.19.0a0+48b1edf** (pre-installed).
  - **ROS deps on Jetson:** `ros-humble-vision-msgs 4.1.1-1jammy.20260416.073004 arm64` now installed (was missing — fixed by the GPG-key refresh above). `ros-humble-cv-bridge 3.2.1-1jammy.20240524.023716 arm64` already present. `ros-humble-sensor-msgs 4.2.4-1jammy.20240523.235623 arm64` already present. `interfaces` discoverable once the vendor overlay is sourced.
  - **Build:** clean rebuild of the package on Jetson finished in **4.75 s** with exit 0 (one harmless `EasyInstallDeprecationWarning` from the ament_python build hook).
  - **Launch smoke test:** node ran for 6 s with no crash, no exception. Honest scaffold INFO line: *"Inference backend is not implemented yet; publishing empty Detection2DArray and ObjectsInfo scaffold messages."* (expected for M1 — no inference yet).
  - **M1 verdict: COMPLETE.** All six acceptance criteria verified on real hardware.

- **Evidence**
  - Updated: `docs/milestones.md` M1 section (concise checkboxes + pointer to this entry).
  - Kanban thread: `t_639cf91d` retry-3 tester comment (2026-06-23 ~18:10) is the authoritative source for the raw `ros2 topic hz` / `bw` / version-check outputs.
  - Jetson: `dpkg -l ros-humble-vision-msgs` → `ii ... 4.1.1-1jammy.20260416.073004 arm64`; `ros2 pkg executables recognition_of_different_colored_cubes` → `recognition_of_different_colored_cubes cube_detection_node`.

- **Blockers**
  - None for M1.

- **Carryover to downstream milestones** (not blockers — track for M3/M4)
  - **M3 (ONNX export):** standalone `onnx` python module is **not** installed on Jetson — `pip install onnx` (or `--no-deps` if upstream pip resolver complains about Jetson's pinned versions). Alternatively, export ONNX on the dev PC and copy the file over.
  - **M4 (TensorRT engine):** `trtexec` CLI is **not** on Jetson PATH. Likely location is `/usr/src/tensorrt/bin/trtexec` (JetPack puts the TensorRT samples under `/usr/src/tensorrt/samples/` on Orin); fallback is the in-Python `python3 -c "from tensorrt.tools import trtexec"` interface.
  - **Dev PC:** the same expired-OSRF-key symptom applies. Recommended one-shot: `sudo curl -sSf https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list && sudo apt update && sudo apt install ros-humble-vision-msgs`.

- **Side notes (informational, not blockers)**
  - `start_app_node.service` is **active** on the Jetson — vendor bringup runs at boot and already brings up the camera + chassis + arm + lidar. Standard workflow per `.cursorrules`: `sudo systemctl stop start_app_node.service` before custom launches to avoid duplicate camera nodes.
  - `/opt/ros/humble/local_setup.bash` references `/home/ubuntu/setup.sh` (legacy HiWonder scaffold leftover, doesn't exist on this Jetson). Workaround: source `/opt/ros/humble/setup.bash` directly + `source /home/ubuntu/ros2_ws/install/setup.bash` (vendor overlay) + `source ~/jetson_ws/install/setup.bash` (project overlay).
  - Kitware apt repo on the Jetson is also missing a GPG key (`NO_PUBKEY 65ADECD7A7039392`); didn't block ROS2 packages, left for next maintenance pass.
  - `ros2 run ... --help` fails on Humble for `--help` placed before `--ros-args` (raises `UnknownROSArgsError`). Use `ros2 run <pkg> <exec> --ros-args --help` instead.

- **Next**
  - Move on to **M2** — download the pretrained Roboflow `best.pt` weights; no training needed unless M4 accuracy is poor.

## 2026-06-05 — README visitor and recruiter refactor

- **Milestone:** M1 — Environment ready
- **Goal**
  - Refocus README for GitHub visitors and recruiters — not an internal dev log.

- **Work done**
  - Restructured `README.md`: merged overview/problem into "What it does", added "What I built" and Results table.
  - Removed redundant sections (topics, success criteria, dependencies bullets, training diagram, internal status).
  - Merged hardware/software into Requirements; reframed Quick Start (dev build + Jetson workflow).
  - Split Documentation index into "For visitors" vs "Development notes".

- **Results**
  - README is shorter and scannable; detail delegated to `docs/` via links.
  - Results section ready to fill after hardware evaluation.

- **Evidence**
  - `README.md`

- **Blockers**
  - None.

- **Next**
  - Verify camera topic on Jetson (`ros2 topic hz /depth_cam/rgb/image_raw`).

## 2026-06-05 — Repository scaffolding and doc alignment

- **Milestone:** M1 — Environment ready
- **Goal**
  - Scaffold the ROS 2 package and align documentation before hardware verification.

- **Work done**
  - Created package structure: `cube_detection_node.py` (scaffold), launch file, config, scripts, training notebook stubs.
  - Populated `README.md`, `project-definition.md`, `technical-stack.md`, `milestones.md`, `evaluation.md`.
  - Added `.cursorrules` with project context and incremental implementation rules.
  - Wrote `Concept-and-Approach.md` and created inference/training pipeline diagrams (`.dot` + `.png`).
  - Pre-M1 alignment: fixed README image links, populated `architecture.md`, added ONNX step to training diagram, removed `ROADMAP.md`, set duration to 1 week across docs.
  - Verified `colcon build` and scaffold node startup locally.

- **Results**
  - Package builds and `cube_detection_node` logs scaffold message on launch.
  - Documentation is consistent; no broken diagram links.
  - Camera topic not yet verified on Jetson — M1 hardware step remains.

- **Evidence**
  - `recognition_of_different_colored_cubes/cube_detection_node.py`
  - `assets/concept2_inference_pipeline.png`, `assets/concept2_training_pipeline.png`
  - `docs/architecture.md`, `.cursorrules`

- **Blockers**
  - None.

- **Next**
  - SSH to Jetson, stop `start_app_node.service`, verify `/depth_cam/rgb/image_raw` with `ros2 topic hz`.
