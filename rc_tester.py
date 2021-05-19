import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5430
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


sock.connect((UDP_IP, UDP_PORT))


data,addr=sock.recv(1)
print(data)
    


sock.close()