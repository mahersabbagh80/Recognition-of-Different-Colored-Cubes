# Mission: Own the colored-cube perception stack

## Why

I want to make and debug the M3–M7 perception decisions in this project rather than only execute commands. I also want to explain the architecture, evidence, trade-offs, and current limitations convincingly in robotics software-engineering interviews.

## Success looks like

- I can draw the path from camera frame to published detection and explain the contract at every boundary.
- I can explain and diagnose the `best.pt → best.onnx → best.engine` export chain.
- I can decode the current `[1, 7, 8400]` output and explain confidence filtering, inverse letterboxing, and per-class NMS without notes.
- I can reason about ROS 2 synchronization, QoS, image conversion, depth validity, and output messages in the current node.
- I can distinguish training metrics, frame-hit coverage, live acceptance evidence, and unknowns without overclaiming.
- I can propose a reversible next experiment for a model, export, runtime, or geometry failure and name the evidence that would confirm it.

## Constraints

- Sessions are approximately one hour and should produce one observable learning win.
- Use light mathematics: include it when it changes an engineering decision, but do not derive backpropagation by hand.
- Anchor every lesson to current repository code, artifacts, or measurements and distinguish those facts from general concepts.
- Preserve the project’s YOLO-first, TensorRT FP16, three-class architecture unless the project itself changes.
- Hardware exercises should work on either the development PC or Jetson when practical, without requiring both simultaneously.

## Out of scope

- Replacing the detector with a classical color-thresholding pipeline.
- Re-deriving the YOLO literature from first principles.
- Full 3D pose estimation, grasp planning, or manipulation control.
- Behaviour cloning or LLM-driven task execution.
