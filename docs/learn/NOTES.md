# NOTES.md — Teaching session notes

## User profile (from interview)

- Engineering background, light math. Want systems / pipelines / debugging, not derivations.
- Mission: own M3–M5 decisions on the project + explain the stack in robotics SWE interviews (Agile Robots, Nura).
- Time budget: ~1 hour per session. One short lesson + quiz + tiny exercise per session.
- Project: YOLOv5s + TensorRT FP16 on Jetson Orin Nano via ROS 2 Humble. Current state: M2 done, M3 (ONNX export) next.
- Language: English only (per system memory).

## Working notes

- Workspace at `~/maher_ws/learn_cube_recognition/`. Keep all teaching content here; do not touch the project's `src/` tree.
- The project has a `.cursorrules` that bans HSV/LAB/contour approaches — don't even mention them as alternatives in lessons.
- Anchor every lesson to a real file/line in the project. Concrete beats abstract.
- Don't re-teach ROS 2 basics (node structure, QoS mechanics) at the level the `robotics-tutor` profile already covers — link to the skill if the user needs to revisit, don't duplicate.
- The first lesson is M3 (ONNX export) anchored, because that's literally the next thing the user is doing.
- Per the teach skill: reference docs in `reference/`, lessons in `lessons/`, learning records in `learning-records/`, reusable components in `assets/`. Build the shared stylesheet first.

## Preferences to remember

- Short lessons over long ones.
- Systems focus over math.
- Concrete file/line references in the project.
- "Why this, not that" framing is welcomed (project makes lots of explicit tradeoffs).
- **Dark theme by default** for lesson reading. The shared stylesheet auto-applies `prefers-color-scheme: dark`; user can still toggle via the button in the top-right of each lesson. Print is always light. Don't author any new lessons that hard-code light-only colors — use CSS variables.
