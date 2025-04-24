#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler
from launch.substitutions import PathJoinSubstitution
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def load_controllers(controllers, ros2_robot_controllers):
    spawners = []
    previous_spawner = None
    for controller in controllers:
        current_spawner = Node(
            package='controller_manager',
            executable='spawner',
            arguments=[controller, '--param-file', ros2_robot_controllers])

        if previous_spawner:
            # Chain spawners sequentially
            spawners.append(
                RegisterEventHandler(
                    event_handler=OnProcessExit(
                        target_action=previous_spawner,
                        on_exit=[current_spawner]
                    )
                )
            )
        else:
            # First spawner
            spawners.append(current_spawner)
            previous_spawner = current_spawner
    return spawners

def activate_controllers(controllers):
    activated = []
    for controller in controllers:
        activated.append(
            ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', controller],
            output='screen')
        )
    return activated
 
def generate_launch_description():

    # Define the controllers to use
    controllers = [
        'joint_state_broadcaster',
        'diff_drive_controller',
        'lower_body_controller',
        'upper_body_controller',
        'head_controller']

    robot_controllers = PathJoinSubstitution(
        [FindPackageShare('hrobot_bringup'), 'config', 'ros2_controllers.yaml'])
    
    loaded_controllers = load_controllers(controllers, robot_controllers)
    
    activated_controllers = activate_controllers(controllers)
 
    # Create the launch description and populate
    ld = LaunchDescription()
 
    # Add the actions to the launch description in sequence
    for controller in loaded_controllers:
        ld.add_action(controller)
    
    # for controller in activated_controllers:
    #     ld.add_action(controller)

    # ld.add_action(activated_controllers)
    # ld.add_action(load_joint_state_broadcaster_controller_cmd)
    # ld.add_action(load_lower_body_controller_cmd)
    # ld.add_action(load_upper_body_controller_cmd)
    # ld.add_action(start_second_controllers_cmd)
    
    return ld
