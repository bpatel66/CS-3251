import pickle
import socket
import sys
import shlex
import re
import thread
import threading
# Variable to hold the size of the receive buffer
BUFFER_SIZE = 100000
# Global Variable that will hold the client's username
username = ''
# Global Variable that will hold the number of active subscriptions that the user has
subscribe_count = 0
# List of the hashtag the user is subbed to
tag_subscriptions = []
# List of the tweets that are to be displayed the next time the client calls the timeline command
timeline_tweets = []
# Queue for receiving a subscription validation message from the server used in subscribe()
sub_queue = []
# Queue for receiving a unsubscription validation message from the server used in unsubscribe()
unsub_queue = []


recv_lock = thread.allocate_lock()
lock = threading.Lock()

# Initialize a dictionary standard for client and server to communicate, initially all key values are empty
dict_msg = {'command' : '', 'hashtag' : '', 'tweet' : '', 'username' : ''}

"""
This method is to display an error message on the terminal
the message will also provide the suggestted fixes for the client side request
"""
def err_msg():
    print('ERROR: It seems the inputted command does not fit the correct format please refer the the messaages below as to how to structure the command.')
    print('')
    print('How to upload message to server:  ./ttweetcl <ServerIP> <ServerPort> <Username> ')
    #print('\"message\" input the message with quotes and there is a character limit of 150 also if you don\'t want to send any message include open and closed quotes ')
    print('')

"""  
@preliminary_validation_setup: helper method that erforms a check on the arguments passed by the client, and then sets up the connection

@argv: argument passed in from the terminal
"""
def preliminary_validation_setup(argv):
    # if the username is not alphanumerics, exit gracefully, otherwise setup connection
    if not argv[3].isalnum():
        print(argv)
        err_msg()
        exit(0)
    # the ServerIP is parsed from argv
    server_ip = argv[1]
    # the ServerPort is parsed from argv
    server_port = int(argv[2])
    # Now to set up the TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # set a timeout if socket can not connect after 15 seconds
    #sock.settimeout(15)
    print("Attempting to connect to server")
    # attempting connect with the server and the port
    sock.connect((server_ip, server_port))
    # validate uniqueness of username  
    validate_username(sock, argv)
    # return the sock for further usage
    return sock

"""  
@validate_username: Validates the uniqueness of the username by checking with the Server to see if the Username is already taken

@sock: this client's socket that it will use to send to and recieve information from the server with
@argv: the argument that was passed into terminal when the client was instatiated
"""
def validate_username(sock, argv):
    print("\nValidating Username for uniqueness on Server")
    # create a dict with the command: check_username, and the user's username
    dict_check = {'command' : 'check_username', 'username': argv[3]}
    # encode the message dict with pickle
    check_data = pickle.dumps(dict_check)
    # send the encodeded message data to the server
    sock.sendall(check_data)
    # get the confirmation from the server that the message was recieved
    response = sock.recv(BUFFER_SIZE)
    # unserialize the response
    server_response = pickle.loads(response)
    # server sends a dict like: response = {'unique': False}
    # check if server returns true for unique username
    if server_response['unique'] is True:
        print("\nusername is unique!\n")
        # if the user name is unique then set the username variable to the inputted username
        global username
        username = argv[3]
    else:
        # if the the username was not valid or if the server is already full display an error message telling the client how to proceed and close the connection
        print("\nERROR: username is NOT unique, or the server is full, retry entering the server with a new username or try again later")
        exit(0)

