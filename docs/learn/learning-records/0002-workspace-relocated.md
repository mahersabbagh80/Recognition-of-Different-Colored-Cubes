# Workspace relocated inside the project repo

Originally scaffolded at `~/maher_ws/learn_cube_recognition/` as a sibling to `src/`. Moved into the project at `docs/learn/` on 2026-06-24.

**Reason:** every lesson in this workspace is anchored to a concrete file/line in this project (`cube_detection_node.py`, `models/best.pt`, the M3/M4 scripts). Future lessons will cite project-specific code. Keeping the workspace inside the repo means the lessons travel with the code they're about — when this project is opened on a different machine, the lessons are right there.

**Implications for future sessions:**
- All path references in lessons use `../assets/...` and `../MISSION.md` from inside `lessons/`, which still resolve from the new location. Verified.
- `MISSION.md` is now scoped to this project, not a general CV learning arc (the original "reusable for the next project" claim was removed).
- The "tracked, not gitignored" decision means a future `git status` will list the lessons alongside the code. That's intentional.
- If a future project needs its own learning workspace, that one will be a fresh `docs/learn/` in that project's repo, not a shared workspace.

**Note on MISSION.md claim:** The original `MISSION.md` said "lessons transfer to the next project (likely manipulation / 6-DOF pick on the same JetRover)." That was true *if* the workspace stayed outside the repo. With the workspace now scoped to this project, the carry-over is at the *conceptual* level (YOLO fundamentals still apply to the manipulation project) but the *files* won't transfer. The "Side benefit" sentence in the original MISSION was therefore overclaimed; future re-use requires either (a) copying individual lessons, or (b) starting a new `docs/learn/` in the next project's repo.
