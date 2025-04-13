import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Paths
    description_pkg = FindPackageShare('hrobot_description')
    urdf_path = os.path.join(description_pkg.find('hrobot_description'), 'urdf', 'pepper.urdf.xacro')
    rviz_config_path = os.path.join(description_pkg.find('hrobot_description'), 'rviz', 'urdf_config.rviz')

    # Generate robot description from xacro
    robot_description = ParameterValue(Command(['xacro ', urdf_path]), value_type=str)

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

    # Robot state publisher node
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{'robot_description': robot_description}]
    )

    # Joint state publisher GUI
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui"
    )

    # RViz2 visualization
    rviz2_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=['-d', rviz_config_path],
        output="screen"
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
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz2_node,
        spawn_entity
    ])
