#机器人自动驾驶系统
robot view:
![robot view](https://github.com/HulinCal/ros2_autopilot_robot/blob/main/qxwy-vehicle%E2%80%8C/src/assets/robot.png)

lidar image view:
![lidar view](https://github.com/HulinCal/ros2_autopilot_robot/blob/main/qxwy-vehicle%E2%80%8C/src/assets/lidar.png)

rgb image view:
![rgb image view](https://github.com/HulinCal/ros2_autopilot_robot/blob/main/qxwy-vehicle%E2%80%8C/src/assets/color.png)

depth image view:
![depth image view](https://github.com/HulinCal/ros2_autopilot_robot/blob/main/qxwy-vehicle%E2%80%8C/src/assets/depth.png)

navigation1:
![navigation image1 view](https://github.com/HulinCal/ros2_autopilot_robot/blob/main/qxwy-vehicle%E2%80%8C/src/assets/nav.png)

navigation2:
![navigation view](https://github.com/HulinCal/ros2_autopilot_robot/blob/main/qxwy-vehicle%E2%80%8C/src/assets/nav2.git)

## 项目功能

本项目是一个基于ROS 2 jazzy + gazebo harmonic的机器人建图、自动导航，主要功能包括：

1. **机器人仿真**：在Gazebo Harmonic中进行机器人仿真
2. **自动导航**：使用Navigation2框架实现自动导航
3. **路径规划**：自动规划从初始位置到目标点的路径
4. **语音合成**：提供文本转语音功能
5. **图像记录**：在导航过程中记录机器人当前位置的图像
6. **控制器管理**：自动加载和激活机器人控制器

## 系统架构

项目由以下几个主要包组成：

### 1. qxwy_description
- **功能**：机器人模型描述、Gazebo仿真环境配置
- **主要文件**：
  - `urdf/`：机器人URDF模型文件
  - `launch/gazebo_sim.launch.py`：启动Gazebo仿真环境
  - `scripts/twist2stamped.py`：将Twist消息转换为TwistStamped消息

### 2. qxwy_navigation2
- **功能**：Navigation2导航配置
- **主要文件**：
  - `config/nav2_params.yaml`：Navigation2参数配置
  - `launch/navigation2.launch.py`：启动Navigation2导航节点
  - `maps/`：地图文件

### 3. qxwy_application
- **功能**：机器人应用功能
- **主要文件**：
  - `init_robot_pose.py`：初始化机器人位姿
  - `nav_to_pose.py`：导航到目标点
  - `get_robot_pose.py`：获取机器人当前位姿
  - `waypoint_follower.py`：路径点跟随

### 4. autopilot_interfaces
- **功能**：定义服务接口
- **主要文件**：
  - `srv/SpeachText.srv`：语音合成服务接口

### 5. autopilot_robot
- **功能**：自动驾驶核心功能
- **主要文件**：
  - `pilot_node.py`：自动驾驶节点
  - `speaker.py`：语音合成节点
  - `config/pilot_config.yaml`：自动驾驶参数配置
  - `launch/autopilot.launch.py`：启动自动驾驶系统

## 依赖的开发工具

### 1. 系统依赖
- **Ubuntu 24.04**：操作系统
- **ROS 2 Jazzy**：机器人操作系统
- **Gazebo Harmonic**：物理仿真环境
- **Python 3.12**：编程语言

### 2. ROS 2 包依赖
- `nav2_simple_commander`：Navigation2简单命令接口
- `geometry_msgs`：几何消息类型
- `sensor_msgs`：传感器消息类型
- `tf2_ros`：坐标变换
- `cv_bridge`：OpenCV与ROS消息转换
- `autopilot_interfaces`：自定义服务接口

### 3. Python 依赖
- `espeakng`：文本转语音库
- `opencv-python`：图像处理库
- `numpy`：数值计算库

### 4. 其他依赖
- `espeak-ng`：语音合成命令行工具
- `colcon`：ROS 2构建工具

## 安装开发工具

### 1. 安装ROS 2 Jazzy

按照[ROS 2官方文档](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debians.html)安装ROS 2 Jazzy。

### 2. 安装Gazebo Harmonic

```bash
sudo apt-get install gazebo
```

### 3. 安装Python依赖

```bash
# 安装espeak-ng命令行工具
sudo apt-get install espeak-ng

# 安装Python库
pip3 install espeakng opencv-python numpy --break-system-packages
```

### 4. 安装ROS 2 包依赖

```bash
# 安装Navigation2
sudo apt-get install ros-jazzy-navigation2 ros-jazzy-nav2-bringup

# 安装其他依赖包
sudo apt-get install ros-jazzy-tf2-ros ros-jazzy-cv-bridge
```

## 项目安装

1. **克隆项目**

```bash
mkdir -p ~/chapt7/chapt7_ws/src
cd ~/chapt7/chapt7_ws/src
git clone <项目仓库地址>
```

2. **构建项目**

```bash
cd ~/chapt7/chapt7_ws
colcon build
```

3. **设置环境变量**

```bash
source ~/chapt7/chapt7_ws/install/setup.bash
```

## 使用方法

### 1. 启动Gazebo仿真环境

```bash
source install/setup.bash
ros2 launch qxwy_description gazebo_sim.launch.py
```
仿真环境启动后，请在7秒内点击gazebo中的run the simulation按钮，然后才能启动ros2的控制器。
也可以在新的终端手动输入以下指令来启动ros2控制器：
```bash
    ros2 control load_controller qxwy_joint_state_broadcaster --set-state active
    ros2 control load_controller qxwy_diff_drive_controller --set-state active
```

### 2. 启动Navigation2导航

```bash
source install/setup.bash
ros2 launch qxwy_navigation2 navigation2.launch.py
```

### 3. 初始化机器人位姿

```bash
ros2 run qxwy_application init_robot_pose
```

### 4. 导航到目标点

```bash
ros2 run qxwy_application nav_to_pose
```

### 5. 启动自动驾驶系统

```bash
ros2 launch autopilot_robot autopilot.launch.py
```

### 6. 测试语音合成服务

```bash
ros2 service call /speach_text autopilot_interfaces/srv/SpeechText "{text: '你好，欢迎使用千羽机器人'}"
```

## 配置文件说明

### 1. 自动驾驶参数配置 (`autopilot_robot/config/pilot_config.yaml`)

```yaml
/pilot_node:
  ros__parameters:
    initial_point: [0.57, -0.9, 0.0]  # 初始位置 (x, y, yaw)
    target_point: [                    # 目标点列表
      4.4, 1.0, 0.93,
      6.0, -0.4, 0.0,
      1.9, -4.15, 1.0,
      9.0, -2.7, 2.0
    ]
    use_sim_time: false
```

### 2. Navigation2参数配置 (`qxwy_navigation2/config/nav2_params.yaml`)

包含Navigation2的各种参数配置，如控制器参数、规划器参数等。

## 常见问题与解决方案

### 1. 机器人不移动
- **原因**：控制器未激活
- **解决方案**：确保Gazebo仿真已启动，并且控制器已自动加载激活

### 2. 导航失败
- **原因**：机器人位姿初始化错误
- **解决方案**：先运行`init_robot_pose`初始化机器人位姿

### 3. 语音合成失败
- **原因**：缺少espeak-ng依赖
- **解决方案**：安装espeak-ng命令行工具和Python库

### 4. 图片保存失败
- **原因**：未设置图片保存路径
- **解决方案**：在启动自动驾驶节点时设置`image_save_path`参数

## 项目结构

```
qxwy-vehicle‌/
├── build/              # 构建输出目录
├── install/            # 安装目录
├── log/                # 日志目录
├── src/                # 源代码目录
│   ├── autopilot_interfaces/     # 服务接口定义
│   ├── autopilot_robot/          # 自动驾驶核心功能
│   ├── qxwy_application/      # 机器人应用功能
│   ├── qxwy_description/      # 机器人模型描述
│   └── qxwy_navigation2/      # Navigation2导航配置
└── README.md           # 项目说明文档
```

## 注意事项

1. **Gazebo Harmonic**：需要手动点击"Run the simulation"按钮启动仿真（注：已经自动开始模拟，不需要点击）
2. **控制器加载**：系统会在Gazebo启动后自动加载并激活控制器
3. **语音合成**：使用espeak-ng库，支持中文语音
4. **导航路径**：Navigation2会自动规划从初始位置到目标点的路径
5. **图片记录**：在导航到每个目标点后，会记录当前位置的图像

## 技术支持

维护：3352885695@qq.com
