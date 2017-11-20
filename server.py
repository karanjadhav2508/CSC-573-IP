import socket
import thread
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

clients = {}

sock = 0

def setup():
	global sock
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))

def add_client(info):
	user_details = info[1].split("-")
	clients[user_details[0]] = user_details[1].split(",")

def send(info, addr):
	global sock
	sender = info[0]
	receiver = info[1]
	msg = info[2]
	if receiver in clients:
		ip, port = clients[receiver]
		cl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		cl_sock.sendto(sender+":"+msg, (ip, int(port)))
		sock.sendto(receiver+":"+msg+":ACK", addr)
		cl_sock.close()
	else:
		sock.sendto("User "+receiver+" not present", addr)

def start():
	global sock
	#for x in xrange(6):
	while True:
		data, addr = sock.recvfrom(1024)
		print data
		info = data.split(":")
		if info[0] == "0":
			add_client(info)
		else:
			send(info, addr)

if __name__=="__main__":
	setup()
	start()