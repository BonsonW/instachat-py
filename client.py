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

peerThreads = []
peerActivity = []
commands = []
waiting = False
timeoutSeconds = 0

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
                peerActivity.append({"peer": self.user, "idleTime": 0})
            elif method == QUIT:
                self.alive = False
                self.socket.sendall(' '.join([QUIT, "None"]).encode())
                print("===== connection has ended with " + self.user)
            elif method == MSSG:
                reset_peer_activity(self.user)
                print(self.user + ": " + params)

        peerThreads.remove(self)

#endregion

#region client processes

def login(sock, user, listeningPort):
    global timeoutSeconds
    
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
        status, timeoutSecondsStr, response = data.decode().split(' ', 2)
        timeoutSeconds = int(timeoutSecondsStr)
        print("==== " + response)

def disconnect(sock, user):
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
    peerThread = get_peer_thread(recipientName)
    if peerThread is not None:
        peerThread.socket.sendall(' '.join([QUIT, "None"]).encode())
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

name = input("name: ")

login(clientSocket, name, welcomeSocket.getsockname()[1])

#endregion

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
                disconnect(clientSocket, name)
                for peerThread in peerThreads:
                    disconnect(peerThread.socket, name)
            elif command == "getmessages":
                get_messages(clientSocket, name)
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

def disconnect_idle_peers():
    global timeoutSeconds
    while True:
        sleep(1)
        for i in range(len(peerActivity)-1, -1, -1):
            p = peerActivity[i]
            peerActivity[i]["idleTime"] += 1
            if p["idleTime"] > timeoutSeconds:
                peerThread = get_peer_thread(p["peer"])
                if peerThread is not None:
                    disconnect(peerThread.socket, name)
                    print("===== connection ending with " + peerThread.user + " due to inactivity")
                peerActivity.pop(i)

def reset_peer_activity(peer):
    for u in peerActivity:
        if u["peer"] == peer:
            u["idleTime"] = 0

updateThread = Thread(target=update_loop)
updateThread.start()

timeoutThread = Thread(target=disconnect_idle_peers)
timeoutThread.start()

welcomeThread = Thread(target=listen)
welcomeThread.start()

while True:
    clientInput = input()
    waiting = False
    commands.append(clientInput)