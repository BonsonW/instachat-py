# external
from threading import Thread
from time import sleep
from socket import *
import time
import sys

# internal
from src.request_methods import *
from src.status_codes import *
from src.data import ALL_USERS

name = input("name: ")

peerThreads = []

#region p2p

class PeerThread(Thread):
    def __init__(self, socket, user):
        Thread.__init__(self)
        self.socket = socket
        self.user = user
        
        self.alive = True
        
    def run(self):
        while self.alive:
            sleep(1)

            data = self.socket.recv(1024)
            try:
                method, params = data.decode().split(' ', 1)
            except:
                continue
            
            if method == HELO:
                self.user = params
            elif method == QUIT:
                self.alive = False
            elif method == MSSG:
                print(self.user + ": " + params)

        peerThreads.remove(self)

#endregion

#region client methods

def login(sock, user, listeningPort):
    # check username
    sock.sendall(' '.join([HELO, user, str(listeningPort)]).encode())
    data = sock.recv(1024)
    status, response = data.decode().split(' ', 1)
    print("==== " + response)
    status = INVALID_PARAMS

    # enter password
    while status != ACTION_COMPLETE:
        pswd = input("password: ")
        sock.sendall(' '.join([LOGN, user, pswd]).encode())

        data = sock.recv(1024)
        status, response = data.decode().split(' ', 1)
        print("==== " + response)

def end_connection(sock, user):
    sock.sendall(' '.join([QUIT, user]).encode())

def get_messages(sock, user):
    sock.sendall(' '.join([GETM, user]).encode())

def send_message(sock, senderName, recipientName, message):
    sock.sendall(' '.join([MSSG, senderName, recipientName, message]).encode())

def who_else(sock, user, time):
    sock.sendall(' '.join([ELSE, user, str(time)]).encode())

def new_connection(address):
    newSocket = socket(AF_INET, SOCK_STREAM)
    newSocket.connect(address)
    return newSocket

def start_private(sock, senderName, recipientName):
    # request address
    sock.sendall(' '.join([ADDR, recipientName]).encode())
    data = sock.recv(1024)
    status, response = data.decode().split(' ', 1)

    # set up new private connection
    if status == ACTION_COMPLETE:
        ip, port = response.split(' ', 1)
        peerSocket = new_connection((ip, int(port)))
        peerSocket.sendall(' '.join([HELO, senderName]).encode())
        peerThread = PeerThread(peerSocket, recipientName)
        peerThreads.append(peerThread)
        peerThread.start()
        print("==== new private connection started with " + recipientName)
    else:
        print("==== " + response)

def send_private(recipientName, message):
    sock = get_peer_socket(recipientName)
    if sock is not None:
        sock.sendall(' '.join([MSSG, message]).encode())
    else:
        print("==== no such user")

def get_peer_socket(user):
    for peerThread in peerThreads:
        if peerThread.user == user:
            return peerThread.socket
    return None

#endregion


#region establish connection

# Server would be running on the same host as Client
# if len(sys.argv) != 3:
#     print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT ======\n");
#     exit(0);
serverHost = "127.0.0.1"
serverPort = 8080
serverAddress = (serverHost, serverPort)

welcomeSocket = socket(AF_INET, SOCK_STREAM)
welcomeSocket.bind(('127.0.0.1', 0))

# define a socket for the client side, it would be used to communicate with the server
clientSocket = new_connection(serverAddress)

login(clientSocket, name, welcomeSocket.getsockname()[1])

#endregion

#region update loop

commands = []

def update_loop():
    wait = False

    while True:

        sleep(1)

        # execute commands
        if commands:
            command = commands.pop()
            wait = False
            
            # execute methods
            if command == "logout":
                end_connection(clientSocket, name)
                # end connection with all peers
            elif command == "y" or command == "n":
                clientSocket.sendall(' '.join([ACTION_COMPLETE, command]).encode())
            elif command == "whoelse":
                who_else(clientSocket, name, "None")
            else:
                try:
                    command, params = command.split(' ', 1)
                    if command == "message":
                        recipientName, messageBody = params.split(' ', 1)
                        send_message(clientSocket, name, recipientName, messageBody)
                    elif command == "broadcast":
                        send_message(clientSocket, name, ALL_USERS, params)
                    elif command == "whoelsesince":
                        offset = float(params)
                        who_else(clientSocket, name, time.time()-offset)
                    elif command == "startprivate":
                        start_private(clientSocket, name, params)
                        continue
                    elif command == "private":
                        recipientName, messageBody = params.split(' ', 1)
                        send_private(recipientName, messageBody)
                        continue
                    else:
                        print("==== invalid command")
                        continue
                except:
                    print("==== invalid command")
                    continue
        elif not wait:
            get_messages(clientSocket, name)
        
        # recieve responses from server
        data = clientSocket.recv(1024)
        try:
            status, body = data.decode().split(' ', 1)
        except:
            continue

        # print response given by server
        if status == CLIENT_QUESTION:
            wait = True
        if body != "None":
            print("==== " + body)
        
        if (status == CONNECTION_END):
            clientSocket.close()
            break


def listen():
    # listen for new peer connection
    while True:
        welcomeSocket.listen()
        peerSocket, peerAddress = welcomeSocket.accept()
        peerThread = PeerThread(peerSocket, peerAddress)
        peerThreads.append(peerThread)
        peerThread.start()

#end region

updateThread = Thread(target=update_loop)
updateThread.start()

welcomeThread = Thread(target=listen)
welcomeThread.start()

while True:
    clientInput = input()
    commands.append(clientInput)
    if clientInput == "logout":
        break