# Teaching notes

Last refreshed: 2026-09-05

## Learner and mission

- Maher has an engineering background and prefers systems, pipelines, debugging, and causal “why” explanations over long mathematical derivations.
- The mission is to own the M3–M7 perception decisions and explain them convincingly in robotics software-engineering interviews.
- Use English, concrete examples, and current repository evidence. Clearly label general concepts versus checkout-specific contracts.
- Give a practical visual or GUI path before terminal commands when both are reasonable.

## Current project anchor

- Workspace: `docs/learn/` inside this repository.
- Runtime stack: a YOLOv5u-style, YOLOv5s-sized checkpoint exported through ONNX to TensorRT FP16 on Jetson Orin Nano with ROS 2 Humble.
- Current model contract: input `[1, 3, 640, 640]`; output `[1, 7, 8400]`; class order `blue_cube`, `green_cube`, `red_cube`.
- Current engineering evidence: M5 is PARTIAL. The runtime path and empty-scene rejection work, while reliable positive detection in the JetRover room remains unresolved.
- The geometry filter’s current `depth > floor + threshold` selection has the wrong sign for raised surfaces in z-depth and must not be described as validated height reasoning.

## Teaching workflow

- Start with `MISSION.md`, then inspect evidence-based files in `learning-records/` before choosing the next lesson.
- If no learning record exists, use a lesson’s retrieval block or the Lesson 0009 explain-back as a diagnostic; do not assume exposure equals mastery.
- Create a numbered learning record only after Maher demonstrates understanding, discloses prior knowledge, or corrects a misconception.
- Lessons use `assets/lesson.css` and `assets/quiz.js`; reusable explanations belong in printable HTML files under `reference/`.
- Keep historical workspace, agent, and milestone notes under `history/`; they are not current teaching state.

## Preferences to preserve

- One focused lesson per session, normally within one hour.
- Dark theme by default; print output remains light.
- Project files and measured outputs before generic examples.
- “Why this, not that?” framing is welcome when it explains a real engineering trade-off.
- No commits unless Maher explicitly requests one.
