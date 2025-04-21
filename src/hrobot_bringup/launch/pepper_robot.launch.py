import os

from launch import LaunchDescription
from launch.substitutions import Command, LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    # Paths
    pkg_share_description = FindPackageShare(package='hrobot_description').find('hrobot_description')
    default_urdf_file = os.path.join(pkg_share_description, 'urdf', 'pepper_robot.urdf.xacro')
    default_rviz_config_file = os.path.join(pkg_share_description, 'rviz', 'urdf_config.rviz')

    # Generate robot description from xacro
    robot_description = ParameterValue(Command(['xacro ', default_urdf_file]), value_type=str)

    # Launch configuration variables
    use_joint_state_pub_gui = LaunchConfiguration('use_joint_state_pub_gui')
    use_joint_state_pub = LaunchConfiguration('use_joint_state_pub')
    rviz_config_file = LaunchConfiguration('rviz_config_file')
    urdf_model = LaunchConfiguration('urdf_model')
    use_rviz = LaunchConfiguration('use_rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Declare the launch arguments
    declare_joint_state_pub_cmd = DeclareLaunchArgument(
        name='use_joint_state_pub',
        default_value='false',
        choices=['true', 'false'],
        description='Flag to enable the joint state publisher (without UI)')
    
    declare_joint_state_pub_gui_cmd = DeclareLaunchArgument(
        name='use_joint_state_pub_gui',
        default_value='true',
        choices=['true', 'false'],
        description='Flag to enable joint_state_publisher_gui')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true')
    
    declare_use_rviz_cmd = DeclareLaunchArgument(
        name='use_rviz',
        default_value='false',
        choices=['true', 'false'],
        description='Enable the joint state publisher')

    declare_rviz_config_file_cmd = DeclareLaunchArgument(
        name='rviz_config_file',
        default_value=default_rviz_config_file,
        description='Full path to the RVIZ config file to use')

    declare_urdf_model_cmd = DeclareLaunchArgument(
        name='urdf_model',
        default_value=default_urdf_file,
        description='Full path to the RVIZ config file to use')

    # Robot state publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name='joint_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
            }])

    # Joint state publisher
    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_joint_state_pub))

    # Joint state publisher GUI
    joint_state_publisher_node_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_joint_state_pub_gui))

    # RViz2 visualization
    rviz2_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_rviz))

    # Return the full launch description
    ld = LaunchDescription()
    
    ld.add_action(declare_joint_state_pub_cmd)
    ld.add_action(declare_joint_state_pub_gui_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_rviz_config_file_cmd)
    ld.add_action(declare_urdf_model_cmd)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_node)
    ld.add_action(joint_state_publisher_node_gui)
    ld.add_action(rviz2_node)

    return ld