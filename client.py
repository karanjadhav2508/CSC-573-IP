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

gbn_window = 4
next_seq = 0
expected_ack_seq = 0

messages = []
gbn_queue = []

def start_server(recv_sock):
	global done, expected_ack_seq
	while True:
		msg, addr = recv_sock.recvfrom(1024)

		if msg.startswith("gbn"):
			ack = msg.split(":")
			ack_gbn_seq = ack[1]
			ack_msg = ack[2]
			if int(ack_gbn_seq) == expected_ack_seq:
				expected_ack_seq = (expected_ack_seq + 1) % gbn_window
				print ack_msg
				del gbn_queue[0]
			else:
				print "Expected message ack not received. Resending all messages in gbn_queue"
				deliver_msgs_in_queue()
			continue

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

def deliver_msgs_in_queue():
	global messages, gbn_queue
	sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
	sock.settimeout(2)

	for i in range(len(gbn_queue)):
		msg = gbn_queue[i][1]
		gbn_seq = "gbn:" + str(gbn_queue[i][0])
		resp = ""

		sock.sendto(gbn_seq+":"+user_id+":"+msg, (SERV_IP, SERV_PORT))

	#resp, addr = sock.recvfrom(1024)
	#if resp == "Message Received by Server: ("+msg+")":
	#	print resp

	#if resp == "":
	#	print "Message Not Sent: ("+msg+"): Server or Network is down"

	#del gbn_queue[0]
	#if len(messages) > 0:
	#	msg = messages[0]
	#	del messages[0]
	#	gbn_queue.append([next_seq, msg])
	#	next_seq = (next_seq + 1) % gbn_window

	sock.close()

def store_message(msg):
	global messages, gbn_queue, gbn_window, next_seq
	if len(gbn_queue) < gbn_window:
		gbn_queue.append([next_seq, msg])
		next_seq = (next_seq + 1) % gbn_window
	else:
		messages.append(msg)	

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

		store_message(msg)
		thread.start_new_thread(deliver_msgs_in_queue,())

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
