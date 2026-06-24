# Mission: Learn the computer-vision theory behind the colored-cube detector

## Why

Two concrete outcomes, in priority order:

1. **Own the M3–M7 decisions on the project** — not just execute the commands. When `best.pt → best.onnx` export fails, or TensorRT FP16 disagrees with the FP32 baseline, I want to know which layer to debug instead of guessing. When the on-robot inference is slow, I want to know whether the bottleneck is preprocessing, postprocessing (NMS), I/O, or actual GPU work.
2. **Explain the stack convincingly in robotics SWE interviews** (Agile Robots, Nura). Interviewers probe "why this architecture, why this export path, what would you do if X failed" — the answer should come from understanding, not from having memorised a tutorial.

A side benefit: lessons transfer to the next project (likely manipulation / 6-DOF pick on the same JetRover), where the perception pipeline will be re-used.

## Success looks like

- I can draw the inference pipeline (`frame → preprocess → backbone → head → NMS → boxes`) and name the cost at each stage.
- I can explain why YOLOv5 + ONNX + TensorRT FP16 is the right chain for the Jetson, and what each link in the chain does.
- I can read the M3 ONNX export script and the M4 TensorRT conversion script and know what the knobs do.
- I can describe the postprocessing path (decoding raw YOLO outputs, confidence thresholding, NMS) without reaching for a reference.
- I can talk through the cv_bridge / vision_msgs / ObjectsInfo wiring in the existing node and reason about QoS choices.
- I can name three concrete failure modes (e.g. INT8 calibration failure, ONNX op-set mismatch, NMS duplicated inside TensorRT vs. outside) and the first thing to try for each.

## Constraints

- **Time:** ~1 hour per session. Lessons must be completable in one sitting.
- **Math tolerance:** light. Use the math where it changes a decision, skip it where it doesn't. No deriving backprop by hand.
- **Project is the anchor.** Every lesson should connect to a real file in the project (`cube_detection_node.py`, `docs/technical-stack.md`, the M3/M4 scripts, etc.) so the learning has a home.
- **No replacing the project's decisions.** Hard constraints in `.cursorrules` are non-negotiable (YOLOv5s + TensorRT FP16, Roboflow dataset, three classes, etc.). Lessons explain, they don't re-litigate.
- **Light hardware access.** The Jetson is on the LAN, the dev PC is local — exercises should run on whichever is reasonable, not require both.

## Out of scope (for this learning arc)

- Classical CV fallbacks (HSV/LAB/contours) — explicitly ruled out by the project.
- 3D pose estimation, depth fusion, grasp planning — these are later projects.
- Re-deriving the YOLOv5 paper from scratch — the project's hard constraint is "execute, don't redesign."
- Behaviour cloning / LLM-driven task execution — that's the next project after this one.
- Building a custom dataset from scratch — explicitly deferred by the project plan.

## Path (rough order, will adjust based on what I learn)

1. Detection fundamentals — what a bounding box is, what NMS does, what a confidence score means.
2. The YOLO family — one-stage vs two-stage, what YOLOv5s actually predicts, anchor-free vs anchor-based.
3. The export chain — what ONNX is, what TensorRT does, why FP16, where things go wrong.
4. ROS 2 integration — cv_bridge, vision_msgs, sensor QoS, message contracts, why the vendor also wants `interfaces/ObjectsInfo`.
5. Debugging on the Jetson — version compatibility, common failure modes, how to bisect.

## How I'll know I'm done

I can sit in front of a robotics SWE interviewer and answer the M3–M5 questions without notes, with concrete references to the project. Until then, more lessons.

## Workspace scope

This workspace lives inside the project repository (`docs/learn/`) because the lessons are anchored to this project's specific files (`cube_detection_node.py`, `models/best.pt`, the M3/M4 scripts). If the lessons were general CV material, they'd live in a sibling directory outside the repo — but every lesson here cites a real file/line in this project, so they should travel with it. (Recorded 2026-06-24 in `docs/LOGBOOK.md` and `learning-records/0002-workspace-relocated.md`.)
