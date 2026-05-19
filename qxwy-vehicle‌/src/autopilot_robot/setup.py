from setuptools import find_packages, setup
from glob import glob

package_name = 'autopilot_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/pilot_config.yaml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hl',
    maintainer_email='hl@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'autopilot_node = autopilot_robot.pilot_node:main',
            'pilot_node = autopilot_robot.pilot_node:main',
            'speaker = autopilot_robot.speaker:main'
        ],
    },
)
