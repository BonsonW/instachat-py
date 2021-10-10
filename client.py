# external
from threading import Thread
from time import sleep
from socket import *
import sys

# internal
from src.request_methods import *
from src.status_codes import *

name = input("name: ")

#region client methods

def login(clientSocket):
    # check username
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

def get_messages(clientSocket, name):
    clientSocket.sendall(' '.join([GETM, name]).encode())

def send_message(clientSocket, senderName, recipientName, message):
    clientSocket.sendall(' '.join([MSSG, senderName, recipientName, message]).encode())

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


#region update loop

commands = []

def update():
    while True:
        sleep(1)
        if commands:
            command = commands.pop()
            
            # execute methods
            if command == "logout":
                logout(clientSocket)
            else:
                print("==== invalid command")
                continue
        else:
            get_messages(clientSocket, name)
        
        # recieve response
        data = clientSocket.recv(1024)
        status, response = data.decode().split(' ', 1)

        # print response given by server
        if response != "None":
            print(response)

        if (status == CONNECTION_END):
            break

#end region

t = Thread(target=update)
t.start()

while True:
    command = input()
    commands.append(command)
    if command == "logout":
        break

# close the socket
clientSocket.close()

