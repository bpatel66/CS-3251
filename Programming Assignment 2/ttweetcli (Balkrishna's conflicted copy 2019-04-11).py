import pickle
import socket
import sys
import shlex
import re
import thread
import threading
#from multiprocessing import Process

BUFFER_SIZE = 100000
username = ''
subscribe_count = 0
tag_subscriptions = []
timeline_tweets = []
sub_queue = []
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


def validate_username(sock, argv):
    print("\nValidating Username for uniqueness on Server")
    # try:
    """ Validates the uniqueness of the username by checking with the Server to see if the Username is already taken"""
    dict_check = {'command' : 'check_username', 'username': argv[3]}
    # encode the message dict with pickle
    check_data = pickle.dumps(dict_check)
    #### TEMP: for now, server response will be harcoded as example, uncomment the lines below for actual implementation ####
    # send the encodeded message data to the server
    sock.sendall(check_data)
    # get the confirmation from the server that the message was recieved
    response = sock.recv(BUFFER_SIZE)
    # unserialize the response
    server_response = pickle.loads(response)
    #print(server_response)
    # temp harcoded:
    #server_response = {'unique' : True}
    # decode the encoded message from the server
    #print('Server response for username uniqueness: ' + str(server_response))

    # server sends a dict like: response = {'unique': False}
    # check if server returns true for unique username
    if server_response['unique'] is True:
        print("\nusername is unique!\n")
        global username
        username = argv[3]
    else:
        print("\nERROR: username is NOT unique, or the server is full, retry entering the server with a new username or try again later")
        exit(0)
    # except:
    #     print("ERROR: unable to verify if username is Unique. Exiting.")
    #     exit(0)


def main(argv):
    # if the inputted command does not have the appropriate number of arguements (4 arguments) an error message will be displayed explaining how to use the command
    if not len(argv) == 4:
        print(argv)
        err_msg()
        exit(0)

    # validate arguments (and username), and retrieve the connection socket object
    sock = preliminary_validation_setup(argv)
    #sock.settimeout(1)

    #print("creating thread to send commands to server")
    
    #thread.start_new_thread(command_loop, (sock,))
    print("creating thread to recieve tweets")
    thread.start_new_thread(receive_tweets, (sock,))

    # run indefinetely until client exits
    while (1):
        # retrieve command args
        command = raw_input('Enter Command:')
        # split command arguments by whitespace while perserving substrings whitespaces
        command_args = shlex.split(command)
        print("\ncommand provided:" + str(command_args))
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
            print("Error: Command not recognized. Available Commands:")
            print('tweet "<150 char max tweet>" <Hashtag>')
            print('subscribe <Hashtag>')
            print('unsubscribe <Hashtag>')
            print('timeline')
            print('exit')

    sock.close()
    exit(0)


def receive_tweets(sock):
    # receive incoming messages
    global timeline_tweets
    global unsub_queue
    global sub_queue

    while True:
        print('waiting to recv a response from server...')
        encodedMessage = sock.recv(BUFFER_SIZE)
        print('\nrecieved a message from server.')
        # decode the encoded message from the server
        decodedMessage = pickle.loads(encodedMessage)
        print('server message: ' + str(decodedMessage))

        if decodedMessage['command'] == 'subscribe':
            sub_queue.append(decodedMessage)
            print("got subscribe message from server, storing in queue.")
        elif decodedMessage['command'] == 'unsubscribe':
            unsub_queue.append(decodedMessage)
            print("got unsubscribe message from server, storing in queue.")
        elif decodedMessage['command'] == 'tweet':
            timeline_tweets.append(decodedMessage)
            print("got tweet message from server, storing in queue.")




def tweet_cli(sock, command_args):
    """ tweet client method that validates tweet content and hashtags and sends them to the server """
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
    if len(hashtag_list) == 0:
        print("Error: invalid hashtags provided")
        return

    # send a message to the server: dict_msg = {'command' : '', 'hashtag' : '', 'tweet' : '', 'username' : ''}
    dict_msg['command'] = 'tweet'
    dict_msg['hashtag'] = hashtag_list
    dict_msg['tweet'] = tweet
    # tell python that username reference is to the global username var
    global username
    dict_msg['username'] = username

    print("Sending tweet to the server as dictionary: " + str(dict_msg))
    # encode the message dict with pickle
    data_tweet = pickle.dumps(dict_msg)

    # send the encodeded message data to the server
    sock.sendall(data_tweet)
    return    


def subscribe_cli(sock, command_args):
    print("in subscribe cli method")
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
    # check if #ALL hashtag is passed
    if not subscribe_count + 1 > 3:
    
        dict_sub = {'command' : 'subscribe', 'hashtag': tag_list[0], 'username' : username}

        print("Sending subscription tag to the server as dictionary: " + str(dict_sub))
            # encode the message dict with pickle
        data_sub = pickle.dumps(dict_sub)

        ## send the encodeded message data to the server
        sock.sendall(data_sub)
        
        ## get the confirmation from the server that the message was recieved
        while len(sub_queue) < 1:
            print('waiting for response from server to store subscription queue')


        print("got a response from the server in subscribe")
        ## unserialize the response
        #recv_lock.release()
        server_response = sub_queue[0]
        sub_queue = []

        if server_response['validation'] == 'too_many_sub':
            print("ERROR: More than 3 hashtag subscriptions not allowed.")
        elif server_response['validation'] == 'already_subbed':
            print("ERROR: Already subscribed to the hashtag.")
        elif server_response['validation'] == 'subscribed':
            print('SUCESS: Subscribed to the hashtag ' + hashtag)
            tag_subscriptions.append(tag_list[0])
            subscribe_count += 1

        print('final subscribe count: ' + str(subscribe_count))
        print('final tag subscriptions list: ' + str(tag_subscriptions))
    else:
        print("ERROR: Can not have more than 3 hashtag subscriptions, please remove a hashtag subscription from this list by doing 'unsubscribe <hashtag>:' " + str(tag_subscriptions))
    return


def unsubscribe_cli(sock, command_args):
    print("in unsubscribe cli method:")
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
        print("Only one hashtag can be provided bro")
        return

    # check subscribe count is not 0
    if subscribe_count > 0:

        dict_unsub = {'command' : 'unsubscribe', 'hashtag': tag_list[0], 'username' : username}

        print("Sending unsubscribe tag to the server as dictionary: " + str(dict_unsub))
            # encode the message dict with pickle
        data_unsub = pickle.dumps(dict_unsub)

        #### TEMP: for now, server response will be harcoded as example, uncomment the lines below for actual implementation ####

        ## send the encodeded message data to the server
        sock.sendall(data_unsub)
        ## get the confirmation from the server that the message was recieved
        while len(unsub_queue) < 1:
            print('waiting for response from server to store unsubscription queue')

        print("got a response from the server in unsubscribe")
        server_response = unsub_queue[0]
        unsub_queue = []
        

        if server_response['validation'] == 'unsubscribed':
            print("SUCESS: Unsubscribed to the hashtag " + hashtag)
            tag_subscriptions.remove(tag_list[0])
            subscribe_count -= 1
        elif server_response['validation'] == 'sub_does_not_exist':
            print("ERROR: No active subscription exists for the hashtag " + hashtag)
        elif server_response['validation'] == 'not_subbed_to_anything':
            print("ERROR: No active subscriptions available.")

        print('final subscribe count: ' + str(subscribe_count))
        print('final tag subscriptions list: ' + str(tag_subscriptions))
    else:
        print("ERROR: the hashtag specified is not in the active hashtag subscriptions or no hashtags subscriptions exist: " + str(tag_subscriptions))
    return


def timeline_cli(sock):
    print("in timeline cli method")
    global username
    global timeline_tweets
    if len(timeline_tweets) == 0:
        print("No tweets in timeline.")
    else:
        print("\nlength of timeline: " + str(len(timeline_tweets)))
        print("Timeline: ")
        for tweet in timeline_tweets:
            print(username + ' ' + str(tweet))
    timeline_tweets = []
    return


def exit_cli(sock):
    print("in exit cli method")
    global username
    dict_exit = {'command' : 'exit', 'username' : username}
    data_exit = pickle.dumps(dict_exit)

    ## send the encodeded message data to the server
    sock.sendall(data_exit)
    sock.close()
    exit(0)
    #else:
        #print("did not recieve a OK response to end connection.")
    return



def validate_listify_hashtag(hashtag):
    print("validating hashtag: " + str(hashtag))

    if not hashtag[0] == "#":
        print('Hashtag must begin with a #. Exiting.')
        return []

    # split hashtag by # and filter out empty values
    hashtag_list = hashtag.split('#')
    # remove first and last empty strings in list due to split()
    hashtag_list = hashtag_list[1:len(hashtag_list)]

    print("provided hashtags for parsing: " + str(hashtag_list))

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
    print('successful parsing of hashtag list: ' + str(hashtag_list))
    return hashtag_list



if __name__ == "__main__":
    main(sys.argv)

sys.exit(0)