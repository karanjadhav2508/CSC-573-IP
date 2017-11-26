"# CSC-573-IP"

Run server : python server.py

Run client : python client.py username password

List users : list

Send msg   : username:message


NOTE:
- On connection, user receives an ack from server.
	- If "Connection Successful", user can send and receive messages.
	- If "Connection Failed", username already exists and wrong password is used. User needs to reconnect. Will not receive messages.
- On successful connection, "list" command will return a list of all the users except self.
- To send messages, type the receivers username followed by a colon (":") and then the message

