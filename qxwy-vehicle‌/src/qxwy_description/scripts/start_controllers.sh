#!/bin/bash

# 等待控制器管理器启动
echo "等待控制器管理器启动..."
while ! ros2 control list_controllers 2>/dev/null | grep -q "controller_manager"; do
    sleep 1
done

echo "控制器管理器已启动，正在加载控制器..."

# 启动关节状态广播器
ros2 run controller_manager spawner qxwy_joint_state_broadcaster &
sleep 2

# 启动差速驱动控制器
ros2 run controller_manager spawner qxwy_diff_drive_controller &
sleep 2

echo "所有控制器已启动！"
echo "运行 'ros2 control list_controllers' 查看控制器状态"