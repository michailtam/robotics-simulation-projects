import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def get_gazebo_model_path():
    ''' Return the package model path (not the shared one, because this does not work) '''
    return os.path.join(os.getcwd(), "src", "hrobot_gazebo", "models")

def generate_launch_description():
    # Files
    pkg_share_gazebo = FindPackageShare(package='hrobot_gazebo').find('hrobot_gazebo')
    pkg_ros_gz_sim = FindPackageShare('ros_gz_sim').find('ros_gz_sim')
    world_path = os.path.join(pkg_share_gazebo, 'worlds', 'hospital.world')
    gazebo_models_path = get_gazebo_model_path()
    
    # Set the Gazebo model path
    set_env_vars_resources = AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gazebo_models_path)

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
        default_value='3.0',
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
        default_value='-1.57',
        description='yaw angle of initial orientation in radians')

    gazebo_config_file = PathJoinSubstitution([
        FindPackageShare('hrobot_gazebo'), 
        'config',
        'ros_gz_bridge.yaml'])
    
    # Gazebo (Ignition/GZ) simulator launch
    # Note: If the used world file does not contain a physics engine, add after the world_path the following plugin in code
    # --physics-engine gz-physics-bullet-featherstone-plugin
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments=[('gz_args', [f' -r -v 4 ', world_path])])
        
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
                    '-Y', yaw,
                    '-allow_renaming', 'true'
                ],
                parameters=[{'use_sim_time': True}],
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

    # # Includes optimizations to minimize latency and bandwidth when streaming image data
    start_gazebo_ros_image_bridge_cmd = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=[
            '/cam_1/image'
        ],
        remappings=[
            ('/cam_1/image', '/cam_1/color/image_raw')
        ])

    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(declare_x_pos_cmd)
    ld.add_action(declare_y_pos_cmd)
    ld.add_action(declare_z_pos_cmd)
    ld.add_action(declare_roll_cmd)
    ld.add_action(declare_pitch_cmd)
    ld.add_action(declare_yaw_cmd)
    ld.add_action(set_env_vars_resources)
    ld.add_action(gazebo_launch)
    ld.add_action(spawn_entity)
    ld.add_action(ros_gazebo_bridge)
    ld.add_action(start_gazebo_ros_image_bridge_cmd)

    return ld
