import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    autopilot_robot_path = get_package_share_directory('autopilot_robot')
    autopilot_robot_config_path = os.path.join(autopilot_robot_path,'config','pilot_config.yaml')
    
    action_pilot_node = launch_ros.actions.Node(
        package='autopilot_robot',
        executable='pilot_node',
        parameters=[autopilot_robot_config_path],
        output='screen'
    )

    action_speaker_node = launch_ros.actions.Node(
        package='autopilot_robot',
        executable='speaker',
        output='screen'
    )

    return launch.LaunchDescription([
        action_pilot_node,
        action_speaker_node
    ])