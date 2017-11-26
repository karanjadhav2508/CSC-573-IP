import socket
import thread
import time
import sys

SERV_IP = "127.0.0.1"
SERV_PORT = 5005
SELF_IP = "127.0.0.1"
SELF_PORT = 0
RAND_PORT = 0

SOCK_TIMEOUT = 2
CONN_REQ = "conn_req"
DROP_PROB = 0.33

done = False
user_id = ""
password = ""

message_queue = []

def valid_usage():
	print "Invalid input. Available commands:"
	print "- list"
	print "- username: message"

def create_sock():
	return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#all good
def start_server(recv_sock):
	global done
	while True:
		msg, addr = recv_sock.recvfrom(1024)
		print msg
		if msg.startswith("Message from"):
			recv_sock.sendto("ack:Message Received", addr)
	recv_sock.close()
	done = True

#all good
def setup_server():
	global SELF_PORT
	recv_sock = create_sock()
	recv_sock.bind((SELF_IP, RAND_PORT))
	SELF_PORT = recv_sock.getsockname()[1]
	print user_id, "LISTENING:", (SELF_IP, SELF_PORT)
	thread.start_new_thread(start_server,(recv_sock,))

#all good
#hardcoded connection_request can be changed, but not a big deal
def send_details():
	global user_id, password, SELF_PORT
	init_sock = create_sock()
	init_sock.sendto(CONN_REQ+":"+user_id+":"+password+":"+str(SELF_IP)+":"+str(SELF_PORT), (SERV_IP, SERV_PORT))
	init_sock.close()

#improve
def deliver_msg(msg):
	sock = create_sock()
	sock.settimeout(SOCK_TIMEOUT)

	resp = ""
	for i in range(3):
		sock.sendto(user_id+":"+msg, (SERV_IP, SERV_PORT))
		try:
			resp, addr = sock.recvfrom(1024)
			if resp == "Message Received by Server: ("+msg+")":
				print resp
				break
		except socket.timeout:
			print "timeout"
			continue

	if resp == "":
		print "Message Not Sent: ("+msg+"): Server or Network is down"

	message_queue.remove(msg)
	sock.close()

def send_msg(msg):
	message_queue.append(msg)
	thread.start_new_thread(deliver_msg,(msg,))

def chat():
	global user_id
	while True:
		msg = raw_input()
		if msg == "list":
			sock = create_sock()
			sock.sendto(user_id+":"+msg, (SERV_IP, SERV_PORT))
			resp, addr = sock.recvfrom(1024)
			print resp
			sock.close()
			continue
		if ":" in msg:
			m = msg.split(":")
			if len(m) == 2 and m[0]:
				send_msg(msg)
				continue
		valid_usage()

if __name__=="__main__":
	if len(sys.argv) != 3:
		print "Usage: client.py <username> <password>"
		exit()

	user_id = sys.argv[1]
	password = sys.argv[2]

	setup_server()
	send_details()
	chat()
