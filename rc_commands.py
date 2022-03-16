import socket
import math
import json
import time

#####            OUTDATED
def send_command_from_list(ourlist,host,port):
    if len(ourlist) != 0:
        commandtosend= ourlist.pop(0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(commandtosend)
        s.close()
    return
#### ---------END OUTDATE

def send_this_command(comm,robohost,roboport,grippa):
    """sends command to robot/gripper
    Args:
        comm: command
        robohost: IP of robot
        roboport: Port of robot
        grippa: gripper class.

    Returns:
        Returns if gripper is done and how many tasks are left.
    """
    gripperdone=0
    if comm[1]=="urscript":
        host=robohost
        port=roboport
        # print(comm[0].encode())
        send_this_command_urscript(comm[0],host,port)


    if comm[1]=="gripper":
        value=((math.floor(float(comm[0]))))

        word = grippa.move_and_wait_for_pos(value,255,255)
        # print(word)
        gripperdone=1
        # print(gripperdone)
        # host=ROBOT_HOST_IP
        # port=SECONDARY_PORT
        # send_this_command_urscript("sleep(1)"+"\n",host,port)

    print("finished sending command")
    return gripperdone,comm[2]

def send_this_command_urscript(comm,host,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(comm.encode())
    s.close()
    return


def read_and_append_list_return_command(filename):
    """sends command to robot/gripper
    Args:
        filename: the filename of the json file

    Returns:
        Returns output needed to be read by send_this_command.
    """
    data=dict
    try:
        with open(filename,"r") as json_file:
            json_file=open(filename)
            data = json.load(json_file)
            
            try:
                command=(data["commands"].pop(0))

            except:
                command={"command":"sleep(1)"+"\n","commandtype":"urscript"}
            commandrecipe=command["command"]
            commandtype=command["commandtype"]
        try:
            with open(filename,"w") as json_file:
                json.dump(data,json_file)
        except:
            time.sleep(0.1)        
            with open(filename,"w") as json_file:
                json.dump(data,json_file)
        tasksleft=len(data["commands"])
        
        return commandrecipe,commandtype,tasksleft
    except:
        commandrecipe="sleep(1)"
        commandtype="urscript"
        tasksleft=1000
        return commandrecipe,commandtype,tasksleft
