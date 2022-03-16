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
JSON_FILE_LOC= 'coords.json' # looks for the json file to read from

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

############# SETTING VARIABLES
keep_running=False
isfree=True #this may cause problems
buttonpressed=False
starttime=time.time()
endtime=time.time()

############ SETUP RTDE CONNECTION. 
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
    global gripperdone
    global starttime
    global runtext

    is_running.config(text=str(keep_running))
    if keep_running:
    # try sending command
        try:
            state = rtde_connection.receive(save_in_binary)
            
            if state is not None: #check the state from RTDE to check if the robot is busy
                val=''
                for i in range(len(output_names)):
                    size=serialize.get_item_size(output_types[i])
                    val=val+str(state.__dict__[output_names[i]])
                if((val)!='0'): # if the robot isnt busy set it free and open for sending commands
                    isfree=True
                machine_status.config(text=val) #update the status in the ui

                botheval=((val)=='0') and (isfree==True) # double lock to avoid sending multiple commands because of asynchrononous update (RTDE has higher refresh rate than execution speed)
                if ((botheval) or (gripperdone)):
                    try: # if possible run the command, catch if it failed
                        gripperdone, lefttasks = send_this_command(read_and_append_list_return_command(JSON_FILE_LOC),ROBOT_HOST_IP,SECONDARY_PORT,gripper)
                    except: # if failed print in command line
                        print("skipped")
                    print(str(lefttasks))
                    tasks_left.config(text=str(lefttasks)) # show how many tasks are left
                    sock.sendto(str(lefttasks).encode(), (UDP_IP,UDP_PORT))# send how many tasks are left through UDP to grasshopper to make a loop possible
                    # if (gripperdone):
                    #     print("gripperdone")
                    isfree=False
                    starttime=time.time()

                endtime=time.time()
                if abs(endtime-starttime)>1: # check every second, not sure why
                    isfree=True

        except rtde.RTDEException: # catch error
            rtde_connection.disconnect()
            print("ERRO")

            # sys.exit()
    else:
        machine_status.config(text="#")
        tasks_left.config(text="#")
    root.update()
    root.after(10,run)


def disconn():
    sys.stdout.write("\rComplete!            \n")
    rtde_connection.send_pause()
    rtde_connection.disconnect()
    gripper.disconnect()


def donothing():
    if not keep_running:
        root.after(10,donothing)

def main():
    global buttonpressed
    if not buttonpressed:    
        buttonpressed=True
        setup()
        root.after(10,run)



def exit():
    global buttonpressed
    global keep_running
    keep_running=False
    disconn()
    root.update()
    buttonpressed=False


def clearjson():
    filename=JSON_FILE_LOC
    data={}
    data["commands"]= []
    
    with open(filename,"w") as write_file:
        json.dump(data,write_file)
    print("successfully cleared json file!")

root= tk.Tk()

canvas1 = tk.Canvas(root, width = 300, height = 300)
canvas1.pack()

button1 = tk.Button(text='run script',command=main, bg='brown',fg='white')
button2 =tk.Button(text='stop script',command=exit, bg='brown',fg='white')
button3 =tk.Button(text='clear json file',command=clearjson, bg='brown',fg='white')

machine_status_text = tk.Label(text = "Machine Status Code")
machine_status = tk.Label(text = "#")

is_running_text = tk.Label(text = "Is Running?")
is_running = tk.Label(text = "False")

tasks_left_text = tk.Label(text = "Number of tasks left")
tasks_left = tk.Label(text = "#")

runtext="process loading"

textstuff=tk.Text()
textstuff.insert(tk.END, runtext)

textrunning=tk.Label(text=runtext)
# canvas1.create_window(50, 100, window=textstuff)
canvas1.create_window(50, 50, window=button1)
canvas1.create_window(150, 50, window=button2)
canvas1.create_window(250, 50, window=button3)
# canvas1.create_window(200,200, window=textrunning)
canvas1.create_window(80,100, window=machine_status_text)
canvas1.create_window(80,120, window=machine_status)

canvas1.create_window(80,200, window=is_running_text)
canvas1.create_window(80,220, window=is_running)


canvas1.create_window(220,100, window=tasks_left_text)
canvas1.create_window(220,120, window=tasks_left)


textstuff.insert(tk.END, runtext)


root.mainloop()




