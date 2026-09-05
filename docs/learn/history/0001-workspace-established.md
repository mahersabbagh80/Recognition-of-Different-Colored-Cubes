# Workspace established for cube-recognition learning arc

The user wants to learn the CV/ML theory behind the JetRover colored-cube project, with two real-world goals: own the M3–M5 decisions (not just execute the commands) and explain the stack convincingly in robotics SWE interviews. Established a `~/maher_ws/learn_cube_recognition/` workspace with `MISSION.md`, `RESOURCES.md` (curated sources, no parametric guessing), a shared stylesheet, and Lesson 0001 anchored to the project's actual M2 artifact (`models/best.pt`) and the M5 wiring target (`cube_detection_node.py`).

**Implications for next sessions:**
- Anchor every lesson to a real file/line in the project, not abstract material.
- The path is: detection fundamentals → YOLO internals → ONNX → TensorRT → ROS 2 wiring. Lesson 0001 covers the foundation; lesson 0002 should move into YOLO output decoding (the next conceptual step before M3 export).
- Math tolerance is light. Use the math only where it changes a decision.
- Don't re-teach ROS 2 basics at the level the robotics-tutor profile already covers; link to that skill if the user needs to revisit.
- The project bans classical CV (HSV/LAB/contours) per `.cursorrules`; lessons must not present those as alternatives.
