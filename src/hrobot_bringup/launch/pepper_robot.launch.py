import os

from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Paths
    pkg_share_description = FindPackageShare(package='hrobot_description').find('hrobot_description')
    file_urdf = os.path.join(pkg_share_description, 'urdf', 'pepper_robot.urdf.xacro')
    file_rviz_config = os.path.join(pkg_share_description, 'rviz', 'urdf_config.rviz')

    # Generate robot description from xacro
    robot_description = ParameterValue(Command(['xacro ', file_urdf]), value_type=str)

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
        arguments=['-d', file_rviz_config],
        output="screen"
    )

    # Return the full launch description
    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz2_node,
    ])
