# RCv1

![thumbnail](https://raw.githubusercontent.com/odbee/RCv1/main/thumb.png)


RCV1 is a plugin to directly control the UR10e robot and the robotiq gripper through a json file.

the new version **rc_master_UI2.py** now includes a graphical user interface to run, stop and clear the tasks


needed input data:

(JSON_FILE_LOC) saves the location of the json file that is filled with commands.

(ROBOT_HOST_IP) The Robot IP is necessary for communcation . It should be retreivable from the Commandboard.
(RTDE_PORT) Port 30004 streams the state of the robot with RTDE.
(SECONDARY_PORT) Port 30002 sends direct commands to the robot to execute.
Both standards are set by the UR.

the Port 127.0.0.1 is used to locally stream data. Port 5005 is used with the grasshopper script to share the current state of the robot. Currently it is sharing the queue.

secondary_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
