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
