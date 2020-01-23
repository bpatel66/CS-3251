import socket
import sys
import pickle
import thread
# List that will hold the users that are active on the server
activeUsers = []
# a dictionary that will map a username to a socket number
userToSocket = {}
# a dictionary that hold that active users and their subscriptions
activeUserSubs = {}
# store the buffer size in a variable
BUFFER_SIZE = 100000

""" 
@HandleTweet: helper method for server to help handle an incomming tweet

@decodedMessage: the decoded dicationary that contains the tweet command, the list of hashtags that user tagged, the tweet itself, and the user's username
"""
def HandleTweet(decodedMessage, clientSocket):
    # construct the tweet to send to the users
    tweet = {'message': decodedMessage['tweet'], 'tags': decodedMessage[
        'hashtag'], 'user': decodedMessage['username'], 'command': 'tweet'}
    print('\n ' + decodedMessage['username'] + " has sent out a tweet")
    # loop through all the active users on the server
    for u in activeUsers:
        # if the user has 'ALL' in their subscriptions send them the tweet
        if 'ALL' in activeUserSubs[u]:
            message = pickle.dumps(tweet)
            print('sending tweet to: ' + str(u))
            userToSocket[u].sendall(message)
        # if the user doesn't have 'ALL' in their subscriptions then check
        # the users subscriptions if they are subscribed to the any of the
        # tweet's hashtags if yes the send the tweet to the user
        else:
            for sub in activeUserSubs[u]:
                if sub in decodedMessage['hashtag']:
                    message = pickle.dumps(tweet)
                    print('sending tweet to: ' + str(u))
                    userToSocket[u].sendall(message)

""" 
@HandleSubscription: helper method for server to help handle a subscription request

@decodedMessage: the decoded dictionary that contains the subscribe command, the hashtag that the user wants to subscribe to, and the user's username
"""
def HandleSubscription(decodedMessage):
    # extract the username and hashtag from the message
    user = decodedMessage['username']
    hashtag = decodedMessage['hashtag']
    print('A subscription request has been sent by: ' + str(user))
    # check if the user is already subscribed to 3 hashtags or if they are
    # already subscribed to the hashtag they are trying to subscribe to if
    # they are not then add the hashtag if they are don't add the hashtag and
    #  inform the user or the specific error they have encountered
    if len(activeUserSubs[user]) == 3:
        response = {'validation': 'too_many_sub','command':'subscribe', 'hashtag': hashtag}
        print(str(user) + ' is subscribed to too many hashtags')
        userToSocket[user].sendall(pickle.dumps(response))
    elif hashtag in activeUserSubs[user]:
        response = {'validation': 'already_subbed', 'command':'subscribe', 'hashtag': hashtag}
        print(str(user) + ' is already subscribed to: ' + str(hashtag))
        userToSocket[user].sendall(pickle.dumps(response))
    else:
        response = {'validation': 'subscribed', 'command':'subscribe', 'hashtag': hashtag}
        activeUserSubs[user].append(hashtag)
        print(str(user) + ' has successfully subscribed to: ' + str(hashtag))
        userToSocket[user].sendall(pickle.dumps(response))

""" 
@HandleUnsubscribe: helper method for server to help handle an unsubscribe request

@decodedMessage: the decoded dictionary that contains the unsubscribe command, the hashtag that the user wants to unsubscibe from, and the user's username
"""
def HandleUnsubscribe(decodedMessage):
    # extract the username and the hashtag from the message that was passed in
    user = decodedMessage['username']
    hashtag = decodedMessage['hashtag']
    print('Unsubscribe request recieved from: ' + str(user))
    # check if the user is subbed to the hashtag or if the user is subbed to
    # anything at all then unsub if you can
    if hashtag not in activeUserSubs[user]:
        response = {'validation': 'sub_does_not_exist', 'command':'unsubscribe', 'hashtag': hashtag}
        print(str(user) + ' was not unsubscribed from: ' + str(hashtag) + ' because that subscription does not exist')
        userToSocket[user].sendall(pickle.dumps(response))
    elif len(activeUserSubs[user]) == 0:
        response = {'validation': 'not_subbed_to_anything', 'command':'unsubscribe', 'hashtag': hashtag}
        print(str(user) + ' was not unsubscribed from: ' + str(hashtag) + ' because there are no subscriptions')
        userToSocket[user].sendall(pickle.dumps(response))
    else:
        response = {'validation': 'unsubscribed', 'command':'unsubscribe', 'hashtag': hashtag}
        activeUserSubs[user].remove(hashtag)
        print(str(user) + ' has successfully unsubscribed from: ' + str(hashtag))
        userToSocket[user].sendall(pickle.dumps(response))

