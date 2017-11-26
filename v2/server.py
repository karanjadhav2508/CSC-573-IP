import socket
import thread
import time
import random

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
clients = {}

SOCK_TIMEOUT = 2
CONN_REQ = "conn_req"
DROP_PROB = 0.33

sock = 0

class UserStore:
	username = ""
	password = ""
	ip = ""
	port = ""
	message_queue = []

	def __init__(self, username, password, ip, port):
		self.username = username
		self.password = password
		self.ip = ip
		self.port = port

	def add_message(self, sender, msg):
		self.message_queue.append([sender, msg])

	def remove_message(self, sender, msg):
		self.message_queue.remove([sender, msg])

def setup():
	global sock
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	print "Server online on UDP port " + str(UDP_PORT)

def deliver_message(sender, receiver, msg):
	global sock
	cl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	cl_sock.settimeout(SOCK_TIMEOUT)

	for i in range(3):
		cl_sock.sendto("Message from "+sender+": "+msg, (clients[receiver].ip, int(clients[receiver].port)))
		try:
			ack, addr = cl_sock.recvfrom(1024)
			if ack == "ack:Message Received":
				sock.sendto("Message Received by Client: ("+receiver+":"+msg+")", (clients[sender].ip, int(clients[sender].port)))
				clients[receiver].remove_message(sender, msg)
				break
		except socket.timeout:
			continue

	cl_sock.close()

def deliver_pending_messages(receiver):
	for msg in clients[receiver].message_queue:
		thread.start_new_thread(deliver_message,(msg[0],receiver,msg[1],))

def add_client(info):
	username = info[1]
	password = info[2]
	ip = info[3]
	port = info[4]

	if username in clients:
		if clients[username].password == password:
			clients[username].ip = ip
			clients[username].port = port
			print username + " ip, port updated and connected"
			print "Sending any pending messages"
			deliver_pending_messages(username)
		else:
			print "User exists, wrong password used"
			return False
	else:
		clients[username] = UserStore(username, password, ip, port)
		print username + " added and connected"

	return True

def send_conn_ack(status, addr):
	global sock
	if status:
		sock.sendto("Connection Successful", addr)
	else:
		sock.sendto("Connection Failed: User exists, wrong password used. Please reconnect", addr)

def send_list(info, addr):
	global sock
	sender = info[0]
	client_list = []
	for receiver in clients:
		if receiver != sender:
			client_list.append(receiver)
	sock.sendto(str(client_list), addr)

def send(info, addr):
	global sock
	sender = info[0]
	receiver = info[1]
	msg = info[2]
	if receiver in clients:
		ip = clients[receiver].ip
		port = clients[receiver].port
		clients[receiver].add_message(sender, msg)
		sock.sendto("Message Received by Server: ("+receiver+":"+msg+")", addr)
		thread.start_new_thread(deliver_message,(sender, receiver, msg,))
	else:
		sock.sendto("User "+receiver+" not present", addr)

def start():
	global sock
	while True:
		data, addr = sock.recvfrom(1024)
		info = data.split(":")
		if info[0] == CONN_REQ:
			status = add_client(info)
			send_conn_ack(status, (info[3], int(info[4])))
		elif info[1] == "list":
			send_list(info, addr)
		else:
			drop = random.uniform(0, 1)
			if(drop < DROP_PROB):
				print "server dropped ", info
			else:
				send(info, addr)

if __name__=="__main__":
	setup()
	start()
