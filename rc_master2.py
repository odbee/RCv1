import argparse
import logging
from rtde import serialize
import sys
sys.path.append('..')
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import rtde.csv_writer as csv_writer
import rtde.csv_binary_writer as csv_binary_writer
import time
import socket
import json
import robotiq_gripper
import math
#setup out communcation



# def update_list(ourlist,host,port):
#     if len(ourlist) !=0:
currentcommand=""
gripperdone=0

def send_command_from_list(ourlist,host,port):
    if len(ourlist) != 0:
        commandtosend= ourlist.pop(0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(commandtosend)
        s.close()
    return

def send_this_command(comm):
    gripperdone=0
    if comm[1]=="urscript":
        host=ROBOT_HOST_IP
        port=SECONDARY_PORT
        # print(comm[0].encode())
        send_this_command_urscript(comm[0],host,port)


    if comm[1]=="gripper":
        value=((math.floor(float(comm[0]))))

        word = gripper.move_and_wait_for_pos(value,255,255)
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


UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP




ROBOT_HOST_IP = '192.168.1.112'
RTDE_PORT = 30004

SECONDARY_PORT=30002
secondary_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)


sampling_frequency =125
config_file='record_configuration.xml'
save_in_binary=False
conf = rtde_config.ConfigFile(config_file)
output_names, output_types = conf.get_recipe('out')

rtde_connection = rtde.RTDE(ROBOT_HOST_IP, RTDE_PORT)
rtde_connection.connect()


# setup recipes
if not rtde_connection.send_output_setup(output_names, output_types, frequency = sampling_frequency):
    logging.error('Unable to configure output')
    sys.exit()
    
#start data synchronization
if not rtde_connection.send_start():
    logging.error('Unable to start synchronization')
    sys.exit()

int = 1
isfree=True


keep_running=True
starttime=time.time()
endtime=time.time()


gripper = robotiq_gripper.RobotiqGripper()
gripper.connect(ROBOT_HOST_IP,63352)
gripper.activate()

while keep_running:
    # if int%10000000==0:
        try:
            state = rtde_connection.receive(save_in_binary)
            if state is not None:
                val=''
                for i in range(len(output_names)):
                    size=serialize.get_item_size(output_types[i])
                    val=val+str(state.__dict__[output_names[i]])
                if((val)!='0'):
                    isfree=True
                

                botheval=((val)=='0') and (isfree==True)
                if ((botheval) or (gripperdone)):
                    #send first command to robot and remove frst
                    # send_command_from_list(dummylist,ROBOT_HOST_IP,SECONDARY_PORT)
                    try:
                        gripperdone, lefttasks = send_this_command(read_and_append_list_return_command('coords.json'))
                    except:
                        print("skipped")
                    print(str(lefttasks))
                    sock.sendto(str(lefttasks).encode(), (UDP_IP,UDP_PORT))
                    # if (gripperdone):
                    #     print("gripperdone")
                    isfree=False
                    starttime=time.time()

                endtime=time.time()
                if abs(endtime-starttime)>1:
                    isfree=True
                    
                # sock.sendto(val.encode("ascii"), (UDP_IP,UDP_PORT))
                # sys.stdout.write("\r")
                # sys.stdout.write(isfree)
                # sys.stdout.flush()


        except rtde.RTDEException:
            rtde_connection.disconnect()
            sys.exit()
        int=1
    # int+=1
    # print(int)
sys.stdout.write("\rComplete!            \n")

rtde_connection.send_pause()
rtde_connection.disconnect()