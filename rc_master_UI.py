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
from rc_commands import *

import tkinter as tk
#setup out communcation

############################ GLOBALS

ROBOT_HOST_IP = '192.168.1.112'
RTDE_PORT = 30004

SECONDARY_PORT=30002
secondary_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sampling_frequency =125
config_file='record_configuration.xml'
save_in_binary=False
conf = rtde_config.ConfigFile(config_file)
output_names, output_types = conf.get_recipe('out')

# other global vars
currentcommand=""
gripperdone=0


UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


keep_running=True
isfree=True #this may cause problems
dumbbitch=True
starttime=time.time()
endtime=time.time()

rtde_connection = rtde.RTDE(ROBOT_HOST_IP, RTDE_PORT)
gripper = robotiq_gripper.RobotiqGripper()


isfree=True #this may cause problems

def setup():
    global keep_running
    # setup rtde
    rtde_connection.connect()
        # setup recipes
    if not rtde_connection.send_output_setup(output_names, output_types, frequency = sampling_frequency):
        logging.error('Unable to configure output')
        sys.exit()
        
    #start data synchronization
    if not rtde_connection.send_start():
        logging.error('Unable to start synchronization')
        sys.exit()
    #setup gripper
    gripper.connect(ROBOT_HOST_IP,63352)
    gripper.activate()
    keep_running=True

def run():
    global isfree
    if keep_running:
    # try sending 
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
                    try:
                        gripperdone, lefttasks = send_this_command(read_and_append_list_return_command('coords.json'),ROBOT_HOST_IP,SECONDARY_PORT,gripper)
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

        except rtde.RTDEException:
            rtde_connection.disconnect()
            sys.exit()




def disconn():
    sys.stdout.write("\rComplete!            \n")
    rtde_connection.send_pause()
    rtde_connection.disconnect()
    gripper.disconnect()




def main():    
    setup()

def exit():
    keep_running=False

root= tk.Tk()

canvas1 = tk.Canvas(root, width = 300, height = 300)
canvas1.pack()

button1 = tk.Button(text='Run script',command=main, bg='brown',fg='white')
button2 =tk.Button(text='Exit Me',command=exit, bg='brown',fg='white')


canvas1.create_window(150, 100, window=button1)
canvas1.create_window(150, 150, window=button2)
root.after(run())
root.mainloop()




