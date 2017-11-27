"# CSC-573-IP"

Run server : python server.py

Run client : python client.py username password

List users : list

Send msg   : username:message


Functionality:
- On connection, user receives an ack from server.
	- If "Connection Successful", user can send and receive messages.
	- If "Connection Failed", username already exists and wrong password is used. User needs to reconnect. Will not receive messages.
- On successful connection, "list" command will return a list of all the users except self.
- To send messages, type the receivers username followed by a colon (":") and then the message
	- User client tries to send the message thrice. If it can't, it'll give message "Message Not Sent: (msg): Server or Network is down" and message has to be resent
	- Once server receives it, user gets acknowledgement "Message Received by Server: (msg)"
	- Server saves the message and tries to send it to receiver thrice
	- If receiver is offline during the 3 tries, all the pending saved messages to the receiver are sent immediately when the receiver comes back online
	- When receiver receives the message, it sends acknowledgement "ack:Message Received"
	- On receiving acknowledgement, server removes the saved message and sends acknowledgement to sender "Message Received by Client: (msg)"
- Offline messages supported. If user2 is not connected, and user1 sends many messages to user2, they are stored and user2 receives all the messages as soon as it comes online

Not Implemented:
- Currently using Stop and Wait functionality. Need to change to GoBack-N
- Currently, if server gets disconnected or reconnects, the clients also have to reconnect. The previously connected clients will not be able to send or receive messages.

