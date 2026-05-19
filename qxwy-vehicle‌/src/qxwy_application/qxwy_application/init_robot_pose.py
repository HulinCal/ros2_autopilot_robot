from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

def main():
    rclpy.init()
    navigator = BasicNavigator()

    init_pose = PoseStamped()
    init_pose.header.frame_id = "map"
    init_pose.header.stamp = navigator.get_clock().now().to_msg()
    init_pose.pose.position.x = 0.0
    init_pose.pose.position.y = -0.5
    init_pose.pose.position.z = 0.0
    init_pose.pose.orientation.w = 1.0

    navigator.setInitialPose(init_pose)
    navigator.waitUntilNav2Active()

    rclpy.spin(navigator)
    rclpy.shutdown()

    # navigator.go_to_pose(init_pose)
    # navigator.wait_for_goal()