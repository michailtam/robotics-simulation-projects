import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    hospibot_navigation_pkg = get_package_share_directory("hospibot_navigation")

    lifecycle_nodes = ["map_saver_server", "slam_toolbox"]

    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description=""
    )

    slam_config_arg = DeclareLaunchArgument(
        "slam_config",
        default_value=os.path.join(hospibot_navigation_pkg, "config", "slam_toolbox.yaml")
    )

    slam_config = LaunchConfiguration("slam_config")
    use_sim_time = LaunchConfiguration("use_sim_time")

    # Execute SLAM using the slam toolbox
    slam_toolbox = Node(
        package="slam_toolbox",
        executable="sync_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[
            slam_config, 
            {"use_sim_time": use_sim_time}
        ]
    )

    # Load the created map i.e. occupancy grid
    nav2_map_saver = Node(
        package="nav2_map_server",
        executable="map_saver_server",
        name="map_saver_server",
        output="screen",
        parameters=[
            {"save_map_timeout": 5.0},
            {"use_sim_time": use_sim_time},
            {"free_thresh_default": 0.196},
            {"occupied_thresh_default": 0.65}
        ]
    )

    # To avoid manually start the nav2_map_saver there is the LifeCycleManager
    nav2_lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager",
        output="screen",
        parameters=[
            {"node_names": lifecycle_nodes},
            {"use_sim_time": use_sim_time}
        ]
    )

    return LaunchDescription([
        use_sim_time_arg,
        slam_config_arg,
        slam_toolbox,
        nav2_map_saver,
        nav2_lifecycle_manager
    ])