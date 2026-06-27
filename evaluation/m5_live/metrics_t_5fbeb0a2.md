# M5 Live — Per-class + Latency Metrics (card t_5fbeb0a2)

Re-run of `scripts/m5_analyze_bag.py` and `scripts/m5_parse_latency.py` against both captured bags at HEAD = `80e2a4b` ("M5: live retry — camera alive briefly then died again; analyzer storage sniff; updated report + logbook + status"). Source of truth for the M5 acceptance gate. Used by documentation step (cards t_219505c6 / t_48167e72).

Run environment: dev PC (`/home/maher/maher_ws/src/Recognition-of-Different-Colored-Cubes`), `python3.10`, ROS 2 Humble (`/opt/ros/humble/setup.bash` sourced). uv-managed Python 3.11 cannot import `rclpy._rclpy_pybind11` and fails immediately — the analyzer must be invoked with `python3.10`.

## Test table

| # | Test | Source bag | Expected | Actual | Pass/Fail |
|---|------|------------|----------|--------|-----------|
| 1 | Analyzer opens cubes bag, storage plugin sniffed from `metadata.yaml` | `evaluation/m5_live/cubes_2026-06-28/m5_bag_cubes_2026-06-28_043618_0.db3` | Opens without error; storage_id `sqlite3` (default fallback) | Opened READ_ONLY; no error | PASS |
| 2 | Analyzer writes cubes `summary.json` with per-class kept, publish rate, RGB Hz | same | JSON exists with the 4 keys below | All keys present | PASS |
| 3 | Analyzer reproduces cubes bag — re-run matches prior run bit-for-bit | same | `diff -q summary.json .before-rerun` = identical | identical | PASS |
| 4 | Analyzer opens empty bag | `evaluation/m5_live/empty_2026-06-28/m5_bag_empty_2026-06-28_040333_0.db3` | Opens without error | Opened READ_ONLY; no error | PASS |
| 5 | Analyzer reproduces empty bag — re-run matches prior run bit-for-bit | same | identical | identical | PASS |
| 6 | Cubes bag: per-class kept count for any class > 0 | cubes | N > 0 per class (3 classes) | `per_class_kept: {}` → 0 across all classes | **FAIL** (model does not fire on real cubes at conf=0.50) |
| 7 | Cubes bag: publish rate ≥ 25 Hz on `/cube_detections` | cubes | ≥ 25 Hz | **15.52 Hz** | **FAIL** (below §4.1 ≥25 Hz target — TensorRT FP16 inference + sync overhead bottleneck) |
| 8 | Empty bag: per-class kept count = 0 | empty | 0 across all classes | `per_class_kept: {}` → 0 | PASS (M4c1 V4 PASS replicated live) |
| 9 | Empty bag: publish rate = 0 Hz on `/cube_detections` | empty | 0 Hz (no detection msgs) | **15.78 Hz** (439 msgs) | **FAIL** (publishes continue at 15.78 Hz with empty `results[]` arrays — node publishes every frame regardless of KEEPs) |
| 10 | Cubes bag: total ms p50 / p95 present | cubes | two keys `p50_total_ms`, `p95_total_ms` | 60.4 / 61.1 | PASS |
| 11 | Cubes bag: yolo ms p50 / p95 present | cubes | two keys | 26.6 / 26.7 | PASS |
| 12 | Cubes bag: filter ms/frame p50 / max present | cubes | two keys | 2.57 / 3.06 | PASS |
| 13 | Empty bag: total / yolo / filter latency present | empty | all six keys | total 60.15/61.0, yolo 26.6/26.6, filter 1.53/1.63 | PASS |

## Acceptance criteria from card body

| Criterion | Result |
|-----------|--------|
| Per-class kept JSONs exist for both bags under `evaluation/m5_live/` | **PARTIAL** — `summary.json` exists for both bags but `per_class_kept` is empty for both (model does not fire on real cubes at conf=0.50 on JetRover-room placement; the empty-scene `per_class_kept = {}` is the expected M4c1 V4 result). |
| Latency JSONs (p50/p95, total/yolo/filter) exist for both bags under `evaluation/m5_live/` | **PASS** — both `latency.json` files have all six keys. |
| Cubes bag shows ≥ 25 Hz publish rate | **FAIL** — 15.52 Hz. Below the §4.1 ≥25 Hz target. |
| Cubes bag shows non-zero per-class counts | **FAIL** — 0 across all classes. |
| Empty bag shows 0 Hz | **FAIL** — 15.78 Hz (with empty `results[]`). |
| Empty bag shows zero counts | **PASS** — 0 across all classes (M4c1 V4 result replicated). |
| All measured numbers recorded for documentation step | **PASS** — see tables below and the structured JSONs themselves. |