"""  
@main: this is the main method for the client, this method is invoked when the client is instantiated and will try and connect to the server.

@argv: the argument that was passed in at the terminal when the client was instantiated
"""
def main(argv):
    # if the inputted command does not have the appropriate number of arguements (4 arguments) an error message will be displayed explaining how to use the command
    if not len(argv) == 4:
        print(argv)
        err_msg()
        exit(0)
    # validate arguments (and username), and retrieve the connection socket object
    sock = preliminary_validation_setup(argv)
    # create a new thread to allow the client to listen for messages from the server    
    thread.start_new_thread(receive_tweets, (sock,))
    # run indefinetely until client exits
    while (1):
        # retrieve command args
        command = raw_input('Enter Command: ')
        # split command arguments by whitespace while perserving substrings whitespaces
        command_args = shlex.split(command)
        # after the argument is parsed, determine which command is inputted at the terminal
        if len(command_args) == 3 and command_args[0] == "tweet":
            tweet_cli(sock, command_args)
        elif len(command_args) == 2 and command_args[0] == "subscribe":
            subscribe_cli(sock, command_args)
        elif len(command_args) == 2 and command_args[0] == "unsubscribe":
            unsubscribe_cli(sock, command_args)
        elif len(command_args) == 1 and command_args[0] == "timeline":
            timeline_cli(sock)
        elif len(command_args) == 1 and command_args[0] == "exit":
            exit_cli(sock)
        else:
            # if an invalid command is inputted send an error message that tells the client how to proceed
            print("Error: Command not recognized. Available Commands:")
            print('tweet "<150 char max tweet>" <Hashtag>')
            print('subscribe <Hashtag>')
            print('unsubscribe <Hashtag>')
            print('timeline')
            print('exit')
    sock.close()
    exit(0)

"""  
@receive_tweets: helper method that allows the client recieve messages/tweets from the server

@sock: the client's socket that it will be listening with
"""
def receive_tweets(sock):
    global timeline_tweets
    global unsub_queue
    global sub_queue

    while True:
        # store the encoded message receieved from the server in a variable
        encodedMessage = sock.recv(BUFFER_SIZE)
        #print('\nrecieved a message from server.')
        # decode the encoded message from the server
        decodedMessage = pickle.loads(encodedMessage)
        # determine the command that was sent from the server to determine how the client needs to manipulate its various data structures
        if decodedMessage['command'] == 'subscribe':
            sub_queue.append(decodedMessage)
            #print("got subscribe message from server, storing in queue.")
        elif decodedMessage['command'] == 'unsubscribe':
            unsub_queue.append(decodedMessage)
            #print("got unsubscribe message from server, storing in queue.")
        elif decodedMessage['command'] == 'tweet':
            timeline_tweets.append(decodedMessage)
            #print("got tweet message from server, storing in timeline.")
""" 
@tweet_cli: helper method to help the client send out tweets to the server as well as validate whether the tweet is valid

@sock: the client's socket that it will use to send and recieve message to and from the server
@command_args: argument that is passed in from the terminal
"""
def tweet_cli(sock, command_args):
    tweet = command_args[1]
    print("tweet: " + tweet + " with length " + str(len(tweet)))
    # validate tweet message length
    if len(tweet) < 1:
        print("ERROR: tweet is less than 1 character.")
        return
    if len(tweet) > 150:
        print('ERROR: tweet is longer than 150 characters.')
        return
    # validate hashtag(s) syntax and return hashtags as a list if more than 1
    hashtag_list = validate_listify_hashtag(command_args[2])
    # validate that there is a valid number of hashtags in the tweet
    if len(hashtag_list) == 0:
        print("Error: invalid hashtags provided")
        return
    if len(hashtag_list) > 8:
        print("Error: Too many Hashtags, max limit: 8")
        return
    # check that all the Tags are within the character limit
    for h in hashtag_list:
        if len(h) > 25:
            print("Error: " + h + " is too long to be a hashtag")
            return
    # constuct the dict containing the tweet that will be sent to the server
    dict_msg['command'] = 'tweet'
    dict_msg['hashtag'] = hashtag_list
    dict_msg['tweet'] = tweet
    # tell python that username reference is to the global username var
    global username
    dict_msg['username'] = username
    # encode the message dict with pickle
    data_tweet = pickle.dumps(dict_msg)
    # send the encodeded message data to the server
    sock.sendall(data_tweet)
    print('Tweet was sent to the server')
    return    

