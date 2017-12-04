#CSC-573-IP

#Chat Application using UDP with Go-Back-N

Team Members:
- Pranav Vaidya (psvaidya)
- Karan Jadhav (kjadhav)
- Sriram Guddati (skguddat)

Environment Settings: 
- Python needs to be installed

Running server:
- Open terminal (command line) and type "python server.py"

Running 2 (or more) client:
- Open another terminal (command line) and type "python client.py user1 pass1 127.0.0.1"
- Open another terminal (command line) and type "python client.py user2 pass2 127.0.0.1"

Client commands:
- list (lists users)
- user1: message (sends message to user1)
- exit (exits the code)

Test Cases:
1) Multiple​ ​ clients​ ​ connect​ ​ to​ ​ server​ ​ and​ ​ get​ ​ list​ ​ of​ ​ available​ ​ clients
	- Start server
	- Start 2 clients user1 and user2
	- type "list" from user1 terminal 
	
	Expected output: 
	- user1 sees output ['user2']

2) Communication between 2 clients (continuation from above)
	- Send messages to each other

	Expected output:
	- user1 receives messages sent by user2
	- user2 receives messages sent by user1
	- both users receive ack when message is received by server
	- both users receive ack when message is received by receiver

3) Sending messages when 1 client is offline (continuation from above)
	- Exit 2nd client user2
	- send multiple messages from user1 to user2

	Expected output:
	- user1 receives ack when message is received by server
	- server tries to send message to user2 but times out, retries 3 times and then saves messages

4) Reconnecting offline client (continuation from above)
	- Start 2nd client user2 again

	Expected output:
	- user2 receives all the messages sent earlier by user1 in the same order
	- user1 receives ack for all messages received by user2

5) Sending messages when server/network is down (continuation from above)
	- Stop the server (cntrl+C)
	- Send message from user1 to user2

	Expected output:
	- user1 is notified that message is not sent and server or network could be down

6) Logging in with wrong password (not continuation)
	- Start the server
	- Start client user1
	- Exit client user1
	- Agains tart client user1 with wrong password

	Expected output:
	- user1 is notified of connection failure as the username exists and password used is wrong


