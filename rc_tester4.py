import socket
import json


json_file=open('coords.json')
data = json.load(json_file)

command=data["commands"].pop(0)
print(command["command"])

print(data)