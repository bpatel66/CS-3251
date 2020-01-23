import pickle
import socket
import sys

BUFFER_SIZE = 150
"""
This method is to display an error message on the terminal
the message will also provide the suggestted fixes for the client side request
"""
def err_msg():
    print('ERROR: It seems the inputted command does not fit the correct format please refer the the messaages below as to how to structure the command.')
    print('')
    print('How to upload message to server: ./ttweetcl.py <ServerIP> <ServerPort> \"message\" input the message with quotes and there is a character limit of 150 also if you don\'t want to send any message include open and closed quotes ')
    print('')
    print(' How to download message from server: ./ttweetcl.py <ServerIP> <ServerPort>')
"""
@main: this method handle the main functionality of the client
@param:
       argv: is the command that was passed in through the terminal
"""
def main(argv):
    # if the inputted command does not have the appropriate number of arguements an error message will be displayed explaining how to use the command
    if len(argv) < 4 or len(argv) > 5:
        print(argv)
        err_msg()
        exit(0)
    
    # the operation -u or -d is parsed from argv
    # if the operation specified is illegal an error will be displayed and the program will exit
    operation = argv[1]
    if operation == '-u':
        operation = 0
    elif operation == '-d':
        operation = 1
    else:
        err_msg()
        exit(0)
    
    # the ServerIP is parsed from argv
    server_ip = argv[2]
    # the ServerPort is parsed from argv
    server_port = int(argv[3])

    # checks that the character limited isn't exceeded
    # if it does exceed the character count, so an error message and terminate the client
    if operation == 0:
        inputted_message = argv[4]
        if len(inputted_message) > 150:
            print('')
            print('ERROR: The character limit for the message is 150')
            exit(0)
    # Now to set up the TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # attempting connect with the server and the port
    sock.connect((server_ip, server_port))
    print("Attempting to connect to server")
    # check to see if the operation is specified an upload
    if operation == 0:
        upload_request_token = 'upload_request`'
        # the message to be sent to the server is established
        # this is where the upload token is added to the front of message to be uploaded
        message = 'Empty Message'
        inputted_message = argv[4]
        if inputted_message == '':
            message = upload_request_token + message
        else:
            message = inputted_message
            message = upload_request_token + message
        print('Sending message to Server: ' + str(server_ip) + ' with Port Number: ' + str(server_port))
        # encode the message with pickle
        message_data = pickle.dumps(message)
        # send the encodeded message data to the server
        sock.sendall(message_data)
        # get the confirmation from the server that the message was recieved
        response = sock.recv(BUFFER_SIZE)
        print(pickle.loads(response))
        # close the connection
        sock.close()
    # if the specified operation is download
    if operation == 1:
        print('Downloading message from Server: ' + str(server_ip) + ' with Port Number: ' + str(server_port))
        # send the downlaod token to the server
        message = 'download_request`'
        sock.sendall(pickle.dumps(message))
        # recieve encoded messsage from server
        response = sock.recv(BUFFER_SIZE)
        # decode the encoded message from the server
        server_response = pickle.loads(response)
        # display the decoded message from the server
        print('The message from the Server: ' + str(server_response))
        # close the socket 
        sock.close()

if __name__ == "__main__":
    main(sys.argv)

sys.exit(0)