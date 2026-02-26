import socket

FGADDR = "127.0.0.1"
FGPORT = 5600

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((FGADDR, FGPORT))

battery = 1
throttle = 0.8

datastr = f"{battery}:{throttle}\n"

sock.sendall(datastr.encode("utf-8"))

print("Sent:", datastr)