Name: Balkrishna Patel
Email: bpatel66@gatech.edu
____________________________________________________________________________________________________________________
Files:
	ttweetcl.py:
		this is the client code
	ttweetser.py:
		this is the server code
	Both files are commented explaining what is going on with the code.
____________________________________________________________________________________________________________________
Compiling and Running the Client and Server:
	-- there is no need to compile the code seperately when you run commands compilation will occur            automatically
	1. first run the server code with the following command:
		python ttweetser.py <Port Number>
			you can choose a port number between 13000 and 14000 by replacing the <Port Number> with the 			port number
	
	2. next you can run the client in download or upload mode with the following commands:
		- download command:
			python ttweetcli.py -d <Server IP> <Server Port>
				this is the download command replace <Server IP> and the <Server Port> with their 				respective values
		- upload command:
			python ttweetcli.py -u <Server IP> <Server Port> "message" 
				to upload a message replace the <Server  IP> and <Server Port> with thier respective 				values and message with the message you would like to send (include the quotes even 				when you want to send an empty message)
	IMPORTANT: Read the limitatios section so limitations that the upload command may have
____________________________________________________________________________________________________________________
Output from Testing Senarior:
Server:

python ttweetser.py 13000
Server: 192.168.44.1 is listening on Port: 13000
listening.....
Client has connected to Server
listening.....
Client has connected to Server
listening.....
Client has connected to Server
listening.....
Client has connected to Server
listening.....
Client has connected to Server
listening.....
Client has connected to Server
listening.....
Client has connected to Server
listening.....
	
	
Client:

-bash-4.1$ python ttweetcl.py -d 130.207.114.30 13000
Attempting to connect to server
Downloading message from Server: 130.207.114.30 with Port Number: 13000
The message from the Server: EMPTY MESSAGE
-bash-4.1$ python ttweetcl.py -u 130.207.114.30 13000 "You should select a port for your ttweet service. We recommend something between say 13000 and 14000. It is wise to provide the server port as input to the server and not to hard code the server port in the program. Note that if your server crashes, its port number may not be usable for a short period of time afterwards (for reasons we will explain later) so it is best to choose a new port number when you restart it."

ERROR: The character limit for the message is 150
-bash-4.1$ python ttweetcl.py -d 130.207.114.30 13000
Attempting to connect to server
Downloading message from Server: 130.207.114.30 with Port Number: 13000
The message from the Server: EMPTY MESSAGE
-bash-4.1$ python ttweetcl.py -u 130.207.114.30 13000 "Hello this is valid message1"
Attempting to connect to server
Sending message to Server: 130.207.114.30 with Port Number: 13000
The Message that is currently on the server is: Upload was Successfull!!!
-bash-4.1$ python ttweetcl.py -d 130.207.114.30 13000                               
Attempting to connect to server
Downloading message from Server: 130.207.114.30 with Port Number: 13000
The message from the Server: Hello this is valid message1
-bash-4.1$ python ttweetcl.py -u 130.207.114.30 13000 "Hello this is valid message2"
Attempting to connect to server
Sending message to Server: 130.207.114.30 with Port Number: 13000
The Message that is currently on the server is: Upload was Successfull!!!
-bash-4.1$ python ttweetcl.py -d 130.207.114.30 13000                               
Attempting to connect to server
Downloading message from Server: 130.207.114.30 with Port Number: 13000
The message from the Server: Hello this is valid message2
-bash-4.1$ python ttweetcl.py -u 130.207.114.30 13000 "You should select a port for your ttweet service. We recommend something between say 13000 and 14000. It is wise to provide the server port as input to the server and not to hard code the server port in the program. Note that if your server crashes, its port number may not be usable for a short period of time afterwards (for reasons we will explain later) so it is best to choose a new port number when you restart it.3"

ERROR: The character limit for the message is 150
-bash-4.1$ python ttweetcl.py -d 130.207.114.30 13000
Attempting to connect to server
Downloading message from Server: 130.207.114.30 with Port Number: 13000
The message from the Server: Hello this is valid message2
____________________________________________________________________________________________________________________
Disclaimer: 
	The client and server code were both written in python 3.6 and I ran them on the Shuttle Servers with the 	test scenarios and no error realated to python syntax or method calls were outputted so I assumed that both 	files work.
____________________________________________________________________________________________________________________
Limitations:
	Because I add a token to the front of the each request I need to spilt the message that the server recieves 	on the character ` so please avoid using the character ` in your message as it may cause your message to not 	be recieved correctly.
____________________________________________________________________________________________________________________
Citations:
	https://realpython.com/python-sockets/
	https://docs.python.org/2/howto/sockets.html
	https://pymotw.com/2/socket/tcp.html
