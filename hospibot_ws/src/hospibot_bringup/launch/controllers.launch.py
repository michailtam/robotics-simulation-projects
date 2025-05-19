#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


class Controllers:
    """
    A class for loading and activating the ros2 controllers for the robot
    """
    def __init__(self):
        
        self._body_controllers = [
            'joint_state_broadcaster',
            'lower_body_controller', 
            'upper_body_controller', 
            'head_controller',
            'diff_drive_controller'
        ]
        
    def create_controllers(self):
        """ Create all the controllers for the robot. """
        previous_spawner = None
        spawners = []
        for controller in self._body_controllers:
            current_spawner = Node(
                package='controller_manager',
                executable='spawner',
                arguments=[controller, '--controller-manager', '/controller_manager'])
            
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


def generate_launch_description():
    
    # Create the Controller class for the ros2 controller management
    ctrls = Controllers()
    controllers = ctrls.create_controllers()

    # Create the launch description and populate
    ld = LaunchDescription()
    
    # Add the actions to the launch description in sequence
    for controller in controllers:
        ld.add_action(controller)

    # Transforms the Twist message to TwistStamped message
    twist_to_stamped_node = Node(
        package='hospibot_bringup',
        executable='twist_relay.py',
        name='twist_relay',
        output='screen'
    )

    ld.add_action(twist_to_stamped_node)

    return ld
