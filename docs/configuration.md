# Detector configuration reference

Default values come from [config/params.yaml](../config/params.yaml). This reference describes the September 2026 checkout.


Defaults live in [config/params.yaml](../config/params.yaml). They still use confidence 0.50, filter enabled, and an automatic default model path. The [tested README command](../README.md#quick-start) overrides them without changing the defaults.

The current node reads these settings during initialization. Use a restart to apply changes: `ros2 param set` alone is not a verified way to update the running detector's cached settings. Model files are local artifacts; see [model inventory](../models/README.md).

**Topics**

| Parameter | Default | Purpose |
|---|---|---|
| `image_topic` | `/depth_cam/rgb/image_raw` | Vendor RGB input the node YOLO-infers on |
| `depth_topic` | `/depth_cam/depth/image_raw` | Vendor color-registered depth (uint16 mm) the geometry filter samples |
| `rgb_camera_info_topic` | `/depth_cam/rgb/camera_info` | Source of `fx/fy/cx/cy` (overridden at startup from the live message) |
| `detections_topic` | `/cube_detections` | Published `vision_msgs/Detection2DArray` — kept detections only |
| `vendor_objects_topic` | `/cube_detections/vendor_objects` | Published `interfaces/ObjectsInfo` — vendor-compatible output |
| `debug_image_topic` | `/cube_detections/debug_image` | Published `sensor_msgs/Image` (bgr8) — annotated overlay for `rqt_image_view` |

**Model + inference**

| Parameter | Default | Purpose |
|---|---|---|
| `model_path` | `""` (automatic search for `models/best.engine`) | Engine path. Set an explicit path to select the dated model; Git does not supply an engine. |
| `confidence_threshold` | `0.50` | YOLO candidates below this are dropped before geometry is even applied. |
| `iou_threshold` | `0.45` | NMS IoU threshold for duplicate suppression on the raw YOLO output. |
| `imgsz` | `640` | Square letterbox size the engine expects. |

**RGB + depth sync**

| Parameter | Default | Purpose |
|---|---|---|
| `sync_slop_sec` | `0.05` | Maximum timestamp gap between an RGB and depth message for the `ApproximateTimeSynchronizer` to pair them (50 ms; a pairing tolerance, not a measured median). |
| `sync_queue_size` | `10` | Pairwise queue depth for the synchronizer. |

**Geometry post-filter**

The [geometry helper](../recognition_of_different_colored_cubes/geometry_filter.py) applies depth-based heuristics to each detection. In September's live comparison, it rejected real cubes as `flat`; the root cause remains unresolved. Earlier June distractor rejection tests do not establish acceptance of real cubes with the current model.

The code names a subset `raised`, but actually selects depth values greater than the surrounding ring median plus a threshold. This is a depth comparison, not a calibrated measurement of height above the floor. The descriptions below reflect the implementation, not a claim that its geometry assumptions are correct.

| Parameter | Default | Plain-language meaning |
|---|---|---|
| `filter_enabled` | `true` | Master switch. Set to `false` to publish every YOLO candidate ≥ `confidence_threshold` with no geometry check. |
| `filter_n_min` | `30` | Minimum number of valid depth pixels inside the YOLO bbox before the filter will even try to decide — below this, the detection is kept with a `low_depth_quality` reason rather than silently rejected. |
| `filter_max_depth_mm` | `4000` | Anything farther than 4 m is treated as invalid depth (kinect noise / dropouts) and excluded from the stats. |
| `filter_inset_px` | `1` | Number of pixels to shrink the YOLO bbox inward before sampling depth. Prevents the annulus from leaking in and the in-box stats from picking up edge pixels of the cube's slanted sides. |
| `filter_annulus_outer_px` | `15` | Width of the surrounding rectangular ring whose median depth supplies the reference. |
| `filter_raised_mm` | `30` | Offset used in `depth > ring_median + offset` to select the subset named `raised`. |
| `filter_min_raised_frac` | `0.20` | Minimum fraction of valid in-box depths in the selected subset; otherwise reject as `flat`. |
| `filter_max_ratio` | `1.2` | Maximum estimated longest/shortest 3D extent ratio for the selected subset; otherwise reject as `aspect`. |
| `filter_max_planar_top_stddev_mm` | `30` | Maximum depth standard deviation of the selected subset; otherwise reject as `no_planar_top`. This is not a plane-fitting test. |

**Diagnostics**

| Parameter | Default | Purpose |
|---|---|---|
| `latency_log_every` | `100` | Frames between p50/p95 latency log lines (total + yolo + filter). |
| `publish_vendor_objects` | `true` | Toggle the vendor-compatible output. |
| `publish_debug_image` | `true` | Toggle the annotated debug overlay. |

Historical geometry-filter parameter rationale and the V2/V3/V4 evidence gate → [`docs/milestones.md`](milestones.md) and [`evaluation/m4c_geometry_filter/report.md`](../evaluation/m4c_geometry_filter/report.md).


## Camera calibration and fallback settings

`fx`, `fy`, `cx`, and `cy` in the YAML are camera calibration fallbacks, replaced from camera information at startup. `fallback_model_path` is declared in the node but is not a verified alternative engine-loading route; use `model_path` explicitly.