"""  
@subscribe_cli: helper method to handle a subscribe command from the user

@sock: the client's socket that it will use to send and recieve messages to and from the server
@command_args: the argument that was passed in from the terminal
"""
def subscribe_cli(sock, command_args):
    # tell python that 'subscribe_count' and 'tag_sub' vars used in this scope is reffering to global
    global subscribe_count
    global tag_subscriptions
    global username
    global sub_queue
    # validate hashtag using helper method
    hashtag = command_args[1]
    tag_list = validate_listify_hashtag(hashtag)
    # perform checks - only one hashtag should exist
    if not len(tag_list) == 1:
        print("Only one hashtag can be provided bro")
        return
    if len(tag_list[0]) > 25:
        print("Hashtags are limited to 25 characters")
        return
    # check if #ALL hashtag is passed
    if not subscribe_count + 1 > 3:
        # create the base dict that will hold the subscribe command, the hashtag that is being subbed to, and the user's username.
        dict_sub = {'command' : 'subscribe', 'hashtag': tag_list[0], 'username' : username}
        # encode the message dict with pickle
        data_sub = pickle.dumps(dict_sub)
        # send the encodeded message data to the server
        sock.sendall(data_sub)
        print("The subscription request was sent to the server")
        # get the confirmation from the server that the message was recieved
        print('waiting for response from server for the subscription..')
        while len(sub_queue) < 1:
            pass
        print("Received a response from the server")
        # grab the servers response from and store it into the queue
        server_response = sub_queue[0]
        sub_queue = []
        # check the response from the server and see if the subscription was accepted or not
        if server_response['validation'] == 'too_many_sub':
            print("ERROR: More than 3 hashtag subscriptions not allowed.")
        elif server_response['validation'] == 'already_subbed':
            print("ERROR: Already subscribed to the hashtag.")
        elif server_response['validation'] == 'subscribed':
            print('SUCCESS: Subscribed to the hashtag ' + hashtag)
            tag_subscriptions.append(tag_list[0])
            subscribe_count += 1
        print('You are currently subscribed to: ' + str(subscribe_count) + " hashtags")
        print('Here are the hashtags you are currently subscribed to: ' + str(tag_subscriptions))
    else:
        print("ERROR: Can not have more than 3 hashtag subscriptions, please remove a hashtag subscription from this list by doing 'unsubscribe <hashtag>:' " + str(tag_subscriptions))
    return

"""  
@unsubscribe_cli: helper method to handle an unsubscribe command from the user

@sock: the client's socket that it will use to send and recieve messages to and from the server
@command_args: the argument that was passed in from the terminal
"""
def unsubscribe_cli(sock, command_args):
    # tell python that 'subscribe_count' and 'tag_sub' vars used in this scope is reffering to global
    global subscribe_count
    global tag_subscriptions
    global username
    global unsub_queue
    # validate hashtag using helper method
    hashtag = command_args[1]
    tag_list = validate_listify_hashtag(hashtag)
    # perform checks - only one hashtag should exist
    if not len(tag_list) == 1:
        print("Only one hashtag is allowed")
        return
    # check subscribe count is not 0
    if subscribe_count > 0:
        # create a diction to be sent the server
        dict_unsub = {'command' : 'unsubscribe', 'hashtag': tag_list[0], 'username' : username}
        # encode the message dict with pickle
        data_unsub = pickle.dumps(dict_unsub)
        ## send the encodeded message data to the server
        sock.sendall(data_unsub)
        print('Unsubscribe request sent to the server')
        ## get the confirmation from the server that the message was recieved
        print('Waiting for response from server for the unsubscription..')
        while len(unsub_queue) < 1:
            pass
        print("Received a response from the server for the unsubscribe request")
        server_response = unsub_queue[0]
        unsub_queue = []
        # check the server response if the unsubscribe request was validated
        if server_response['validation'] == 'unsubscribed':
            print("SUCESS: Unsubscribed to the hashtag " + hashtag)
            tag_subscriptions.remove(tag_list[0])
            subscribe_count -= 1
            removeFromTimeline(tag_list[0])
        elif server_response['validation'] == 'sub_does_not_exist':
            print("ERROR: No active subscription exists for the hashtag " + hashtag)
        elif server_response['validation'] == 'not_subbed_to_anything':
            print("ERROR: No active subscriptions available.")

        print('You are now subscribed to: ' + str(subscribe_count) + ' hashtags')
        print('Here are the hashtags you are subscribed to: ' + str(tag_subscriptions))
    else:
        print("ERROR: the hashtag specified is not in the active hashtag subscriptions or no hashtags subscriptions exist: " + str(tag_subscriptions))
    return


