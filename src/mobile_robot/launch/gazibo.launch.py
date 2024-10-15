import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # this name has to match the robot name in the Xacro file
    robotXacroName = 'differential_drive_robot'

    # this is the name of our package, and the folder for defining paths
    namePackage = 'mobile_robot'

    # Relative paths to the Xacro and Gazebo world files
    modelFileRelativePath = 'model/robot.urdf.xacro'
    worldFileRelativePath = 'model/empty_world.world'

    # Absolute paths to the model and world files
    pathModelFile = os.path.join(
        get_package_share_directory(namePackage), modelFileRelativePath
    )
    pathWorldFile = os.path.join(
        get_package_share_directory(namePackage), worldFileRelativePath
    )

    # Get the robot description from the Xacro model file
    robotDescription = xacro.process_file(pathModelFile).toxml()

    # This is the launch file from the gazebo_ros package
    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
    )

    # Launch description from Gazebo
    gazeboLaunch = IncludeLaunchDescription(
        gazebo_rosPackageLaunch,
        launch_arguments={'world': pathWorldFile}.items()
    )

    # Create a gazebo_ros Node
    spawnModelNode = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', robotXacroName],
        output='screen'
    )

    # Robot State Publisher Node
    nodeRobotStatePublisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robotDescription,
            'use_sim_time': True
        }]
    )

    # Create an empty LaunchDescription object
    launchDescriptionObject = LaunchDescription()

    # Add Gazebo launch action
    launchDescriptionObject.add_action(gazeboLaunch)

    # Add the two nodes (Spawn Model and Robot State Publisher)
    launchDescriptionObject.add_action(spawnModelNode)
    launchDescriptionObject.add_action(nodeRobotStatePublisher)

    return launchDescriptionObject
