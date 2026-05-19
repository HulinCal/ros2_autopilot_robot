#!/usr/bin/env python3
"""
Twist to TwistStamped message converter
Converts geometry_msgs/msg/Twist to geometry_msgs/msg/TwistStamped
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped

class TwistToTwistStamped(Node):
    def __init__(self):
        super().__init__('twist_to_twist_stamped')
        
        # Subscriber for Twist messages
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.twist_callback,
            10
        )
        
        # Publisher for TwistStamped messages
        self.publisher = self.create_publisher(
            TwistStamped,
            '/qxwy_diff_drive_controller/cmd_vel',
            10
        )
        
        self.get_logger().info('Twist to TwistStamped converter started')
    
    def twist_callback(self, msg):
        # Create TwistStamped message
        twist_stamped = TwistStamped()
        twist_stamped.header.stamp = self.get_clock().now().to_msg()
        twist_stamped.header.frame_id = ''
        twist_stamped.twist = msg
        
        # Publish the converted message
        self.publisher.publish(twist_stamped)

def main(args=None):
    rclpy.init(args=args)
    node = TwistToTwistStamped()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()