from __future__ import division
import pickle
import socket
import sys

MAX_QUEUE_SIZE = 1
BUFFER_SIZE = 161

message = 'EMPTY MESSAGE'

"""
this method is to deliver an error message for the server.
"""
def err_msg():
    print('ERROR: The command to run the serve seems to be incorrect please use the following format: ')
    print('./ttweetsv.py <ServerPort>')

"""
@main: in this method the command that was passed through the terminal will be parsed and the server will
       instantiated
@param:
       argv: the command that was passed through the terminal
"""
def main(argv):
    # the global message variable allows the 
    global  message
    # checks if they command that was passed through was valid if not then throw an error
    if len(argv) != 2:
        print(argv)
        err_msg()
        exit(0)
    # get the ip address of the host
    server_ip = socket.gethostbyname(socket.gethostname())
    # get the port number of argv
    port_number = int(argv[1])

    # create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind the socket to the port number that was passed in
    sock.bind((server_ip, port_number))
    activeUsers = []
    while True:
        # listen for a connection on the port
        sock.listen(MAX_QUEUE_SIZE)
        print('Server: '+ str(server_ip) + ' is listening on Port: '+ str(port_number))
        # accept a client connection
        client_socket, client_address = sock.accept()
        print('Client has connected to Server')
        try:
            while True:
                # recieve a back of size = BUFFER_SIZE
                msg = client_socket.recv(BUFFER_SIZE)
                message_decoded = pickle.loads(msg)
                # split the client request into the token and the message
                client_request = message_decoded.split("`")
                # get the token to determine the client request type
                token = client_request[0]
                # get the message from the client
                client_message = client_request[1]
                # if the token is an upload token then preform upload operations
                if token == 'upload_request':
                    # set the message on the server to the message sent from the client
                    message = client_message
                    # send a decoded confirmation messsage to the client
                    client_socket.sendall(pickle.dumps('Message Uploaded'))
                    # end the operation
                    break
                # if the take is a download tocken then send the message that is on the most recent message for this session
                if token == 'download_request':
                    client_socket.sendall(pickle.dumps(message))
                    break
        # closes the client socket
        finally:
            client_socket.close()

if __name__ == "__main__":
    main(sys.argv[:])

sys.exit(0)