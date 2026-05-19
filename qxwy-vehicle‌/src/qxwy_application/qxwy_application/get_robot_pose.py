import rclpy
from rclpy.node import Node
import rclpy.time
from tf2_ros import TransformListener,Buffer # 坐标监听器
from tf_transformations import euler_from_quaternion # 四元数转欧拉角函数
import math # 角度转弧度函数

class TFBroadcaster(Node):
    def __init__(self):
        super().__init__('tf_broadcaster')
        self.buffer_ = Buffer()
        self.listener_ = TransformListener(self.buffer_,self)
        self.timer_ = self.create_timer(1.0,self.get_transform)

    def get_transform(self):
        """
        实时查询坐标关系 buffer_
        """
        try:
            result = self.buffer_.lookup_transform('map','base_footprint',
                rclpy.time.Time(seconds=0.0),rclpy.time.Duration(seconds=1.0))
            transform = result.transform
            self.get_logger().info(f'平移:{transform.translation}')
            self.get_logger().info(f'旋转:{transform.rotation}')
            rotation_euler = euler_from_quaternion([
                transform.rotation.x,
                transform.rotation.y,
                transform.rotation.z,
                transform.rotation.w])
            self.get_logger().info(f'旋转RPY:{rotation_euler}')
        except Exception as e:
            self.get_logger().error(f'查询坐标关系失败:{str(e)}')

def main():
    rclpy.init()
    tf_broadcaster = TFBroadcaster()
    rclpy.spin(tf_broadcaster)
    rclpy.shutdown()
