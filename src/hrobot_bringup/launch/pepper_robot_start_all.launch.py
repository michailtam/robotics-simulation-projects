import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Paths of the shared packages and files
    pkg_share_bringup = FindPackageShare(package='hrobot_bringup').find('hrobot_bringup')
    pkg_share_gazebo = FindPackageShare(package='hrobot_gazebo').find('hrobot_gazebo')
    
    # Executes the robot state publisher, joint state publisher and rviz 
    launch_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                pkg_share_bringup,
                'launch',
                'pepper_robot.launch.py'])
        )
    )

    # Spawns the robot in Gazebo 
    spawn_robot_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                pkg_share_gazebo, 
                'launch', 
                'spawn.launch.py'])
        )
    )
    
    # Return the full launch description
    return LaunchDescription([
        launch_robot,
        spawn_robot_gazebo,
    ])
