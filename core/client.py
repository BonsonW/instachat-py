# external
from socket import *
import sys

# internal
from request_methods import *
from status_codes import *

#region client methods

def login(clientSocket):
    # enter username
    name = input("name: ")
    clientSocket.sendall(' '.join([HELO, name]).encode())
    data = clientSocket.recv(1024)
    status, response = data.decode().split(' ', 1)
    print(response)
    status = INVALID_PARAMS

    # enter password
    while status != ACTION_COMPLETE:
        pswd = input("password: ")
        clientSocket.sendall(' '.join([LOGN, name, pswd]).encode())

        data = clientSocket.recv(1024)
        status, response = data.decode().split(' ', 1)
        print(response)


def logout(clientSocket):
    clientSocket.sendall(' '.join([QUIT, "None"]).encode())
    data = clientSocket.recv(1024)
    status, response = data.decode().split(' ', 1)
    print(response)

#endregion


#region establish connection

# Server would be running on the same host as Client
# if len(sys.argv) != 3:
#     print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT ======\n");
#     exit(0);
serverHost = "127.0.0.1"
serverPort = 8080
serverAddress = (serverHost, serverPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_STREAM)

# build connection with the server and send message to it
clientSocket.connect(serverAddress)

login(clientSocket)

#endregion


#region client loop

while True:
    # send method
    message = input("===== please type any message you want to send to server:\n")
    
    if message == "logout":
        logout(clientSocket)
    # recieve response
    data = clientSocket.recv(1024)
    status, response = data.decode().split(' ', 1)

    # print response given by server
    print(response)
        
    ans = input('\nDo you want to continue(y/n) :')
    if ans == 'y':
        continue
    else:
        break

#end region

# close the socket
clientSocket.close()

