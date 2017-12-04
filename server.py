import socket
import thread
import time
import threading

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

clients = {}

sock = 0

gbn_window = 4
next_seq = 0
expected_ack_seq = 0

all_messages = []
# gbn queue: each element tuple contianing gbn sequence number, message and retry attempts count
gbn_queue = []

lock = 0

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
		self.message_queue.append([sender, self.username, msg])

	def remove_message(self, sender, msg):
		if [sender, self.username, msg] in self.message_queue:
			self.message_queue.remove([sender, self.username, msg])

def setup():
	global sock
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	print "Server online on UDP port " + str(UDP_PORT)
	thread.start_new_thread(deliver_messages,())

def timeout_check(gbn_seq):
	global next_seq, expected_ack_seq, all_messages
	time.sleep(2)
	if expected_ack_seq == gbn_seq:
		if len(gbn_queue) > 0:
			if gbn_queue[0][2] >= 3:
				print "Max Retries completed. Unable to send messages. Client could be down. Messages saved, will be sent later"
				for val in gbn_queue:
					msg = val[1]
					sender = val[3]
					receiver = val[4]
					all_messages.append([sender, receiver, msg])
				del gbn_queue[:]
				next_seq = 0
				expected_ack_seq = 0
			else:
				print "Timeout waiting for ack. Resending all messages in gbn_queue (retry number " + str(gbn_queue[0][2])  + ")"
				gbn_queue[0][2] = gbn_queue[0][2] + 1

def deliver_messages():
	global sock, gbn_queue, clients
	cl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	while True:
		time.sleep(1)

		size = len(gbn_queue)
		for i in range(size):
			if len(gbn_queue) > 0:
				i = i - (size - len(gbn_queue))
				msg = gbn_queue[i][1]
				sender = gbn_queue[i][3]
				receiver = gbn_queue[i][4]
				gbn_seq = "gbn:" + str(gbn_queue[i][0])
	
			cl_sock.sendto("Message from "+sender+": "+msg+":"+gbn_seq, (clients[receiver].ip, int(clients[receiver].port)))
			if len(gbn_queue) > 0:
				i = i - (size - len(gbn_queue))
				thread.start_new_thread(timeout_check,(gbn_queue[i][0],))

	cl_sock.close()

def send_ack(gbn_seq, sender, receiver, msg):
	global sock, clients
	cl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	print "RECEIVED FROM " + sender + " (gbn:"+gbn_seq+":"+receiver+":"+msg+")"
	print "Sending ack"

	cl_sock.sendto("gbn:"+gbn_seq+":Message Received by Server: ("+receiver+":"+msg+")", (clients[sender].ip, int(clients[sender].port)))

	cl_sock.close()


def deliver_pending_messages(receiver):
	global gbn_queue, gbn_window, next_seq, clients, all_messages
	for msg in clients[receiver].message_queue:
		sender = msg[0]
		recv = msg[1]
		message = msg[2]
		if len(gbn_queue) < gbn_window:
			all_messages.remove([sender, recv, message])
			gbn_queue.append([next_seq, message, 0, sender, recv])
			next_seq = (next_seq + 1) % gbn_window

def add_client(info):
	global clients
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
	global sock, clients
	sender = info[0]
	client_list = []
	for receiver in clients:
		if receiver != sender:
			client_list.append(receiver)
	sock.sendto(str(client_list), addr)

def send(info, addr):
	global sock, all_messages, gbn_queue, gbn_window, next_seq, clients
	gbn_seq = info[1]
	sender = info[2]
	receiver = info[3]
	msg = info[4]
	if receiver in clients:
		ip = clients[receiver].ip
		port = clients[receiver].port
		clients[receiver].add_message(sender, msg)
		
		if len(gbn_queue) < gbn_window:		
			gbn_queue.append([next_seq, msg, 0, sender, receiver])
			next_seq = (next_seq + 1) % gbn_window
		else:
			all_messages.append([sender, receiver, msg])

		send_ack(gbn_seq, sender, receiver, msg)
	else:
		sock.sendto("User "+receiver+" not present", addr)

def check_ack(gbn_ack_no):
	global sock, all_messages, gbn_queue, expected_ack_seq, clients, next_seq
	if int(gbn_ack_no) == expected_ack_seq:
		expected_ack_seq = (expected_ack_seq + 1) % gbn_window
		msg = gbn_queue[0][1]
		sender = gbn_queue[0][3]
		receiver = gbn_queue[0][4]
		sock.sendto("Message Received by Client: ("+receiver+":"+msg+")", (clients[sender].ip, int(clients[sender].port)))
		del gbn_queue[0]
		clients[receiver].remove_message(sender, msg)

		if len(all_messages) > 0:
			next_sender = all_messages[0][0]
			next_receiver = all_messages[0][1]
			next_msg = all_messages[0][2]
			del all_messages[0]
			gbn_queue.append([next_seq, next_msg, 0, next_sender, next_receiver])
			next_seq = (next_seq + 1) % gbn_window

	else:
		#ignore dup/unexpected ack
		return

def start():
	global sock
	while True:
		data, addr = sock.recvfrom(4096)
		info = data.split(":")
		if info[0] == "connection_request":
			status = add_client(info)
			send_conn_ack(status, (info[3], int(info[4])))
		elif info[1] == "list":
			send_list(info, addr)
		elif info[0] == "ack":
			check_ack(info[3])
		else:
			send(info, addr)

if __name__=="__main__":
	setup()
	start()
