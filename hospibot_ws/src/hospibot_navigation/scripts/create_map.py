#!/usr/bin/env python3
import rclpy 
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, MapMetaData
import rclpy.time
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformListener, LookupException


class Pose:
    def __init__(self, px=0, py=0):
        self.x = px
        self.y = py

def coordinatesToPose(px, py, map_info: MapMetaData):
    pose = Pose()
    pose.x = round((px - map_info.origin.position.x) / map_info.resolution)
    pose.y = round((py - map_info.origin.position.y) / map_info.resolution)
    return pose

def poseOnMap(pose: Pose, map_info: MapMetaData):
    return pose.x < map_info.width and pose.x >= 0 and pose.y < map_info.height and pose.y >= 0

def poseToCell(pose: Pose, map_info: MapMetaData):
    return map_info.width * pose.y + pose.x


class Mapping(Node):

    def __init__(self):
        super().__init__("mapping_node")

        # Define map dimensions
        self.declare_parameter("width", 100.0) # 100m width
        self.declare_parameter("height", 100.0) # 100 height
        self.declare_parameter("resolution", 0.1) # 10 cm

        width = self.get_parameter("width").value
        height = self.get_parameter("height").value
        resolution = self.get_parameter("resolution").value

        self.map_ = OccupancyGrid()
        self.map_.info.width = round(width / resolution)    # Number of rows
        self.map_.info.height = round(height / resolution)  # Number of columns
        self.map_.info.resolution = resolution
        # Set the origin in the middle of the map
        self.map_.info.origin.position.x = float(-round(width / 2.0))
        self.map_.info.origin.position.y = float(-round(height / 2.0))
        self.map_.header.frame_id = "odom"
        self.map_.data = [-1] * (self.map_.info.width * self.map_.info.height) # Initialize all cells to unknown

        self.map_publisher = self.create_publisher(OccupancyGrid, "map", 1)
        self.scan_subscriber = self.create_subscription(LaserScan, "scan", self.scan_callback, 10)
        self.timer = self.create_timer(1.0, self.timer_callback)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def scan_callback(self, scan: LaserScan):
        # Read the current position of the robot and mark it on the map
        try:
            t = self.tf_buffer.lookup_transform(self.map_.header.frame_id, scan.header.frame_id, rclpy.time.Time())
        except LookupException:
            self.get_logger().info("Unable to transform between the frames /odom and /base_footprint")
            return
        
        robot_pos = coordinatesToPose(t.transform.translation.x, t.transform.translation.y, self.map_.info)
        if not poseOnMap(robot_pos, self.map_.info):
            self.get_logger().info("The robot is out of the map!")
            return
        
        robot_cell = poseToCell(robot_pos, self.map_.info)
        self.map_.data[robot_cell] = 100

    def timer_callback(self):
        self.map_.header.stamp = self.get_clock().now().to_msg()
        self.map_publisher.publish(self.map_)


def main():
    rclpy.init()
    node = Mapping()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()


