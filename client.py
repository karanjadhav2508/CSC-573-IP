import socket
import thread
import time
import sys

SERV_IP = "127.0.0.1"
SERV_PORT = 5005
SELF_IP = "127.0.0.1"
SELF_PORT = 0
RAND_PORT = 0

done = False
user_id = ""
password = ""

message_queue = []

def start_server(recv_sock):
	global done
	while True:
		msg, addr = recv_sock.recvfrom(1024)
		print msg

		if msg.startswith("Message from "):
			recv_sock.sendto("ack:Message Received", addr)
	recv_sock.close()
	done = True

def setup_server():
	global SELF_PORT
	recv_sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
	recv_sock.bind((SELF_IP, RAND_PORT))
	SELF_PORT = recv_sock.getsockname()[1]
	print user_id, "LISTENING:", (SELF_IP, SELF_PORT)
	thread.start_new_thread(start_server,(recv_sock,))

def send_details():
	global user_id, password, SELF_PORT
	init_sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
	init_sock.sendto("connection_request:"+user_id+":"+password+":"+str(SELF_IP)+":"+str(SELF_PORT), (SERV_IP, SERV_PORT))
	init_sock.close()

def deliver_msg(msg):
	sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
	sock.settimeout(2)

	resp = ""
	for i in range(3):
		sock.sendto(user_id+":"+msg, (SERV_IP, SERV_PORT))
		try:
			resp, addr = sock.recvfrom(1024)
			if resp == "Message Received by Server: ("+msg+")":
				print resp
				break
		except socket.timeout:
			continue

	if resp == "":
		print "Message Not Sent: ("+msg+"): Server or Network is down"

	message_queue.remove(msg)
	sock.close()

def chat():
	global done, user_id
	while True:
		msg = raw_input()
		if msg == "list":
			sock = socket.socket(socket.AF_INET,
                                     socket.SOCK_DGRAM)
			sock.sendto(user_id+":"+msg, (SERV_IP, SERV_PORT))
			resp, addr = sock.recvfrom(1024)
			print resp
			sock.close()
			continue

		if len(msg.split(":")) == 1:
			print "Invalid input. Available commands:"
			print "- list"
			print "- username: message"
			continue

		message_queue.append(msg)
		thread.start_new_thread(deliver_msg,(msg,))

	while not done:
		time.sleep(1)

if __name__=="__main__":
	if len(sys.argv) != 3:
		print "Usage: client.py <username> <password>"
		exit()

	user_id = sys.argv[1]
	password = sys.argv[2]

	setup_server()
	send_details()
	chat()
