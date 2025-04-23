#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
 
 
def generate_launch_description():

    # Launch the joint-state-broadcaster first
    start_joint_state_broadcaster_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_broadcaster'],
        output='screen')
    
    # Launch the body-part-controller
    start_body_part_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'body_part_controller'],
        output='screen')

    # Launch the diff-drive-controller
    start_diff_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'diff_controller'],
        output='screen')

    # Register event handlers for sequencing
    # Launch the joint state broadcaster after spawning the robot
    start_first_controllers_cmd = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=start_joint_state_broadcaster_controller,
            on_exit=[start_body_part_controller]))
    
    start_second_controllers_cmd = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=start_body_part_controller,
            on_exit=[start_diff_controller]))
 
    # Create the launch description and populate
    ld = LaunchDescription()
 
    # Add the actions to the launch description in sequence
    ld.add_action(start_first_controllers_cmd)
    ld.add_action(start_second_controllers_cmd)
    
    return ld
