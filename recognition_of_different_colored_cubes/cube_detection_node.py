#!/usr/bin/env python3
"""Live colored cube detection on the JetRover (M5).

Subscribes to the vendor depth-camera RGB stream and the color-registered
depth stream (``/depth_cam/rgb/image_raw`` + ``/depth_cam/depth/image_raw``),
runs TensorRT FP16 YOLOv5 inference on each RGB frame, then applies the
M4c1 geometry post-filter to every YOLO candidate above the configurable
confidence threshold. Only KEEP detections are published.

ROS 2 outputs (same as the M1/M3 scaffold):

- ``/cube_detections``  ``vision_msgs/Detection2DArray``
- ``/cube_detections/vendor_objects``  ``interfaces/ObjectsInfo``
- ``/cube_detections/debug_image``  ``sensor_msgs/Image``  (annotated overlay)

The TensorRT engine, model class list, conf threshold, and all geometry-filter
parameters are ROS 2-declared and tunable at runtime (see ``config/params.yaml``).

Depth-camera intrinsics are read once from ``/depth_cam/rgb/camera_info`` at
startup; if the topic is unavailable, the node falls back to the configured
``fx`` / ``fy`` / ``cx`` / ``cy`` defaults. ``/depth_cam/depth/camera_info`` is
also consumed for the optional ``depth_unit`` sanity check (the M4c1 geometry
filter assumes the depth image is uint16 millimeters).

The TensorRT call uses the proven inline pattern from
``scripts/test_inference.py`` (single binding allocation, shared CUDA stream
across frames, ``execute_async_v2`` + ``stream.synchronize``). On JetPack 6 /
TensorRT 8.6.2 / pycuda 2024.1 the wrapped-helper pattern silently returned
all-zero outputs, so we intentionally keep the allocation block at module /
node-construction scope.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

import numpy as np
import rclpy
from cv_bridge import CvBridge, CvBridgeError
from interfaces.msg import ObjectInfo, ObjectsInfo
from message_filters import ApproximateTimeSynchronizer, Subscriber
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose

from recognition_of_different_colored_cubes.geometry_filter import (  # noqa: E402
    compute_geometry, decide,
)

CLASS_NAMES = ["blue_cube", "green_cube", "red_cube"]
CLASS_COLORS = {
    "blue_cube": (66, 133, 244),
    "green_cube": (52, 168, 83),
    "red_cube": (234, 67, 53),
}


@dataclass(frozen=True)
class CubeDetection:
    """Internal detection representation shared by all output converters."""

    class_name: str
    score: float
    box: Sequence[float]
    reason: str = "kept"


def _letterbox(im: np.ndarray, new_shape: int = 640):
    """Resize+pad to a square ``new_shape``, preserving aspect ratio.

    Same logic as ``scripts/test_inference.py`` letterbox(). Returns the
    padded CHW float32 array (already divided by 255, NCHW-ready) plus the
    affine (ratio, pad_l, pad_t) needed to undo the letterbox at decode time.
    """
    h0, w0 = im.shape[:2]
    r = min(new_shape / h0, new_shape / w0)
    new_w, new_h = int(round(w0 * r)), int(round(h0 * r))
    pad_w, pad_h = new_shape - new_w, new_shape - new_h
    pad_l, pad_t = pad_w // 2, pad_h // 2
    pad_r, pad_b = pad_w - pad_l, pad_h - pad_t
    from PIL import Image

    img = np.array(Image.fromarray(im).resize((new_w, new_h), 1))
    img = np.pad(
        img,
        ((pad_t, pad_b), (pad_l, pad_r), (0, 0)),
        mode="constant",
        constant_values=114,
    )
    return img, r, (pad_l, pad_t)


def _decode_yolov5_output(
    out: np.ndarray, conf_thres: float, iou_thres: float,
    orig_wh, ratio, pad,
) -> list[tuple[str, float, tuple[float, float, float, float]]]:
    """Decode Ultralytics YOLOv5 fused-decode output [1, 7, 8400]."""
    import torch
    from torchvision.ops import nms

    pred = out[0].transpose()
    boxes = pred[:, :4]
    scores = pred[:, 4:]
    cls_conf = scores.max(axis=1)
    cls_id = scores.argmax(axis=1)
    mask = cls_conf >= conf_thres
    boxes, cls_conf, cls_id = boxes[mask], cls_conf[mask], cls_id[mask]
    if boxes.shape[0] == 0:
        return []

    xyxy = np.zeros_like(boxes)
    xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2
    pad_l, pad_t = pad
    xyxy[:, [0, 2]] -= pad_l
    xyxy[:, [1, 3]] -= pad_t
    xyxy /= ratio
    ow, oh = orig_wh
    xyxy[:, [0, 2]] = xyxy[:, [0, 2]].clip(0, ow - 1)
    xyxy[:, [1, 3]] = xyxy[:, [1, 3]].clip(0, oh - 1)

    keep: list[int] = []
    for c in np.unique(cls_id):
        idx = np.where(cls_id == c)[0]
        if idx.size == 0:
            continue
        b_c = torch.from_numpy(xyxy[idx]).float()
        s_c = torch.from_numpy(cls_conf[idx]).float()
        k = nms(b_c, s_c, iou_thres).numpy().tolist()
        keep.extend(idx[k])

    detections: list[tuple[str, float, tuple[float, float, float, float]]] = []
    for i in sorted(keep):
        detections.append((
            CLASS_NAMES[int(cls_id[i])],
            float(cls_conf[i]),
            tuple(float(v) for v in xyxy[i]),
        ))
    return detections


class CubeDetectionNode(Node):
    """Live TensorRT + geometry-filter ROS 2 perception node."""

    def __init__(self) -> None:
        super().__init__("cube_detection_node")

        # ── Topics ────────────────────────────────────────────────────
        self.declare_parameter("image_topic", "/depth_cam/rgb/image_raw")
        self.declare_parameter("depth_topic", "/depth_cam/depth/image_raw")
        self.declare_parameter("rgb_camera_info_topic", "/depth_cam/rgb/camera_info")
        self.declare_parameter("detections_topic", "/cube_detections")
        self.declare_parameter("vendor_objects_topic", "/cube_detections/vendor_objects")
        self.declare_parameter("debug_image_topic", "/cube_detections/debug_image")

        # ── Publish toggles ───────────────────────────────────────────
        self.declare_parameter("publish_vendor_objects", True)
        self.declare_parameter("publish_debug_image", True)

        # ── Model + inference ─────────────────────────────────────────
        self.declare_parameter("model_path", "")  # default filled in below
        self.declare_parameter("confidence_threshold", 0.50)
        self.declare_parameter("iou_threshold", 0.45)
        self.declare_parameter("imgsz", 640)

        # ── Sync ──────────────────────────────────────────────────────
        self.declare_parameter("sync_slop_sec", 0.05)
        self.declare_parameter("sync_queue_size", 10)

        # ── Geometry filter — v2-only M4c1 params ─────────────────────
        self.declare_parameter("filter_enabled", True)
        self.declare_parameter("filter_n_min", 30)
        self.declare_parameter("filter_max_depth_mm", 4000)
        self.declare_parameter("filter_inset_px", 1)
        self.declare_parameter("filter_annulus_outer_px", 15)
        self.declare_parameter("filter_raised_mm", 30)
        self.declare_parameter("filter_min_raised_frac", 0.20)
        self.declare_parameter("filter_max_planar_top_stddev_mm", 30)
        self.declare_parameter("filter_max_ratio", 1.2)

        # ── Camera intrinsics (fallback if camera_info never arrives) ─
        self.declare_parameter("fx", 360.3266)
        self.declare_parameter("fy", 360.3266)
        self.declare_parameter("cx", 321.0181)
        self.declare_parameter("cy", 179.2141)

        # ── Diagnostics ───────────────────────────────────────────────
        self.declare_parameter("latency_log_every", 100)
        self.declare_parameter("fallback_model_path", "")  # dev-PC no-engine fallback

        # Pull values out into plain attributes for hot-loop use.
        self.image_topic = self.get_parameter("image_topic").value
        self.depth_topic = self.get_parameter("depth_topic").value
        self.rgb_camera_info_topic = self.get_parameter("rgb_camera_info_topic").value
        self.detections_topic = self.get_parameter("detections_topic").value
        self.vendor_objects_topic = self.get_parameter("vendor_objects_topic").value
        self.debug_image_topic = self.get_parameter("debug_image_topic").value
        self.publish_vendor_objects = bool(
            self.get_parameter("publish_vendor_objects").value
        )
        self.publish_debug_image = bool(
            self.get_parameter("publish_debug_image").value
        )
        self.confidence_threshold = float(
            self.get_parameter("confidence_threshold").value
        )
        self.iou_threshold = float(self.get_parameter("iou_threshold").value)
        self.imgsz = int(self.get_parameter("imgsz").value)
        self.sync_slop_sec = float(self.get_parameter("sync_slop_sec").value)
        self.sync_queue_size = int(self.get_parameter("sync_queue_size").value)
        self.filter_enabled = bool(self.get_parameter("filter_enabled").value)
        self.latency_log_every = int(self.get_parameter("latency_log_every").value)

        self.filter_params = {
            "n_min": int(self.get_parameter("filter_n_min").value),
            "max_depth_mm": int(self.get_parameter("filter_max_depth_mm").value),
            "inset_px": int(self.get_parameter("filter_inset_px").value),
            "annulus_outer_px": int(self.get_parameter("filter_annulus_outer_px").value),
            "raised_mm": float(self.get_parameter("filter_raised_mm").value),
            "min_raised_frac": float(
                self.get_parameter("filter_min_raised_frac").value
            ),
            "max_planar_top_stddev_mm": float(
                self.get_parameter("filter_max_planar_top_stddev_mm").value
            ),
            "max_ratio": float(self.get_parameter("filter_max_ratio").value),
            "fx": float(self.get_parameter("fx").value),
            "fy": float(self.get_parameter("fy").value),
            "cx": float(self.get_parameter("cx").value),
            "cy": float(self.get_parameter("cy").value),
        }

        self.model_path = self.get_parameter("model_path").value
        if not self.model_path:
            # Default resolution: prefer the workspace install dir (where the
            # colcon-built artifacts usually live), then the source dir, then
            # the user's home on Jetson / dev PC.
            _candidates = [
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                    "models",
                    "best.engine",
                ),
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "..", "..", "models", "best.engine",
                ),
                "/home/ubuntu/jetson_ws/src/Recognition-of-Different-Colored-Cubes/models/best.engine",
                "/home/maher/maher_ws/src/Recognition-of-Different-Colored-Cubes/models/best.engine",
            ]
            for cand in _candidates:
                cand_abs = os.path.abspath(cand)
                if os.path.exists(cand_abs):
                    self.model_path = cand_abs
                    break
            else:
                self.model_path = os.path.abspath(_candidates[0])  # best guess; will warn at load

        self.bridge = CvBridge()
        self._warned_bridge_error = False
        self._warned_engine_missing = False

        # ── Latency diagnostics ───────────────────────────────────────
        self._frame_count = 0
        self._sync_count = 0
        self._publish_count = 0
        self._total_ms_window: list[float] = []
        self._yolo_ms_window: list[float] = []
        self._filter_ms_window: list[float] = []
        self._reject_counts = {"flat": 0, "aspect": 0,
                               "no_planar_top": 0, "low_raised_frac": 0,
                               "high_planar_std": 0, "other": 0}

        # ── Engine (lazy — TensorRT only importable on Jetson) ───────
        self._engine = None
        self._ctx = None
        self._trt_in_name = None
        self._trt_out_name = None
        self._trt_in_shape = None
        self._trt_out_shape = None
        self._in_host = None
        self._out_host = None
        self._in_dev = None
        self._out_dev = None
        self._bindings: list[int] = []
        self._stream = None
        self._engine_loaded = False

        # ── Publishers ────────────────────────────────────────────────
        self.detections_pub = self.create_publisher(
            Detection2DArray, self.detections_topic, 10,
        )
        self.vendor_objects_pub = None
        if self.publish_vendor_objects:
            self.vendor_objects_pub = self.create_publisher(
                ObjectsInfo, self.vendor_objects_topic, 10,
            )
        self.debug_image_pub = None
        if self.publish_debug_image:
            self.debug_image_pub = self.create_publisher(
                Image, self.debug_image_topic, 10,
            )

        # ── Camera info (intrinsics + depth-unit sanity check) ───────
        self._got_camera_info = False
        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            self.rgb_camera_info_topic,
            self._camera_info_cb,
            qos_profile_sensor_data,
        )

        # ── Synchronised RGB + depth subscribers ─────────────────────
        rgb_sub = Subscriber(self, Image, self.image_topic)
        depth_sub = Subscriber(self, Image, self.depth_topic)
        self._sync = ApproximateTimeSynchronizer(
            [rgb_sub, depth_sub],
            queue_size=self.sync_queue_size,
            slop=self.sync_slop_sec,
        )
        self._sync.registerCallback(self._sync_cb)

        # Lazy-engine init: attempt TensorRT load now. If we're on a dev PC
        # without CUDA / pycuda, fall back to a no-op inference stub so
        # colcon + topic wiring can still be smoke-tested. The Jetson will
        # always succeed here because the vendor bringup ships TensorRT 8.6.2
        # + pycuda 2024.1.
        self._try_load_engine()

        self.get_logger().info(
            "cube_detection_node (M5) ready:\n"
            f"  rgb_topic={self.image_topic}\n"
            f"  depth_topic={self.depth_topic}\n"
            f"  detections_topic={self.detections_topic}\n"
            f"  vendor_objects_topic={self.vendor_objects_topic}\n"
            f"  debug_image_topic={self.debug_image_topic}\n"
            f"  publish_vendor_objects={self.publish_vendor_objects}\n"
            f"  publish_debug_image={self.publish_debug_image}\n"
            f"  model_path={self.model_path}\n"
            f"  engine_loaded={self._engine_loaded}\n"
            f"  confidence_threshold={self.confidence_threshold}\n"
            f"  iou_threshold={self.iou_threshold}\n"
            f"  imgsz={self.imgsz}\n"
            f"  sync_slop_sec={self.sync_slop_sec}\n"
            f"  filter_enabled={self.filter_enabled}\n"
            f"  filter_params={self.filter_params}"
        )

    # ── Engine loading (Jetson-only path; safe no-op on dev PC) ──────
    def _try_load_engine(self) -> None:
        if not self.model_path or not os.path.exists(self.model_path):
            self.get_logger().warn(
                f"TensorRT engine not found at {self.model_path!r}. "
                "Node will run in no-inference fallback mode "
                "(publishes empty detections)."
            )
            return
        try:
            import tensorrt as trt  # noqa: F401
            import pycuda.driver as cuda  # noqa: F401
            import pycuda.autoinit  # noqa: F401
        except Exception as exc:  # ImportError on dev PC
            self.get_logger().warn(
                f"TensorRT/pycuda import failed ({exc}); node will run in "
                "no-inference fallback mode."
            )
            return

        try:
            import tensorrt as trt
            import pycuda.driver as cuda

            trt_logger = trt.Logger(trt.Logger.WARNING)
            with open(self.model_path, "rb") as f:
                engine_bytes = f.read()
            self._engine = trt.Runtime(trt_logger).deserialize_cuda_engine(engine_bytes)
            if self._engine is None:
                raise RuntimeError("engine deserialization returned None")
            self._ctx = self._engine.create_execution_context()
            self._trt_in_name = self._engine.get_tensor_name(0)
            self._trt_out_name = self._engine.get_tensor_name(1)
            self._trt_in_shape = tuple(self._engine.get_tensor_shape(self._trt_in_name))
            self._trt_out_shape = tuple(self._engine.get_tensor_shape(self._trt_out_name))
            in_dtype = trt.nptype(self._engine.get_tensor_dtype(self._trt_in_name))
            out_dtype = trt.nptype(self._engine.get_tensor_dtype(self._trt_out_name))
            self._in_host = cuda.pagelocked_empty(int(np.prod(self._trt_in_shape)), in_dtype)
            self._out_host = cuda.pagelocked_empty(int(np.prod(self._trt_out_shape)), out_dtype)
            self._in_dev = cuda.mem_alloc(self._in_host.nbytes)
            self._out_dev = cuda.mem_alloc(self._out_host.nbytes)
            self._bindings = [int(self._in_dev), int(self._out_dev)]
            self._stream = cuda.Stream()
            self._engine_loaded = True
            self.get_logger().info(
                f"TensorRT engine loaded: in={self._trt_in_name} "
                f"{self._trt_in_shape}  out={self._trt_out_name} "
                f"{self._trt_out_shape}"
            )
        except Exception as exc:
            self.get_logger().error(
                f"TensorRT engine load failed for {self.model_path!r}: {exc}"
            )
            self._engine_loaded = False

    # ── Camera-info one-shot ─────────────────────────────────────────
    def _camera_info_cb(self, msg: CameraInfo) -> None:
        if self._got_camera_info:
            return
        # Update intrinsics from the live camera_info. ROS CameraInfo's K is
        # row-major [fx, 0, cx, 0, fy, cy, 0, 0, 1]. The field may be a
        # numpy array or a plain list — coerce to list first.
        try:
            k_list = list(msg.k)
        except TypeError:
            k_list = []
        if len(k_list) >= 9:
            fx = float(k_list[0]); fy = float(k_list[4])
            cx = float(k_list[2]); cy = float(k_list[5])
            if fx > 1.0 and fy > 1.0:
                self.filter_params["fx"] = fx
                self.filter_params["fy"] = fy
                self.filter_params["cx"] = cx
                self.filter_params["cy"] = cy
                self.get_logger().info(
                    f"Camera intrinsics from {self.rgb_camera_info_topic}: "
                    f"fx={fx:.2f} fy={fy:.2f} cx={cx:.2f} cy={cy:.2f}"
                )
        self._got_camera_info = True
        # We don't unsubscribe — the topic rate is low and the early-return
        # in this callback makes it free.

    # ── Synchronised RGB + depth callback ────────────────────────────
    def _sync_cb(self, rgb_msg: Image, depth_msg: Image) -> None:
        self._sync_count += 1
        t_frame0 = time.perf_counter()

        try:
            rgb = self.bridge.imgmsg_to_cv2(rgb_msg, desired_encoding="bgr8")
            depth_mm = self.bridge.imgmsg_to_cv2(
                depth_msg, desired_encoding="passthrough"
            )
        except CvBridgeError as exc:
            if not self._warned_bridge_error:
                self.get_logger().warn(f"CvBridge conversion failed: {exc}")
                self._warned_bridge_error = True
            return

        if depth_mm is None or depth_mm.dtype != np.uint16 or depth_mm.ndim != 2:
            # Depth must be uint16 mm per the M4c1 evidence gate. Skip frame.
            return

        # ── Inference ────────────────────────────────────────────────
        yolo_ms = 0.0
        detections: list[tuple[str, float, tuple[float, float, float, float]]] = []
        if self._engine_loaded:
            detections, yolo_ms = self._infer(rgb)
        # else: empty detections list (no-inference fallback)

        # ── Geometry filter (only on KEEP candidates) ────────────────
        kept: list[CubeDetection] = []
        filter_ms_total = 0.0
        for class_name, conf, box in detections:
            x1, y1, x2, y2 = [int(round(v)) for v in box]
            if not self.filter_enabled:
                kept.append(CubeDetection(class_name=class_name, score=conf,
                                          box=box, reason="filter_disabled"))
                continue
            t_f0 = time.perf_counter()
            stats = compute_geometry(depth_mm, x1, y1, x2, y2, self.filter_params)
            verdict, reason = decide(stats, self.filter_params)
            filter_ms_total += (time.perf_counter() - t_f0) * 1000.0
            if verdict == "KEEP":
                kept.append(CubeDetection(class_name=class_name, score=conf,
                                          box=box, reason=reason))
            else:
                # Map reject-reason strings to a small canonical set for the
                # summary stats surfaced back to the operator.
                bucket = "other"
                for tag in ("flat", "aspect", "no_planar_top",
                            "low_raised_frac", "high_planar_std"):
                    if reason.startswith(tag):
                        bucket = tag
                        break
                self._reject_counts[bucket] = self._reject_counts.get(bucket, 0) + 1

        # ── Publish ──────────────────────────────────────────────────
        self._publish_outputs(rgb_msg, rgb, kept)
        self._publish_count += 1

        # ── Latency bookkeeping + periodic log ──────────────────────
        total_ms = (time.perf_counter() - t_frame0) * 1000.0
        self._total_ms_window.append(total_ms)
        self._yolo_ms_window.append(yolo_ms)
        self._filter_ms_window.append(filter_ms_total)
        self._frame_count += 1
        if self._frame_count % max(1, self.latency_log_every) == 0:
            self._log_latency_summary()

    def _infer(self, rgb: np.ndarray):
        """Run the TensorRT engine on a single RGB frame. Returns (dets, yolo_ms)."""
        import pycuda.driver as cuda  # local import for dev-PC fallback

        rgb_rgb = rgb[:, :, ::-1]  # BGR -> RGB for the network
        orig_h, orig_w = rgb_rgb.shape[:2]
        img, r, (pad_l, pad_t) = _letterbox(rgb_rgb, self.imgsz)
        img = img.astype(np.float32) / 255.0
        img = img.transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        img = img[np.newaxis, ...]

        np.copyto(self._in_host, img.ravel())
        cuda.memcpy_htod_async(self._in_dev, self._in_host, self._stream)
        t0 = time.perf_counter()
        self._ctx.execute_async_v2(bindings=self._bindings,
                                   stream_handle=self._stream.handle)
        self._stream.synchronize()
        ms = (time.perf_counter() - t0) * 1000.0
        cuda.memcpy_dtoh_async(self._out_host, self._out_dev, self._stream)
        self._stream.synchronize()
        out = self._out_host.reshape(self._trt_out_shape)
        dets = _decode_yolov5_output(
            out, self.confidence_threshold, self.iou_threshold,
            (orig_w, orig_h), r, (pad_l, pad_t),
        )
        return dets, ms

    # ── Output helpers ───────────────────────────────────────────────
    def _publish_outputs(self, rgb_msg: Image, rgb: np.ndarray,
                         kept: List[CubeDetection]) -> None:
        self.detections_pub.publish(self._to_detection_array_msg(rgb_msg, kept))
        if self.vendor_objects_pub is not None:
            self.vendor_objects_pub.publish(self._to_vendor_objects_msg(rgb_msg, kept))
        if self.debug_image_pub is not None:
            debug = self._to_debug_image_msg(rgb_msg, rgb, kept)
            if debug is not None:
                self.debug_image_pub.publish(debug)

    def _to_detection_array_msg(self, image_msg: Image,
                                detections: Iterable[CubeDetection]) -> Detection2DArray:
        out = Detection2DArray()
        out.header = image_msg.header
        out.detections = [self._to_detection2d_msg(image_msg, d) for d in detections]
        return out

    def _to_detection2d_msg(self, image_msg: Image, d: CubeDetection) -> Detection2D:
        x_min, y_min, x_max, y_max = [float(v) for v in d.box]
        msg = Detection2D()
        msg.header = image_msg.header
        hyp = ObjectHypothesisWithPose()
        hyp.hypothesis.class_id = d.class_name
        hyp.hypothesis.score = float(d.score)
        msg.results.append(hyp)
        msg.bbox.center.position.x = (x_min + x_max) / 2.0
        msg.bbox.center.position.y = (y_min + y_max) / 2.0
        msg.bbox.size_x = max(0.0, x_max - x_min)
        msg.bbox.size_y = max(0.0, y_max - y_min)
        return msg

    def _to_vendor_objects_msg(self, image_msg: Image,
                               detections: Iterable[CubeDetection]) -> ObjectsInfo:
        out = ObjectsInfo()
        out.objects = [self._to_vendor_object_msg(image_msg, d) for d in detections]
        return out

    def _to_vendor_object_msg(self, image_msg: Image, d: CubeDetection) -> ObjectInfo:
        msg = ObjectInfo()
        msg.class_name = d.class_name
        msg.box = [int(round(v)) for v in d.box]
        msg.score = float(d.score)
        msg.width = int(image_msg.width)
        msg.height = int(image_msg.height)
        return msg

    def _to_debug_image_msg(self, image_msg: Image, rgb: np.ndarray,
                            detections: List[CubeDetection]) -> Optional[Image]:
        try:
            from PIL import Image as PILImage, ImageDraw, ImageFont
            pil = PILImage.fromarray(rgb[:, :, ::-1])  # BGR -> RGB
            draw = ImageDraw.Draw(pil)
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13
                )
            except OSError:
                font = ImageFont.load_default()
            for d in detections:
                x1, y1, x2, y2 = [int(round(v)) for v in d.box]
                color = CLASS_COLORS.get(d.class_name, (255, 255, 0))
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                label = f"{d.class_name} {d.score:.2f} {d.reason[:18]}"
                draw.text((x1, max(0, y1 - 16)), label, fill=color, font=font)
            # HUD strip
            draw.rectangle([0, 0, pil.width, 18], fill=(0, 0, 0))
            hud = (
                f"M5 | conf>={self.confidence_threshold:.2f} | "
                f"filter={'on' if self.filter_enabled else 'off'} | "
                f"keep={len(detections)}"
            )
            draw.text((4, 2), hud, fill=(255, 255, 255), font=font)
            bgr = np.array(pil)[:, :, ::-1]
            out = self.bridge.cv2_to_imgmsg(bgr, encoding="bgr8")
            out.header = image_msg.header
            return out
        except CvBridgeError as exc:
            if not self._warned_bridge_error:
                self.get_logger().warn(f"debug image conversion failed: {exc}")
                self._warned_bridge_error = True
            return None

    # ── Latency summary ─────────────────────────────────────────────
    def _log_latency_summary(self) -> None:
        if not self._total_ms_window:
            return
        total = np.array(self._total_ms_window)
        yolo = np.array(self._yolo_ms_window)
        flt = np.array(self._filter_ms_window)
        self.get_logger().info(
            f"latency over last {len(total)} frames  "
            f"total ms: median={np.median(total):.1f}  p95={np.percentile(total, 95):.1f}  "
            f"yolo ms: median={np.median(yolo):.1f}  p95={np.percentile(yolo, 95):.1f}  "
            f"filter ms/frame: median={np.median(flt):.2f}  "
            f"sync={self._sync_count}  publishes={self._publish_count}  "
            f"rejects={self._reject_counts}"
        )
        # Reset windows so we always report over the last N frames.
        self._total_ms_window.clear()
        self._yolo_ms_window.clear()
        self._filter_ms_window.clear()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CubeDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Final latency dump so the operator gets one last log line on Ctrl-C.
        node._log_latency_summary()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()