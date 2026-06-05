from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'recognition_of_different_colored_cubes'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Maher Alshirazi Alsabbagh',
    maintainer_email='mahersabbagh80@gmail.com',
    description='Detect and classify differently colored cubes using the JetRover depth camera and ROS 2',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cube_detection_node = recognition_of_different_colored_cubes.cube_detection_node:main',
        ],
    },
)
