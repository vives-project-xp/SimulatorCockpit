import socket
import time

UDP_INPUT_PORT = 5600

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# batterij AAN
sock.sendto(b"BATTERY=1\n", ("127.0.0.1", UDP_INPUT_PORT))
print("Battery ON")
time.sleep(3)

# batterij UIT
sock.sendto(b"BATTERY=0\n", ("127.0.0.1", UDP_INPUT_PORT))
print("Battery OFF")
