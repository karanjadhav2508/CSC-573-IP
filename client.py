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

def start_server(recv_sock):
	global done
	while True:
		msg, addr = recv_sock.recvfrom(1024)
		print msg
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
	global user_id, SELF_PORT
	init_sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
	init_sock.sendto("0"+":"+user_id+"-"+str(SELF_IP)+","+str(SELF_PORT), (SERV_IP, SERV_PORT))
	init_sock.close()

def chat():
	global done, user_id
	while True:
		msg = raw_input()
		sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
		sock.sendto(user_id+":"+msg, (SERV_IP, SERV_PORT))
		resp, addr = sock.recvfrom(1024)
		print resp
		sock.close()
	while not done:
		time.sleep(1)

if __name__=="__main__":
	user_id = sys.argv[1]
	setup_server()
	send_details()
	chat()