#!/usr/bin/env python3
"""ROS 2 node for YOLOv5 + TensorRT colored cube detection."""

import rclpy
from rclpy.node import Node

# from cv_bridge import CvBridge
# from sensor_msgs.msg import Image
# from vision_msgs.msg import Detection2DArray


class CubeDetectionNode(Node):
    """Subscribe to camera, run inference, publish detections."""

    def __init__(self):
        super().__init__('cube_detection_node')

        # TODO: declare parameters from config/params.yaml
        # self.declare_parameter('image_topic', '/depth_cam/rgb/image_raw')
        # self.declare_parameter('detections_topic', '/cube_detections')
        # self.declare_parameter('debug_image_topic', '/cube_detections/debug_image')
        # self.declare_parameter('confidence_threshold', 0.5)
        # self.declare_parameter('model_path', '')

        # TODO: CvBridge for ROS Image <-> OpenCV conversion
        # self.bridge = CvBridge()

        # TODO: subscribe to camera image topic
        # self.image_sub = self.create_subscription(
        #     Image, image_topic, self.image_callback, 10)

        # TODO: publishers for detections and debug image
        # self.detections_pub = self.create_publisher(Detection2DArray, detections_topic, 10)
        # self.debug_image_pub = self.create_publisher(Image, debug_image_topic, 10)

        self.get_logger().info('cube_detection_node initialized (scaffold)')

    # def image_callback(self, msg: Image) -> None:
    #     """Process incoming camera frame."""
    #     pass


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
