#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped


class TwistRelay(Node):
    """
    This class converts the Twist messages published by the robot to TwistStamped messages for
    the differential drive controller.
    """
    def __init__(self):
        super().__init__('twist_relay')
        # Receive the Twist message
        self.controller_sub = self.create_subscription(Twist, '/cmd_vel', self.controller_twist_callback, 10)
        # Send the TwistStamped message
        self.controller_pub = self.create_publisher(TwistStamped, '/diff_drive_controller/cmd_vel', 10)

    def controller_twist_callback(self, msg: Twist):
        # Conversion process
        stamped_msg = TwistStamped()
        stamped_msg.header.stamp = self.get_clock().now().to_msg()
        stamped_msg.twist = msg
        self.controller_pub.publish(stamped_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TwistRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
