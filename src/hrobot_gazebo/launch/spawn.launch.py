import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    # Set the pose configuration variables
    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    z = LaunchConfiguration('z')
    roll = LaunchConfiguration('roll')
    pitch = LaunchConfiguration('pitch')
    yaw = LaunchConfiguration('yaw')

    # Set default values
    declare_x_pos_cmd = DeclareLaunchArgument(
        name='x',
        default_value='0.0',
        description='x-position')

    declare_y_pos_cmd = DeclareLaunchArgument(
        name='y',
        default_value='0.0',
        description='y-position')
    
    declare_z_pos_cmd = DeclareLaunchArgument(
        name='z',
        default_value='0.0',
        description='z-position')

    declare_roll_cmd = DeclareLaunchArgument(
        name='roll',
        default_value='0.0',
        description='roll angle of initial orientation in radians')

    declare_pitch_cmd = DeclareLaunchArgument(
        name='pitch',
        default_value='0.0',
        description='pitch angle of initial orientation in radians')

    declare_yaw_cmd = DeclareLaunchArgument(
        name='yaw',
        default_value='0.0',
        description='yaw angle of initial orientation in radians')

    gazebo_config_file = PathJoinSubstitution([
        FindPackageShare('hrobot_gazebo'), 
        'config', 
        'gazebo_bridge.yaml'])

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
                arguments=[
                    '-topic', 'robot_description', 
                    '-entity', 'pepper',
                    '-x', x,
                    '-y', y,
                    '-z', z,
                    '-R', roll,
                    '-P', pitch,
                    '-Y', yaw
                ],
                output='screen'
            )
        ]
    )

    # Brdge ROS2 with Gazebo
    ros_gazebo_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gazebo_bridge',
        parameters=[{
            'config_file': gazebo_config_file
        }],
        output='screen'
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(declare_x_pos_cmd)
    ld.add_action(declare_y_pos_cmd)
    ld.add_action(declare_z_pos_cmd)
    ld.add_action(declare_roll_cmd)
    ld.add_action(declare_pitch_cmd)
    ld.add_action(declare_yaw_cmd)
    ld.add_action(gazebo_launch)
    ld.add_action(spawn_entity)
    ld.add_action(ros_gazebo_bridge)

    return ld
