import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from geometry_msgs.msg import Twist, TwistStamped

class TwistConverter(Node):
    def __init__(self):
        super().__init__('twist_converter')

        # 导航来的速度
        self.sub = self.create_subscription(Twist, '/cmd_vel_nav', self.cb, 10)

        # 🔥 关键：发布时强制 BEST_EFFORT！
        qos = QoSProfile(reliability=QoSReliabilityPolicy.RELIABLE, depth=10)
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', qos)

    def cb(self, msg):
        out = TwistStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = "base_link"
        out.twist = msg
        self.pub.publish(out)

def main():
    rclpy.init()
    node = TwistConverter()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
