import socket
import thread
import time
import common

class client:
	def __init__(self, details):
		self.ip = details[0]
		self.port = int(details[1])
		self.expectedseqnum = 0

class Server:
	def setup(self):
		self.sock = common.create_sock()
		self.sock.bind(common.SERVER)
		print "server listening", common.SERVER

	def __init__(self, ip="127.0.0.1", port=5005):
		self.ip = ip
		self.port = port
		self.clients = {}
		self.sock = common.setup((ip, port))

	def start(self):
		while True:
			msg, addr = self.sock.recvfrom(1024)
			info = msg.split(":")
			if msg.startswith("new"):
				self.clients[info[1]] = client(info[2:])
			elif msg.startswith("msg"):
				receiver = info[3]
				c = self.clients[receiver]
				if (int(info[1])) == c.expectedseqnum:
					sender = info[2]
					receiver_sock = (c.ip, c.port)
					send_sock = common.create_sock()
					send_sock.sendto("msg_from:"+sender+":"+info[1]+":"+info[4], receiver_sock)
					c.expectedseqnum += 1
		self.sock.close()


if __name__ == "__main__":
	s = Server()
	s.start()
