from geometry_msgs.msg import PoseStamped,Pose
from nav2_simple_commander.robot_navigator import BasicNavigator,TaskResult
import rclpy
from rclpy.node import Node
import rclpy.time
from tf2_ros import TransformListener,Buffer # 坐标监听器
from tf_transformations import euler_from_quaternion,quaternion_from_euler # 四元数转欧拉角函数
import math # 角度转弧度函数
from autopilot_interfaces.srv import SpeachText
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class PilotNode(BasicNavigator):
    def __init__(self,node_name='pilot_node'):
        super().__init__(node_name)

        # 声明参数
        self.declare_parameter('initial_point',[0.0,0.0,0.0])
        self.declare_parameter('target_point',[0.0,0.0,0.0,1.0,1.0,1.57])

        # 从参数服务器获取参数
        self.initial_point_ = self.get_parameter('initial_point').value
        self.target_point_ = self.get_parameter('target_point').value

        self.buffer_ = Buffer()
        self.listener_ = TransformListener(self.buffer_,self)

        self.speaker_client_ = self.create_client(SpeachText, '/speach_text')
        
        self.declare_parameter('image_save_path','')
        self.image_save_path_ = self.get_parameter('image_save_path').value

        self.cv_brige_ = CvBridge()

        self.latest_image_ = None

        self.image_sub_ = self.create_subscription(Image, '/depth_camera', self.image_callback, 1) # 深度相机订阅
        # self.image_sub_ = self.create_subscription(Image, '/camera', self.image_callback, 1) # 相机订阅

    def image_callback(self, msg):
        self.latest_image_ = msg

    def record_image(self):
        """
        记录图片
        """
        if self.latest_image_ is not None:
            pose = self.get_current_pose()
            self.get_logger().info(f'当前位姿: {pose}')
            save_path = f'{self.image_save_path_}image_{pose.translation.x:3.2f}_{pose.translation.y:3.2f}_{pose.translation.z:3.2f}.png'

            if self.latest_image_.encoding == 'rgb8' or self.latest_image_.encoding == 'bgr8':
                cv_image = self.cv_brige_.imgmsg_to_cv2(self.latest_image_)
                cv2.imwrite(save_path, cv_image)
            else:
                cv_image = self.cv_brige_.imgmsg_to_cv2(self.latest_image_, desired_encoding="32FC1")
                cv_image_mm = (cv_image * 1000).astype(np.uint16)
                # 归一化到0-255，应用色彩映射
                vis_image = cv2.normalize(cv_image_mm, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                #vis_image = cv2.applyColorMap(vis_image, cv2.COLORMAP_JET)
                cv2.imwrite(save_path, vis_image)
            
            self.get_logger().info(f'图片已保存到 {save_path}-原始图片类型:{self.latest_image_.encoding}')
        else:
            self.get_logger().info(f'当前没有图片')

    def get_pose_by_xyyaw(self,x,y,yaw):
        """
        根据x,y,yaw获取PoseStamped
        """
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = "map"
        goal_pose.header.stamp = self.get_clock().now().to_msg()

        # 返回顺序是x,y,z,w
        from geometry_msgs.msg import Point, Quaternion
        quat = quaternion_from_euler(0.0,0.0,yaw)
        goal_pose.pose.position = Point(x=x, y=y, z=0.0)
        goal_pose.pose.orientation = Quaternion(x=quat[0], y=quat[1], z=quat[2], w=quat[3])
        return goal_pose

    def init_robot_pose(self):
        """
        初始化机器人位姿
        """
        # 检查参数是否存在
        if self.has_parameter('initial_point'):
            self.get_logger().info(f'初始位置参数 initial_point 存在:{self.get_parameter("initial_point").value}')
        else:
            self.get_logger().info(f'参数 initial_point 不存在')
        
        # 获取参数值（使用相对路径）
        self.initial_point_ = self.get_parameter('initial_point').value
        self.get_logger().info(f'使用相对路径获取到的初始位置参数: {self.get_parameter('initial_point').value}')

        init_pose = self.get_pose_by_xyyaw(self.initial_point_[0], self.initial_point_[1], self.initial_point_[2])
        self.get_logger().info(f'初始位置x-y-w: {self.initial_point_[0]}, {self.initial_point_[1]}, {self.initial_point_[2]}')

        self.setInitialPose(init_pose)

        self.waitUntilNav2Active()

    def get_target_points(self):
        """
        获取目标点
        """
        # 检查参数是否存在
        if self.has_parameter('target_point'):
            self.get_logger().info(f'目标点参数 target_point 存在:{self.get_parameter("target_point").value}')
        else:
            self.get_logger().info(f'参数 target_point 不存在')

        points = []
        self.target_point_ = self.get_parameter('target_point').value
        for index in range(0,int(len(self.target_point_)/3)):
            x = self.target_point_[index*3]
            y = self.target_point_[index*3+1]
            yaw = self.target_point_[index*3+2]
            points.append(self.get_pose_by_xyyaw(x,y,yaw))
            self.get_logger().info(f'获取到目标点{index}->{x},{y},{yaw}')

        return points
    
    def nav_to_pose(self,target_point):
        """
        导航到目标点
        """
        self.goToPose(target_point)

        while not self.isTaskComplete():
            feedback = self.getFeedback()
            self.get_logger().info(f'剩余距离：{feedback.distance_remaining}')
            #self.cancelTask()

        result = self.getResult()
        self.get_logger().info(f'导航完成：{result}')

    def get_current_pose(self):
        """
        获取当前位姿
        """
        while rclpy.ok():
            try:
                result = self.buffer_.lookup_transform('map','base_footprint',
                    rclpy.time.Time(seconds=0.0),rclpy.time.Duration(seconds=1.0))
                transform = result.transform
                # self.get_logger().info(f'平移:{transform.translation}')
                # self.get_logger().info(f'旋转:{transform.rotation}')
                # rotation_euler = euler_from_quaternion([
                #     transform.rotation.x,
                #     transform.rotation.y,
                #     transform.rotation.z,
                #     transform.rotation.w])
                # self.get_logger().info(f'旋转RPY:{rotation_euler}')
                return transform
            except Exception as e:
                self.get_logger().error(f'查询坐标关系失败:{str(e)}')

    def speach_text(self,text):
        """
        请求朗读文本服务
        """

        # 等待服务可用
        while not self.speaker_client_.wait_for_service(1.0):
            self.get_logger().warning(f"服务 /speach_text 未可用，等待1秒后重试")

        # 创建请求
        request = SpeachText.Request()
        request.text = text

        # 发送请求
        future = self.speaker_client_.call_async(request)

        # 等待服务响应
        rclpy.spin_until_future_complete(self,future)

        response = future.result()
        if response.result is not None:
            if response.result == True:
                self.get_logger().info(f"朗读完成: {text}")
            else:
                self.get_logger().warn(f"朗读失败: {text}")
        else:
            self.get_logger().warn(f"朗读服务响应失败: {text}")

def main():
    rclpy.init()

    pilot = PilotNode()
    
    pilot.speach_text("正在准备初始化位置！")
    pilot.init_robot_pose()
    pilot.speach_text("初始化位置完成！")

    points = pilot.get_target_points()
    for point in points:
        # pilot.speach_text(f"正在准备导航到目标点{point}")
        pilot.nav_to_pose(point)
        # pilot.speach_text(f"导航到目标点{point}")
        pilot.record_image()

    pilot.speach_text("navigation complete")

    rclpy.shutdown()
