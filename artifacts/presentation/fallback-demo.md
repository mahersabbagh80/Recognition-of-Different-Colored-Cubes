# Saved-evidence fallback demonstration

Use this sequence if the robot is unavailable or a live restart takes more than about one minute.

1. Open slide 14 and explain that it contains the saved live ROS 2 debug view from today's test.
2. Point to the red detection and its confidence value.
3. State the separately observed three-cube result: blue about 0.85, green about 0.86, and red about 0.74, with exactly three boxes.
4. State the empty-scene observation: `keep=0` after all cubes were removed.
5. Continue to slide 15 and explain that enabling the geometry filter kept zero detections even though the model continued producing candidates.

This fallback uses preserved project evidence. No backup video was recorded during the completed live session, so do not introduce it as a video demonstration.
