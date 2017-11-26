import time
import thread

class some_class:
	def __init__(self):
		self.x = 5
	def t_func(self):
		self.x += 1

s = some_class()
thread.start_new_thread(s.t_func,())
time.sleep(2)
print s.x
