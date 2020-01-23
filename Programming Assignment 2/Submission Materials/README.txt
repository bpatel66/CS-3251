CS 3251 Programming Assignment 2

## Team Work ##
	Client Side and this readme was written by Nestor Moreno, Server side and test output was written by Balkrishna Patel.

## How To Run ##
	To Run Client side, perform this command using Python 2:
		- python ttweetcli.py {ip_address} {port} {username} 
			- as an example: 'python ttweetcli.py 10.0.0.27 8080 Philip'
	To Run Server side, perform this command:
		- python ttweetsrv.py {port}
			- as an example: 'python ttweetsrv.py 8080'

	To Run commands inside client, see below section


## High level description ##

# Our client and server is written with Python 2 version. We utilized threading to concurrently send and receive message on both the client and server side.

# Our tweet client (ttweetcli) has several commands:
* tweet “<150 char max tweet>” <Hashtag>	# tweet out a message
* subscribe <Hashtag>				# subscribe to a hashtag
* unsubscribe <Hashtag>				# unsubscribe to a hashtag
* timeline					# display a list of received tweets 
* exit						# exit the client


# Our tweet server has one command:
* ttweetsrv <Port>
	- You can run ttweetsrv by doing: 'python ttweetsrv.py 8080' as an example. 


# For the client implementation:

	One thread is always waiting to receive a message, and the other thread is always waiting for a command to be entered by the client. 
	* The thread that receives any message places the message in a respective queue or list.
	
	- If the client gets a tweet message from the server, it places the 
	tweet in the user's timeline tweets list since the user is subscribed to one or	
	#ALL of the tweets in the message that is received.
	
	- If the client subscribes to any hashtag, a response will be sent back from the server, and the subscribe() method will wait for the respective subscribe_queue to not be empty to grab the response. After response is received,  the queue is set to be empty, and the subscribed hashtag is added to the client side subscription list keep which keeps tracks of active subscriptions.

	- If the client unsubscribes to any hashtag, the response is received the hashtag removed from both the server and the client side data structures. 
	
	- a timeline data structure list is kept on the client side to display the 
	received tweets sent by the server to the client. Any timeline command will 
	display the contents of the list and then clear the list completely.


		
 # For the server implementation:

	The server listens to any incoming connections and creates a thread for each client that is always waiting to receive a command. 

	The server has methods to handle client commands:

		- @HandleTweet: helper method for server to help handle an incoming tweet
		- @HandleSubscription: helper method for server to help handle a subscription request
		- @HandleUnsubscribe: helper method for server to help handle an unsubscribe request
		- @HandleExit: helper method for server to help handle an exit request
		- @OnNewClient: this method is invoked whenever a new client comes online, this mehtod validates that the user that is trying to log on isn't already logged on, then it begins to handle the commands that the user/client is sending to the server
		

	The server keeps a list of data structures explained below:
		* activeUsers = []
			- List that will hold the users that are active on the server
		* userToSocket = {}
			- # a dictionary that will map a username to a socket number
		* activeUserSubs = {}
			- # a dictionary that hold that active users and their subscriptions
	


	* When the client sends a tweet, each user in the activeUserSubs dictionary is sent a tweet if a hashtag they are subscribed to appears in the tweet or #ALL.
	* When the client sends a subscribe command, the hashtag is checked if it already exists in activeUserSubs dictionary, if it does not, then it is added to the user's 
		subscription list. A response is sent specifying the result of the operation.
	* When the client sends a unsubscribe command, the hashtag is checked if it does not exist in activeUserSubs dictionary, if it does exist, the hashtag is removed from the user's
		subscription list. A response is sent specifying the result of the operation.
	* When the client sends an exit command, the user is removed from activeUsers and their socket is closed and removed in userToSocket and removed from activeUserSubs dictionary.


## Notes:
	For the timeline command, you will see a difference between the timeline command in the test outputs and the actual output, the timeline was changed after the tests were run and it still behaves the same as it did but it will just look different when running the code. 

		- before it showed a dict (in test output), now when running the code it shows a beautified output.
