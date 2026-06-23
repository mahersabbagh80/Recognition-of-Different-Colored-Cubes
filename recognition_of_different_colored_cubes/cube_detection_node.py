#!/usr/bin/env python3
"""ROS 2 node scaffold for vendor-aligned colored cube detection.

The node owns the project-specific perception graph only. Camera bring-up stays
in the HiWonder/vendor stack, normally publishing ``/depth_cam/rgb/image_raw``.

Full YOLOv5/TensorRT inference is intentionally not implemented in this card:
model artifacts and runtime backend setup are later milestones. Until then the
node republishes an empty detection set plus a debug image pass-through so the
ROS graph, message contracts, and launch/config wiring can be verified.
"""

from dataclasses import dataclass
from typing import Iterable, List, Sequence

import rclpy
from cv_bridge import CvBridge, CvBridgeError
from interfaces.msg import ObjectInfo, ObjectsInfo
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose


@dataclass(frozen=True)
class CubeDetection:
    """Internal detection representation shared by all output converters.

    Bounding boxes use image-pixel corners: ``x_min, y_min, x_max, y_max``.
    """

    class_name: str
    score: float
    box: Sequence[float]


class CubeDetectionNode(Node):
    """Subscribe to camera and publish standard + vendor detection outputs."""

    def __init__(self):
        super().__init__('cube_detection_node')

        self.declare_parameter('image_topic', '/depth_cam/rgb/image_raw')
        self.declare_parameter('detections_topic', '/cube_detections')
        self.declare_parameter('debug_image_topic', '/cube_detections/debug_image')
        self.declare_parameter('vendor_objects_topic', '/cube_detections/vendor_objects')
        self.declare_parameter('publish_vendor_objects', True)
        self.declare_parameter('publish_debug_image', True)
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('model_path', '')

        self.image_topic = self.get_parameter('image_topic').value
        self.detections_topic = self.get_parameter('detections_topic').value
        self.debug_image_topic = self.get_parameter('debug_image_topic').value
        self.vendor_objects_topic = self.get_parameter('vendor_objects_topic').value
        self.publish_vendor_objects = self.get_parameter('publish_vendor_objects').value
        self.publish_debug_image = self.get_parameter('publish_debug_image').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.model_path = self.get_parameter('model_path').value

        self.bridge = CvBridge()
        self._warned_bridge_error = False
        self._warned_placeholder = False

        self.detections_pub = self.create_publisher(
            Detection2DArray,
            self.detections_topic,
            10,
        )
        self.vendor_objects_pub = None
        if self.publish_vendor_objects:
            self.vendor_objects_pub = self.create_publisher(
                ObjectsInfo,
                self.vendor_objects_topic,
                10,
            )
        self.debug_image_pub = None
        if self.publish_debug_image:
            self.debug_image_pub = self.create_publisher(
                Image,
                self.debug_image_topic,
                10,
            )

        self.image_sub = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            qos_profile_sensor_data,
        )

        self.get_logger().info(
            'cube_detection_node started: '
            f'image_topic={self.image_topic}, '
            f'detections_topic={self.detections_topic}, '
            f'vendor_objects_topic={self.vendor_objects_topic}, '
            f'publish_vendor_objects={self.publish_vendor_objects}, '
            f'debug_image_topic={self.debug_image_topic}, '
            f'publish_debug_image={self.publish_debug_image}, '
            f'confidence_threshold={self.confidence_threshold}, '
            f'model_path="{self.model_path}"'
        )

    def image_callback(self, msg: Image) -> None:
        """Process one image and publish all configured scaffold outputs."""
        detections = self.run_inference_placeholder(msg)

        self.detections_pub.publish(self.to_detection_array_msg(msg, detections))

        if self.vendor_objects_pub is not None:
            self.vendor_objects_pub.publish(self.to_vendor_objects_msg(msg, detections))

        if self.debug_image_pub is not None:
            debug_msg = self.to_debug_image_msg(msg, detections)
            if debug_msg is not None:
                self.debug_image_pub.publish(debug_msg)

    def run_inference_placeholder(self, msg: Image) -> List[CubeDetection]:
        """Return no detections until the YOLOv5/TensorRT backend is ready.

        Keeping this placeholder explicit lets the package verify ROS 2 topics,
        parameters, QoS, and message dependencies without pretending model
        inference exists before weights/engines are available.
        """
        if not self._warned_placeholder:
            self.get_logger().warn(
                'Inference backend is not implemented yet; publishing empty '
                'Detection2DArray and ObjectsInfo scaffold messages.'
            )
            self._warned_placeholder = True

        # Touch the input through CvBridge so bridge/runtime wiring is exercised
        # during graph tests. The converted frame will be used by real inference
        # and debug overlays in a later milestone.
        try:
            self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except CvBridgeError as exc:
            if not self._warned_bridge_error:
                self.get_logger().warn(f'CvBridge conversion failed: {exc}')
                self._warned_bridge_error = True

        return []

    def to_detection_array_msg(
        self,
        image_msg: Image,
        detections: Iterable[CubeDetection],
    ) -> Detection2DArray:
        """Convert internal detections to the standard ROS vision output."""
        output = Detection2DArray()
        output.header = image_msg.header
        output.detections = [self.to_detection2d_msg(image_msg, det) for det in detections]
        return output

    def to_detection2d_msg(self, image_msg: Image, detection: CubeDetection) -> Detection2D:
        """Convert one detection to ``vision_msgs/Detection2D``."""
        x_min, y_min, x_max, y_max = [float(value) for value in detection.box]
        center_x = (x_min + x_max) / 2.0
        center_y = (y_min + y_max) / 2.0

        msg = Detection2D()
        msg.header = image_msg.header
        hypothesis = ObjectHypothesisWithPose()
        hypothesis.hypothesis.class_id = detection.class_name
        hypothesis.hypothesis.score = float(detection.score)
        msg.results.append(hypothesis)
        msg.bbox.center.position.x = center_x
        msg.bbox.center.position.y = center_y
        msg.bbox.size_x = max(0.0, x_max - x_min)
        msg.bbox.size_y = max(0.0, y_max - y_min)
        return msg

    def to_vendor_objects_msg(
        self,
        image_msg: Image,
        detections: Iterable[CubeDetection],
    ) -> ObjectsInfo:
        """Convert internal detections to HiWonder ``interfaces/ObjectsInfo``."""
        output = ObjectsInfo()
        output.objects = [self.to_vendor_object_msg(image_msg, det) for det in detections]
        return output

    def to_vendor_object_msg(self, image_msg: Image, detection: CubeDetection) -> ObjectInfo:
        """Convert one detection to the vendor object-message shape."""
        msg = ObjectInfo()
        msg.class_name = detection.class_name
        msg.box = [int(round(value)) for value in detection.box]
        msg.score = float(detection.score)
        msg.width = int(image_msg.width)
        msg.height = int(image_msg.height)
        return msg

    def to_debug_image_msg(
        self,
        image_msg: Image,
        detections: Iterable[CubeDetection],
    ) -> Image | None:
        """Return a debug image pass-through until overlay drawing is added."""
        del detections  # Real overlay drawing belongs with the inference backend.
        try:
            frame = self.bridge.imgmsg_to_cv2(image_msg, desired_encoding='bgr8')
            debug_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            debug_msg.header = image_msg.header
            return debug_msg
        except CvBridgeError as exc:
            if not self._warned_bridge_error:
                self.get_logger().warn(f'CvBridge debug image conversion failed: {exc}')
                self._warned_bridge_error = True
            return None


def main(args=None):
    rclpy.init(args=args)
    node = CubeDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
