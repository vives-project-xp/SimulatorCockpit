import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 5500))

print("Wachten op data...")

while True:
    data, _ = sock.recvfrom(1024)
    print(data.decode(errors="ignore"))
