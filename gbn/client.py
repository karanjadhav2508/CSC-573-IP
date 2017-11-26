import socket
import thread
import time
import sys
import common

class receiver:
	def __init__(self):
		self.expectedseqnum = 0

class Client:
	def send_details(self):
		send_sock = common.create_sock()
		send_sock.sendto("new:"+self.username+":"+self.ip+":"+str(self.port), common.SERVER)
		send_sock.close()

	def start_server(self):
		while True:
			msg, addr = self.sock.recvfrom(1024)
			m = msg.split(":")
			if msg.startswith("ack"):
				print m
				self.base = int(m[1]) + 1
				if self.base != self.nextseqnum:
					thread.start_new_thread(self.start_timer, (self.base))
			elif msg.startswith("msg_from"):
				if m[1] not in self.receivers:
					self.receivers[m[1]] = receiver()
				if int(m[2]) == self.receivers[m[1]].expectedseqnum:
					print msg
					self.receivers[m[1]].expectedseqnum += 1
					ack_sock = common.create_sock()

	def __init__(self, username, ip="127.0.0.1"):
		self.username = username
		self.ip = ip
		self.nextseqnum = 0
		self.expectedseqnum = 0
		self.base = 0
		self.n = 0
		self.sndpkt = {}
		self.receivers = {}
		self.sock = common.setup((self.ip, 0))
		self.port = self.sock.getsockname()[1]
		thread.start_new_thread(self.start_server,())
		print self.username, "listening", (self.ip, self.port)
		self.send_details()

	@staticmethod
	def udt_send(msg):
		send_sock = common.create_sock()
		send_sock.sendto(msg, common.SERVER)
		send_sock.close()

	def start_timer(self, old_base):
		start = time.time()
		while time.time() - start < common.TIMEOUT:
			continue
		if old_base == self.base:
			for i in xrange(self.base+self.n):
				self.udt_send(self.sndpkt[i])
			thread.start_new_thread(self.start_timer, (old_base,))

	def make_pkt(self, data):
		return "msg:"+str(self.nextseqnum)+":"+self.username+":"+data

	def rdt_send(self, msg):
		while self.nextseqnum<self.base+self.n:
			sleep(0.05)

		self.sndpkt[self.nextseqnum] = self.make_pkt(msg)
		thread.start_new_thread(Client.udt_send,(self.sndpkt[self.nextseqnum],))
		if(self.base==self.nextseqnum):
			thread.start_new_thread(self.start_timer, (self.base,))
		self.nextseqnum += 1

	def chat(self):
		while True:
			msg = raw_input()
			self.rdt_send(msg)

if __name__ == "__main__":
	c = Client(sys.argv[1])
	c.chat()