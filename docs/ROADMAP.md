# Goals & Roadmap

---

## Goals & Success Criteria

| Goal | Done when |
|------|-----------|
| Camera streaming | Image topic publishing on the Jetson (topic name TBD on hardware) |
| Image visible | Frame visible in RViz2 or `rqt_image_view` |

---

## Milestones

### Milestone 1 — Camera Bringup

- [ ] Confirm ROS 2 Humble is running on the Jetson
- [ ] Stop the HiWonder auto-start service: `sudo systemctl stop start_app_node.service`
- [ ] Launch bringup and confirm camera node starts without errors
- [ ] Discover the camera image topic: `ros2 topic list`
- [ ] Confirm image data is publishing: `ros2 topic echo <image_topic> --once`
- [ ] View the live feed in RViz2 or `rqt_image_view`

**Done when:** A camera image topic is live on the Jetson and a frame is visible in a viewer.

---

<!-- Milestones 2+ (color segmentation, cube detection, ROS output) will be added after Milestone 1 is validated on hardware. -->
