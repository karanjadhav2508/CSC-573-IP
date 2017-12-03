import socket
import thread
import time
import random

TIMEOUT = 0.5
MSG_START = "Message: "
ACK = "ack"
DROP_PROB = 0.5

class RDT:
	def __init__(self, client):
		self.client = client

	def timer(self, old_base):
		start = time.time()
		while time.time() - start < TIMEOUT:
			continue
		if old_base == self.client.base:
			#print self.client.user, "timer",  old_base, "expired"
			for i in xrange(self.client.base + self.client.n):
				if i in self.client.sndpkt:
					self.udt_send(self.client.sndpkt[i])
			#print self.client.user, "resent messages."
			thread.start_new_thread(self.timer, (old_base,))
			#print self.client.user, "restarted timer", old_base

	def udt_send(self, msg):
		sock = self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(msg, (self.client.ip, self.client.recv_port))
		sock.close()

	#both methods being passed client's members explicitly, inspite of them being available
	#NOTE : need to possibly revisit this at a later time after testing
	@staticmethod
	def make_pkt(seqnum, msg):
		return str(seqnum)+":"+MSG_START + msg

	@staticmethod
	def make_ack(seqnum):
		return ACK+":"+str(seqnum)

	def rdt_send(self, msg):
		c = self.client
		while c.nextseqnum >= c.base + c.n:
			time.sleep(0.05)
		c.sndpkt[c.nextseqnum] = RDT.make_pkt(c.nextseqnum, msg)
		thread.start_new_thread(self.udt_send, (c.sndpkt[c.nextseqnum],))

		# TIMER - to be implemented
		temp_base = c.base
		if c.base == c.nextseqnum:
			#print c.user, "started timer", temp_base
			thread.start_new_thread(self.timer, (temp_base,))

		c.nextseqnum += 1

	def rdt_recv(self):
		c = self.client
		msg, addr = c.sock.recvfrom(1024)
		info = msg.split(":")

		#sender side receive for ACK
		if(info[0] == ACK):
			print c.user, "received ACK", info[1]
			c.base = int(info[1]) + 1
			#TIMER - to be implemented
			if c.base != c.nextseqnum:
				thread.start_new_thread(self.timer, (c.base,))
		#receiver side for regular messages
		elif c.expectedseqnum == int(info[0]):
			if random.uniform(0,1) > DROP_PROB:
				print msg
				self.udt_send(RDT.make_ack(c.expectedseqnum))
				c.expectedseqnum += 1





