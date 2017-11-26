import socket

SERVER = ("127.0.0.1", 5005)
TIMEOUT = 3

def create_sock():
	return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def setup(ip_port):
	sock = create_sock()
	sock.bind(ip_port)
	return sock