import os
from launch import LaunchDescription
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import ExecuteProcess
import launch

def generate_launch_description():
    # ====================== 【只需修改这里】 ======================
    package_name = "qxwy_description" # "你的功能包名"  
    model_file_name = "qxwy.urdf.xacro" # "你的模型.xacro"  # 可填 xacro / urdf / sdf
    model_subfolder = "urdf/qxwy" # 模型所在文件夹
    world_file_name = "custom_room.sdf" # Gazebo 世界文件
    world_subfolder = "world" # 世界文件所在文件夹
    robot_name = "qxwy" # 机器人名字
    # ==============================================================

    # 模型路径
    pkg_share = FindPackageShare(package=package_name).find(package_name)
    model_path = PathJoinSubstitution([pkg_share, model_subfolder, model_file_name])
    world_path = PathJoinSubstitution([pkg_share, world_subfolder, world_file_name])

    # ==============================================
    # 自动判断：xacro 转 URDF，其他直接读取
    # ==============================================
    if model_file_name.endswith('.xacro'):
        robot_description = Command(['xacro ', model_path])
    else:
        robot_description = Command(['cat ', model_path])

    # ==============================================
    # 加载gazebo,及世界文件
    # ==============================================
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r',world_path],
        output='screen'
    )

    # 自动开始模拟
    start_simulation = ExecuteProcess(
        cmd=['gz', 'service', '-s', '/world/custom_room/control', '--reqtype', 'gz.msgs.Empty', '--reptype', 'gz.msgs.Empty', '--timeout', '3000', '--req', '{}'],
        output='screen'
    )

    # 机器人状态发布
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": ParameterValue(robot_description, value_type=str)}]
    )

    # 加载模型到 Gazebo
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-string", robot_description,
            "-name", robot_name,
            "-x", "0.0", "-y", "0.0", "-z", "0.0"
        ],
        output="screen"
    )

    cmd_entity = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry@ignition.msgs.Odometry",
            "/tf@tf2_msgs/msg/TFMessage@ignition.msgs.Pose_V",
            # Camera topics
        ],
        parameters=[{"use_sim_time": True}],
        output="screen"
    )

    # 推荐：动态发布 odom → base_link（从 /odom 话题计算）这个不行
    # ekf_node = Node(
    #     package="robot_localization",
    #     executable="ekf_node",
    #     name="ekf_filter_node",
    #     output="screen",
    #     parameters=[{
    #         "use_sim_time": True,
    #         "odom0": "/odom",
    #         "odom0_config": [True, True, False, False, False, True, False, False, False, False, False, False, False, False, False],
    #         "odom0_queue_size": 10,
    #     }]
    # )

    # 正确：ROS 2 Jazzy 从 /odom 发布 odom -> base_link TF
    odom_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="odom_static_broadcaster",
        arguments=["0", "0", "0", "0", "0", "0", "odom", "base_footprint"],
        parameters=[{"use_sim_time": True}],
        output="screen"
    )

    # 正确：ROS 2 Jazzy 从 /lidar 发布 lidar -> base_link TF
    laser_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "0", "0", "0.1",    # x y z
            "0", "0", "0",      # rpy
            "base_link",        # 父 frame
            "qxwy/base_footprint/gpu_lidar"  #可通过ros2 topic echo /lidar 查看雷达frame_id
        ],
        parameters=[{"use_sim_time": True}],
        output="screen"
    )


    

    # 正确的 joint_state_publisher（必须带 robot_description）
    # joint_state_publisher = Node(
    #     package="joint_state_publisher",
    #     executable="joint_state_publisher",
    #     name="joint_state_publisher",
    #     output="screen",
    #     parameters=[
    #         {"use_sim_time": True},
    #         {"robot_description": f"$(find-xacro {model_path})"}
    #     ]
    # )

    # ==============================================
    # 🔥 🔥 🔥 官方标准桥接（完全遵循 Gazebo 文档）--
    # 普通相机
    # ==============================================
    camera_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera@sensor_msgs/msg/Image@gz.msgs.Image',
            #'/camera/depth@sensor_msgs/msg/Image@gz.msgs.Image', #这个没用
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'
        ],
        output='screen'
    )

    # 深度相机
    depth_camera_bridge  = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/depth_camera'],
        output='screen',
        parameters=[{"use_sim_time": True}], 
    )

    # 5. 根据topcic加载相机（已经加载spawn_entity ）
    depth_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'depth_camera', '-topic', 'robot_description'],#, '-x', '4', '-y', '0', '-z', '1.0', '-R', '0', '-P', '0', '-Y', '3.14'],
        output='screen'
    )

    # 加载 joint_state_broadcaster 控制器
    action_load_joint_state_controller = launch.actions.ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', 'qxwy_joint_state_broadcaster', '--set-state', 'active'],
        output='screen'
    )

    # 配置 joint_state_broadcaster 控制器
    # action_configure_joint_state_controller = launch.actions.ExecuteProcess(
    #     cmd=['ros2 control set_controller_state', 'qxwy_joint_state_broadcaster', 'active'],
    #     output='screen'
    # )

    # 加载 diff_drive_controller 控制器
    action_load_diff_drive_controller = launch.actions.ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', 'qxwy_diff_drive_controller', '--set-state', 'active'],
        output='screen'
    )

    # 配置 diff_drive_controller 控制器
    # action_configure_diff_drive_controller = launch.actions.ExecuteProcess(
    #     cmd=['ros2', 'control', 'set_controller_state', 'qxwy_diff_drive_controller', 'active'],
    #     output='screen'
    # )

    # Twist to TwistStamped converter for teleop_twist_keyboard
    twist_converter = Node(
        package='qxwy_description',
        executable='twist_to_twist_stamped.py',
        name='twist_to_twist_stamped',
        output='screen',
        parameters=[{"use_sim_time": True}]
    )

    # 获取脚本路径
    pkg_share = FindPackageShare(package=package_name).find(package_name)
    twist2stamped_script = os.path.join(pkg_share, 'scripts', 'twist2stamped.py')

    # Twist to TwistStamped converter for navigation2
    twist2stamped_node = ExecuteProcess(
        cmd=['python3', twist2stamped_script],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        camera_bridge,
        depth_camera_bridge,
        robot_state_publisher,
        # joint_state_publisher,
        spawn_entity,
        # cmd_entity,  # 注释掉，与diff_drive_controller冲突
        #depth_entity,
        odom_tf_node,
        laser_tf_node,
        # 延迟开始模拟，确保Gazebo已经完全启动
        launch.actions.TimerAction(
            period=2.0,
            actions=[start_simulation]
        ),
        # 延迟加载控制器，确保模拟已经开始
        launch.actions.TimerAction(
            period=7.0,  # 增加延迟时间，确保模拟已经开始
            actions=[
                action_load_joint_state_controller,
                action_load_diff_drive_controller
            ]
        ),
        # 启动话题转换脚本
        twist2stamped_node
    ])