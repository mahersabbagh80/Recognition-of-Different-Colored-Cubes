import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('recognition_of_different_colored_cubes')
    params_file = os.path.join(pkg_share, 'config', 'params.yaml')

    cube_detection_node = Node(
        package='recognition_of_different_colored_cubes',
        executable='cube_detection_node',
        name='cube_detection_node',
        output='screen',
        parameters=[params_file],
    )

    return LaunchDescription([
        cube_detection_node,
    ])
