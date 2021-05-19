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
import os
#setup out communcation


dummylist=["movel(p[0.6, -.13, 0.4,0.0,0.0,0], a=0.6, v=0.1, t=0, r=0)" + "\n",
"movel(p[0.6, -.13, 0.8,0.0,0.0,0], a=0.6, v=0.1, t=0, r=0)" + "\n",
"movel(p[0.6, -.13, 0.4,0.0,0.0,0], a=0.6, v=0.1, t=0, r=0)" + "\n",
"movel(p[0.6, -.13, 0.8,0.0,0.0,0], a=0.6, v=0.1, t=0, r=0)" + "\n"]

newlist=[]


# def update_list(ourlist,host,port):
#     if len(ourlist) !=0:
currentcommand=""

def send_command_from_list(ourlist,host,port):
    if len(ourlist) != 0:
        commandtosend= ourlist.pop(0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(commandtosend)
        s.close()
    return

def send_this_command(comm):
    print(comm[1]=="urscript")
    print(comm)
    if comm[1]=="urscript":
        host=ROBOT_HOST_IP
        port=SECONDARY_PORT
        send_this_command_urscript(comm[0],host,port)


def send_this_command_urscript(comm,host,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(comm)
    s.close()
    return



def read_and_append_list_return_command(filename):
    data=dict
    with open(filename,"r") as json_file:
        json_file=open(filename)
        data = json.load(json_file)
        command=(data["commands"].pop(0))
        commandrecipe=command["command"]
        commandtype=command["commandtype"]
        print(commandrecipe)
        
    with open(filename,"w") as json_file:
        json.dump(data,json_file)
    
    
    return commandrecipe,commandtype

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
isidle=True


keep_running=True

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
                    isidle=True
                if (((val)=='0') and (isidle==True)):
                    #send first command to robot and remove frst
                    # send_command_from_list(dummylist,ROBOT_HOST_IP,SECONDARY_PORT)
                    send_this_command(read_and_append_list_return_command('coords.json'))
                    isidle=False

                sock.sendto(val.encode("ascii"), (UDP_IP,UDP_PORT))
                # sys.stdout.write("\r")
                # sys.stdout.write(isidle)
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