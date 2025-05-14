#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped
from builtin_interfaces.msg import Time


class TwistToStamped(Node):
    def __init__(self):
        super().__init__('twist_to_stamped')
        self.subscription = self.create_subscription(Twist, '/cmd_vel', self.twist_callback, 10)
        self.publisher = self.create_publisher(TwistStamped, '/diff_drive_controller/cmd_vel', 10)

    def twist_callback(self, msg: Twist):
        stamped_msg = TwistStamped()
        stamped_msg.header.stamp = self.get_clock().now().to_msg()
        stamped_msg.twist = msg
        self.publisher.publish(stamped_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TwistToStamped()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
