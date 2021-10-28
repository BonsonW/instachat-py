# external
from threading import Thread
from time import sleep
from socket import *
import time
import os
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
                print("===== connection ended with: " + self.user)
            elif method == MSSG:
                print(self.user + ": " + params)

        peerThreads.remove(self)

#endregion

#region client processes

def login(sock, user, listeningPort):
    # check username
    sock.sendall(' '.join([HELO, user, str(listeningPort)]).encode())
    data = sock.recv(1024)
    status, response = data.decode().split(' ', 1)
    print("==== " + response)
    status = ERROR

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
        print("==== private connection started with " + recipientName)
    else:
        print("==== " + response)

def end_private(recipientName):
    thread = get_peer_thread(recipientName)
    if thread is not None:
        thread.socket.sendall(' '.join([QUIT, "None"]).encode())
        print("==== connection ended with " + recipientName)
    else:
        print("==== invalid user")
        
def send_private(recipientName, message):
    sock = get_peer_socket(recipientName)
    if sock is not None:
        sock.sendall(' '.join([MSSG, message]).encode())
    else:
        print("==== invalid user")

def get_peer_socket(user):
    for peerThread in peerThreads:
        if peerThread.user == user:
            return peerThread.socket
    return None

def get_peer_thread(user):
    for peerThread in peerThreads:
        if peerThread.user == user:
            return peerThread
    return None

def deny_request(sock, user):
    sock.sendall(' '.join([DENY, user]).encode())

def block(sock, senderName, recipientName):
    sock.sendall(' '.join([BLCK, senderName, recipientName]).encode())

def unblock(sock, senderName, recipientName):
    sock.sendall(' '.join([NBLK, senderName, recipientName]).encode())

#endregion


#region establish connection

# Server would be running on the same host as Client
if len(sys.argv) != 2:
    print("\n===== error usage, python3 client.py SERVER_PORT\n")
    exit(0)

serverPort = int(sys.argv[1])

# define a socket for the client side, it would be used to communicate with the server
clientSocket = new_connection(("127.0.0.1", serverPort))

welcomeSocket = socket(AF_INET, SOCK_STREAM)
welcomeSocket.bind(("127.0.0.1", 0))

login(clientSocket, name, welcomeSocket.getsockname()[1])

#endregion

#region update loop

commands = []
waiting = False

def update_loop():
    global waiting

    while True:

        sleep(1)
        if waiting:
            continue

        # execute commands
        if commands:
            command = commands.pop()
            
            # execute methods
            if command == "logout":
                end_connection(clientSocket, name)
                for thread in peerThreads:
                    thread.socket.sendall(' '.join([QUIT, name]).encode())
            elif command == "y":
                commands.pop(1)
                print("==== you have accepted")
            elif command == "n":
                commands.pop(0)
                print("==== you have denied")
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
                    elif command == "stopprivate":
                        end_private(params)
                        continue
                    elif command == "deny":
                        deny_request(clientSocket, params)
                    elif command == "block":
                        block(clientSocket, name, params)
                    elif command == "unblock":
                        unblock(clientSocket, name, params)
                    else:
                        print("==== invalid command")
                        continue
                except:
                    print("==== invalid command")
                    continue
        else:
            get_messages(clientSocket, name)
        
        # recieve responses from server
        data = clientSocket.recv(1024)
        try:
            status, body = data.decode().split(' ', 1)
        except:
            continue

        # handle response given by server
        if status == CONFIRMATION:
            body, accept, deny = body.split(" |", 2)
            commands.append(accept)
            commands.append(deny)
            waiting = True

        if body != "None":
            print("==== " + body)
        
        if (status == CONNECTION_END):
            os._exit(0)


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
    waiting = False
    commands.append(clientInput)