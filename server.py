import socket
import thread
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

clients = {}

sock = 0

class UserDetails:
	username = ""
	password = ""
	ip = ""
	port = ""

	def __init__(self, username, password, ip, port):
		self.username = username
		self.password = password
		self.ip = ip
		self.port = port

def setup():
	global sock
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	print "Server online on UDP port " + str(UDP_PORT)

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
		else:
			print "User exists, wrong password used"
			return False
	else:
		clients[username] = UserDetails(username, password, ip, port)
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
		info = data.split(":")
		if info[0] == "connection_request":
			status = add_client(info)
			send_conn_ack(status, (info[3], int(info[4])))
		elif info[1] == "list":
			send_list(info, addr)
		else:
			send(info, addr)

if __name__=="__main__":
	setup()
	start()