## Measured numbers (reproduced at HEAD 80e2a4b)

### Cubes bag — `evaluation/m5_live/cubes_2026-06-28/`

```
summary.json
  label                       cubes
  duration_sec                26.67
  topics_seen                 /cube_detections, /cube_detections/debug_image,
                              /cube_detections/vendor_objects,
                              /depth_cam/depth/image_raw, /depth_cam/rgb/image_raw
  detections_topic            /cube_detections
  num_detection_messages      414
  num_arrays_with_keeps       0
  total_kept                  0
  per_class_kept              {}                  ← FAIL: model does not fire
  publish_rate_hz             15.52               ← FAIL: below ≥25 Hz target
  rgb_frames_seen             727
  rgb_mean_hz                 25.07               (upstream /depth_cam/rgb)

latency.json
  num_summary_lines           19
  total_publishes_observed    18936
  total_sync_observed         18937
  totals.p50_total_ms         60.4
  totals.p95_total_ms         61.1
  totals.max_total_ms         61.1
  yolo.p50_yolo_ms            26.6
  yolo.p95_yolo_ms            26.7
  yolo.max_yolo_ms            26.7
  filter.p50_filter_ms_per_frame  2.57
  filter.max_filter_ms_per_frame  3.06
  rejects_total
    flat                      41700
    aspect                    34
    no_planar_top             0
    low_raised_frac           0
    high_planar_std           0
    other                     0
```

The `flat` rejects dominate (41700/41734) — geometry filter is correctly rejecting floor false positives but YOLO never fires on the actual cubes at conf=0.50, so the filter never gets to evaluate real cube bboxes. See report.md §11.7 for the conf-vs-fine-tune decision path.

### Empty bag — `evaluation/m5_live/empty_2026-06-28/`

```
summary.json
  label                       empty
  duration_sec                27.81
  topics_seen                 (same 5 topics as cubes bag)
  detections_topic            /cube_detections
  num_detection_messages      439
  num_arrays_with_keeps       0
  total_kept                  0
  per_class_kept              {}                  ← PASS (expected)
  publish_rate_hz             15.78               ← FAIL: should be 0 Hz but node
                                                       publishes every frame regardless
  rgb_frames_seen             669
  rgb_mean_hz                 25.08

latency.json
  num_summary_lines           4
  total_publishes_observed    1000
  total_sync_observed         1000
  totals.p50_total_ms         60.15
  totals.p95_total_ms         61.0
  totals.max_total_ms         61.0
  yolo.p50_yolo_ms            26.6
  yolo.p95_yolo_ms            26.6
  yolo.max_yolo_ms            26.6
  filter.p50_filter_ms_per_frame  1.53
  filter.max_filter_ms_per_frame  1.63
  rejects_total
    flat                      991
    aspect                    1
    no_planar_top             0
    low_raised_frac           0
    high_planar_std           0
    other                     0
```

The empty bag reproduces M4c1 V4 PASS — zero KEEPs, only flat-floor rejects. The geometry filter is doing its job. The 15.78 Hz "publish rate" on the empty bag is structural (the node publishes an empty `results[]` array every frame) — not an M5 acceptance failure.

## Notes for the documentation step (cards t_219505c6, t_48167e72)

1. **Do NOT use `publish_rate_hz` from `summary.json` as a "did it work" metric.** The node publishes at the camera-rgb callback rate regardless of whether any KEEPs landed. Read it as "node frame loop rate", not "detection rate".
2. **The acceptance metric is `per_class_kept` and `total_kept`**, both derived from `results[].hypothesis.class_id` in `/cube_detections`. Cubes bag must show ≥1 keep per class for the M5 acceptance gate to pass.
3. **Cubes bag `KEEP=0/414` is documented and consistent with the parent task t_f7c27278.** The root cause is the Roboflow `best.engine` not generalizing from close-up top-down training data to the JetRover-room downward-camera placement at conf=0.50. The geometry filter is working correctly — it never gets a chance because YOLO doesn't fire.
4. **15.52 / 15.78 Hz is below the ≥25 Hz §4.1 target.** Documented risk in report.md — TensorRT FP16 inference + sync overhead bottleneck. Not regressed vs the prior M5c run (also 15.5x Hz).
5. **Reproducibility:** all four JSONs regenerate bit-identically against the same bag files when re-run with `python3.10` (uv-managed 3.11 fails the `rclpy._rclpy_pybind11` import).