"""  
@hashtag: helper method to remove tweets containing a single hashtag from unsubscribe()

"""
def removeFromTimeline(hashtag):
    global timeline_tweets
    deleted = False
    tweetsToDelete = []
    #print("Initial timeline before deletion: " + str(timeline_tweets))
    for tweet in timeline_tweets:
        if hashtag in tweet['tags']:
            if len(tweet['tags']) == 1:
                #print('only one hashtag in timeline, removing: ' + str(tweet))
                tweetsToDelete.append(tweet)
            elif len(tweet['tags']) > 1 and not deleted:
                #print('more than one hashtag in tweet, removing only once: ' + str(tweet))
                tweetsToDelete.append(tweet)
                deleted = True
    #print('tweets marked for deletion: ' + str(tweetsToDelete))
    for tweet in tweetsToDelete:
        if tweet in timeline_tweets:
            timeline_tweets.remove(tweet)
    #print('final timeline for debugging: ' + str(timeline_tweets))



"""  
@timeline_cli: helper method to handle a timeline command from the user

@sock: the client's socket that it will use to communicate with the server
"""
def timeline_cli(sock):
    global username
    global timeline_tweets
    # display the user's timeline
    if len(timeline_tweets) == 0:
        print("No tweets in timeline.")
    else:
        # print("\nlength of timeline: " + str(len(timeline_tweets)))
        print("Timeline: ")
        for tweet in timeline_tweets:
            tags = ''
            for tag in tweet['tags']:
                tags += '#' + tag
            print('Client: ' + username + ', Sender: ' + str(tweet['user']) + ', tweet: ' + str(tweet['message']) + ', hastags: ' + tags)
    # clear the timeline so that next time new tweets will be displayed
    timeline_tweets = []
    return

"""  
@exit_cli: helper method to handle an exit command from the user

@sock: the client's socket that it will use to communicate with the server
"""
def exit_cli(sock):
    global username
    # the dict that will send the request to the server
    dict_exit = {'command' : 'exit', 'username' : username}
    # encode the dict to be sent
    data_exit = pickle.dumps(dict_exit)
    # send the encodeded message data to the server
    sock.sendall(data_exit)
    print('Good bye...')
    # close the socket
    sock.close()
    # close the client
    exit(0)
    return

"""  
@validate_listify_hashtag: helper method that will put the inputted hashtags into a list

@hashtag: hashtags that are going to added to a list of hashtags that will be sent to the server
"""
def validate_listify_hashtag(hashtag):
    # validate the hashtag
    if not hashtag[0] == "#":
        print('Hashtag must begin with a #. Exiting.')
        return []
    # split hashtag by # and filter out empty values
    hashtag_list = hashtag.split('#')
    # remove first and last empty strings in list due to split()
    hashtag_list = hashtag_list[1:len(hashtag_list)]
    # if more than 8 hashtag units or when splitting a # appears in the list,
    # or empty hashtag or > 25 characters, or tag is not alphaneumeric, fail and return back to main
    for tag in hashtag_list:
        if len(hashtag_list) < 9 and len(tag) == 0:
            print('ERROR: A # can not be followed by another # without at least one character seperating it (i.e. ## is invalid).')
            return []
        if len(hashtag_list) > 8:
            print('ERROR: Hashtag count exceeds maximum of 8 units.')
            return []
        if len(tag) > 25:
            print('ERROR: hashtag is longer than 25 characters. Must be between 1 and 25 characters long.')
            return []
        if not tag.isalnum():
            print('ERROR: hashtag "' + str(tag) + '" must be alphanumerical.')
            return []
    #print('successful parsing of hashtag list: ' + str(hashtag_list))
    return hashtag_list


if __name__ == "__main__":
    main(sys.argv)

sys.exit(0)