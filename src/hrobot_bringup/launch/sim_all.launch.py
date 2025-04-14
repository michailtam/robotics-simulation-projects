import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Paths
    robot_bringup_pkg = FindPackageShare('hrobot_bringup')
    robot_gazebo_pkg = FindPackageShare('hrobot_gazebo')

    # Executes the robot state publisher, joint state publisher and rviz 
    launch_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                robot_bringup_pkg, 
                'launch', 
                'display.launch.py'])
        )
    )

    # Spawns the robot in Gazebo 
    spawn_robot_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                robot_gazebo_pkg, 
                'launch', 
                'spawn.launch.py'])
        )
    )
    
    # Return the full launch description
    return LaunchDescription([
        launch_robot,
        spawn_robot_gazebo
    ])
