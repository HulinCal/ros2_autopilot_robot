from setuptools import find_packages, setup

package_name = 'qxwy_application'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hl',
    maintainer_email='hl@todo.todo',
    description='TODO: Package description',
    license='Apache2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'init_robot_pose = qxwy_application.init_robot_pose:main',
            'get_robot_pose = qxwy_application.get_robot_pose:main',
            'nav_to_pose = qxwy_application.nav_to_pose:main',
            'waypoint_follower = qxwy_application.waypoint_follower:main',
        ],
    },
)
