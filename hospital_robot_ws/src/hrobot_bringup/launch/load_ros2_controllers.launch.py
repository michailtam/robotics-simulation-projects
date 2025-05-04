#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.substitutions import PathJoinSubstitution
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import LogInfo


class Controllers:
    """
    A class for loading and activating the ros2 controllers for the robot
    """
    def __init__(self, ros2_control_file: str):
        """
        Args:
            ros2_control_file: Path to ROS 2 controllers config yaml
        """
        self._body_controllers = [
            'joint_state_broadcaster',
            'lower_body_controller', 
            'upper_body_controller', 
            'head_controller']
        self._ros2_control_file = ros2_control_file
        self.js_broadcaster_msg = "Controller successfull loaded."
        
    def create_controllers(self):
        previous_spawner = None
        spawners = []
        for controller in self._body_controllers:
            current_spawner = Node(
                package='controller_manager',
                executable='spawner',
                arguments=[controller, '--param-file', self._ros2_control_file])
            
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

    controller_file = PathJoinSubstitution(
        [FindPackageShare('hrobot_bringup'), 'config', 'ros2_controllers.yaml'])

    # Create the Controller class for the ros2 controller management
    ctrls = Controllers(controller_file)

    controllers = ctrls.create_controllers()

    # diff_drive_controller_cmd = Node(
    #         package='controller_manager',
    #         executable='spawner',
    #         name='controller_manager',
    #         # remappings=[('/diff_drive_controller/cmd_vel', '/cmd_vel')],  # Remap here
    #         arguments=['diff_drive_controller', '--param-file', controller_file]
    #     )
    
    # Create the launch description and populate
    ld = LaunchDescription()
    
    # Add the actions to the launch description in sequence
    for controller in controllers:
        ld.add_action(controller)
    # ld.add_action(diff_drive_controller_cmd)

    return ld