""" 
@HandleExit: helper method for server to help handle an exit request

@decodedMessage: the decoded dictionary that contains the exit command and the user's username
"""
def HandleExit(decodedMesssage):
    # extracted the username from the message
    user = decodedMesssage['username']
    # grab the user's socket and close connection
    print('An exit request has been sent by: ' + str(user))
    userToSocket[user].close()
    # delete the user and their socket from the userToSocket dict
    del userToSocket[user]
    # delete the user and their subscriptions from the activeUsersSub dict
    del activeUserSubs[user]
    # remove the user from the activeUsers list
    activeUsers.remove(user)
    print(str(user) + ' has left the server')
    # return from here to close the thread
    return

"""  
@OnNewClient: this method is invoked whenever a new client comes online, this mehtod validates that the user that is trying to log on isn't already logged on, then it begins to handle the commands that the user/client is sending to the server

@clientSocket: the client's socket
@addr: the client's IP address
"""
def OnNewClient(clientSocket, addr):
    while True:
        # recieve an encoded message from the client
        encodedMessage = clientSocket.recv(BUFFER_SIZE)
        # decode the encoded message from the client
        decodedMessage = pickle.loads(encodedMessage)

        if decodedMessage['command'] == 'check_username':
            # validate whether the user user is already on the server or not
            if decodedMessage['username'] not in activeUsers and len(activeUsers) < 5:
                response = {'unique': True}
                # add the username to the list of active users
                activeUsers.append(decodedMessage['username'])
                # add the username and socket to the dictionary of active
                # users and sockets
                usernameSocket = {decodedMessage['username']: clientSocket}
                userToSocket.update(usernameSocket)
                newUser = {decodedMessage['username']: []}
                # add the user and an empty list to the dictionary of active users and subs
                activeUserSubs.update(newUser)
                # encode the response dictionary and send the encoded dictionary to tbe client
                encodedMessage = pickle.dumps(response)
                clientSocket.sendall(encodedMessage)
                print(decodedMessage['username'] + ' has entered the server')
            else:
                response = {'unique': False}
                clientSocket.sendall(pickle.dumps(response))
                return
        if decodedMessage['command'] == 'tweet':
            HandleTweet(decodedMessage, clientSocket)
        if decodedMessage['command'] == 'subscribe':
            HandleSubscription(decodedMessage)
        if decodedMessage['command'] == 'unsubscribe':
            HandleUnsubscribe(decodedMessage)
        if decodedMessage['command'] == 'exit':
            HandleExit(decodedMessage)
            return
    clientSocket.close()

"""  
@main: this is the main method for the server, this method initialize the server with it's address and the port number that it will be using to listen for clients

@argv: this is the command that was used to invoke the server from the terminal
"""
def main(argv):
    # check that the server initialized properly if not throw error message
    # and exit gracefully
    if len(argv) != 2:
        print('The command that has been entered is incorrect. Please use the '
              'following command: ')
        print('python ./ttweetsv.py <ServerPort>')
        exit(0)

    # get the host computer's IP address
    serverIP = socket.gethostbyname(socket.gethostname())
    # get the port the server will be listening for
    portNumber = int(argv[1])
    """ # set the max Buffer Size
    BUFFER_SIZE = sys.maxint """
    # create a bare TCP server that is not tied to ip or port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this will allow us to reuse the same port for the server if the server
    # crashes
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the server to the host's IP and the selected port number
    s.bind((serverIP, portNumber))
    # the server will begin listening
    s.listen(5)
    print('Server: ' + str(serverIP) + ' is listening on Port: ' + str(
        portNumber))
    while True:
        # accept a new client
        conn, addr = s.accept()    
        # this instantiates a new thread whenever a new user logs on
        thread.start_new_thread(OnNewClient, (conn, addr))
    s.close()


if __name__ == "__main__":
    main(sys.argv[:])