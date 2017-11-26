import socket
import sys
import thread
import time
from rdt import *

WINDOW_SIZE = 3

class Client:
	def setup(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.ip, self.port))
		while True:
			self.rdt.rdt_recv()

	def __init__(self, user, port, recv_port, ip="127.0.0.1"):
		self.baseLock = False
		self.user = user
		self.port = port
		self.recv_port = recv_port
		self.ip = ip
		#rdt service
		self.rdt = RDT(self)
		#gbn variables
		self.base = 0
		self.n = WINDOW_SIZE
		self.nextseqnum = 0
		self.expectedseqnum = 0
		self.sndpkt = {}
		#start receiver thread
		thread.start_new_thread(self.setup, ())

	def chat(self):
		while True:
			msg = raw_input()
			self.rdt.rdt_send(msg)

if __name__ == "__main__":
	c = Client(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
	c.chat()

	# msg_file = raw_input()
	# time.sleep(2)
	# with open(msg_file) as f:
	# 	for line in f:
	# 		#print c.user, "sending", line
	# 		c.rdt.rdt_send(line)
	# 		time.sleep(1.0)
	# print c.user, "waiting for pending messages"
	# time.sleep(20)