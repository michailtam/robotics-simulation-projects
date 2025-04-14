import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    # Gazebo (Ignition/GZ) simulator launch
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ),
        launch_arguments={
            'gz_args': ['-r -v 4 empty.sdf --physics-engine gz-physics-bullet-featherstone-plugin']
        }.items()
    )

    # Spawn the robot into the Gazebo simulation
    spawn_entity = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=['-topic', 'robot_description', '-entity', 'pepper'],
                output='screen'
            )
        ]
    )

    # Return the full launch description
    return LaunchDescription([
        gazebo_launch,
        spawn_entity
    ])
