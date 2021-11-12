# external
from os import times
from socket import *
from threading import Thread
import sys, select
from time import sleep, strptime, time

# internal
from src import auth, data, message
from src.request_methods import *
from src.status_codes import *

userActivity = []
usersBlocked = []

#region client thread

class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.authorised = False
        self.listeningPort = None
        self.user = None
        self.peerRequests = []
        self.attempts = 0

        self.alive = True
        
    def run(self):
        response = []
        while self.alive:

            data = self.clientSocket.recv(1024)

            try:
                method, params = data.decode().split(' ', 1)
            except:
                continue
            
            if method != GETM:
                reset_user_activity(self.user)

            if self.authorised:
                if method == QUIT:
                    response = self.logout()
                elif method == GETM:
                    response = self.get_messages(params)
                elif method == MSSG:
                    senderName, recipientName, messageBody = params.split(' ', 2)
                    response = self.send_message(senderName, recipientName, messageBody)
                elif method == BLCK:
                    user, other = params.split(' ', 1)
                    response = self.block(user, other)
                elif method == NBLK:
                    user, other = params.split(' ', 1)
                    response = self.unblock(user, other)
                elif method == ADDR:
                    response = self.req_address(self.user, params)
                elif method == ELSE:
                    user, timeStamp = params.split(' ', 1)
                    if (timeStamp == "None"):
                        response = self.who_else_now(user)
                    else:
                        response = self.who_else_since(user, float(timeStamp))
                elif method == DENY:
                    response = self.deny_request(params)
                else:
                    response = [ERROR, "the method you have requested is not available"]
            else:
                if method == QUIT:
                    self.alive = False
                    response = [CONNECTION_END, "ending connection, goodbye"]
                elif method == HELO:
                    user, listeningPort = params.split(' ', 1)
                    response = self.welcome(user, int(listeningPort))
                elif method == LOGN:
                    user, pswd = params.split(' ', 1)
                    response = self.login(user, pswd)
                else:
                    response = [ERROR, "the method you have requested is not available"]

            self.clientSocket.sendall(' '.join(response).encode())

#region client thread processes

    def logout(self):
        self.alive = False
        message.send(self.user, data.ALL_USERS, "logged off")
        data.set_offline(self.user, self)
        return [CONNECTION_END, "ending connection, goodbye"]

    def welcome(self, user, listeningPort):
        self.listeningPort = listeningPort
        if not data.user_exists(user):
            return [ACTION_COMPLETE, "hello", user, "please enter a password for your new account"]
        if user == data.ALL_USERS:
            return [ERROR, "invalid username entered"]
        return [ACTION_COMPLETE, "welcome", user, "please enter your password"]
               
    def login(self, user, pswd):
        self.user = user
        
        if is_blocked(user):
            return [ERROR, "timed out for too many password attempts, try again later"]
        
        # create new acc
        if not data.user_exists(user):
            auth.add_cred(user, pswd)
            data.add_user(user, pswd)
            data.set_online(user, self)
            message.send(user, data.ALL_USERS, "logged on")
            self.authorised = True
            userActivity.append({"user": user, "idleTime": 0})
            return [ACTION_COMPLETE, str(timeoutSeconds), "welcome", user, "you are logged into your new account"]

        # or check password
        # timeout after 3 failed attempts
        self.authorised = data.password_match(user, pswd)
        if self.authorised:
            data.set_online(user, self)
            message.send(user, data.ALL_USERS, "logged on")
            userActivity.append({"user": user, "idleTime": 0})
            return [ACTION_COMPLETE, str(timeoutSeconds), "welcome", user, "you are successfully logged in"]
        else:
            self.attempts += 1
            if self.attempts >= 3:
                self.attempts = 0
                usersBlocked.append({"user": user, "blockTime": blockDuration})
                return [ERROR, "timed out for too many password attempts, try again later"]
            return [ERROR, "incorrect password provided for", user]
    
    def get_messages(self, user):
        messages = message.get_messages(user)
        if messages:
            return [ACTION_COMPLETE, '\n'.join(messages)]
        else:
            return [ERROR, "None"]

    def send_message(self, senderName, recipientName, messageBody):
        if not data.user_exists(recipientName):
            return [ERROR, "invalid user"]
        if message.send(senderName, recipientName, messageBody):
            return [ACTION_COMPLETE, "None"]
        elif recipientName == data.ALL_USERS:
            return [ACTION_COMPLETE, "not all users were able to recieve your message"]
        else:
            return [ERROR, "you've been blocked by", recipientName]

    def block(self, senderName, recipientName):
        if not data.user_exists(senderName) or senderName == recipientName:
            return [ERROR, "invalid user"]
        sender = data.get_user(senderName)
        sender.block(recipientName)
        return [ACTION_COMPLETE, recipientName, "is now blocked"]
    
    def unblock(self, senderName, recipientName):
        if not data.user_exists(senderName) or senderName == recipientName:
            return [ERROR, "invalid user"]
        sender = data.get_user(senderName)
        if sender.unblock(recipientName):
            return [ACTION_COMPLETE, recipientName, "is now unblocked"]
        return [ERROR, recipientName, "is already unblocked"]

    def who_else_since(self, user, timeStamp):
        onlineSince = data.get_online_since(timeStamp, user)
        if onlineSince:
            return [ACTION_COMPLETE, "previously logged on:\n", '\n'.join(onlineSince)]
        else:
            return [ACTION_COMPLETE, "no users were logged in since this time"]

    def who_else_now(self, user):
        onlineNow = data.get_online_now(user)
        if onlineNow:
            return [ACTION_COMPLETE, " online now:\n", '\n'.join(onlineNow)]
        else:
            return [ACTION_COMPLETE, "no other users are online right now"]

    def req_address(self, senderName, recipientName):
        if not data.user_exists(recipientName):
            return [ERROR, "invalid user"]
        if data.get_user(recipientName).blocks(senderName):
            return [ERROR, "invalid user"]
        addr = data.get_address(recipientName)
        if addr is None:
            return [ERROR, "user not currently online"]

        peerThread = data.get_clientThread(recipientName)
        peerSock = peerThread.clientSocket
        
        # if not queued up as peer, send request to recipient
        # otherwise start connection
        if recipientName not in self.peerRequests:
            peerSock.send(' '.join([CONFIRMATION, "would you like to start a private connection with", senderName, "? (y/n)", "|startprivate", senderName, "|deny", senderName]).encode())
            if senderName not in peerThread.peerRequests:
                peerThread.peerRequests.append(senderName)
            return [ERROR, "private connection has been requested"]
        peerSock.send(' '.join([ACTION_COMPLETE, "private connection started with", senderName]).encode())
        return [ACTION_COMPLETE, addr[0], str(addr[1])]

    def deny_request(self, user):
        if user in self.peerRequests:
            self.peerRequests.remove(user)
            message.send("server", user, ' '.join([self.user, "has denied your request"]))
            return [ACTION_COMPLETE, "None"]
        return [ERROR, "invalid user"]

#endregion

#endregion

#region server processes

def is_blocked(user):
    for u in usersBlocked:
        if u["user"] == user:
            return True
    return False

def unblock_users():
    while True:
        sleep(1)
        for i, u in enumerate(reversed(usersBlocked)):
            usersBlocked[i]["blockTime"] -= 1
            if u["blockTime"] < 0:
                del(usersBlocked[i])

def disconnect_idle_clients():
    while True:
        sleep(1)
        for i in range(len(userActivity)-1, -1, -1):
            u = userActivity[i]
            userActivity[i]["idleTime"] += 1
            if u["idleTime"] > timeoutSeconds:
                clientThread = data.get_clientThread(u["user"])
                if clientThread is not None:
                    clientThread.clientSocket.sendall(' '.join([CONNECTION_END, "you have been kicked for inactivity"]).encode())
                    clientThread.logout()
                userActivity.pop(i)


def reset_user_activity(user):
    for u in userActivity:
        if u["user"] == user:
            u["idleTime"] = 0
#endregion

#region server initialization

# acquire server host and port from command line parameter
if len(sys.argv) != 4:
    print("\n===== error usage, python3 server.py SERVER_PORT BLOCK_DURATION TIMEOUT\n")
    exit(0)

serverPort = int(sys.argv[1])
blockDuration = int(sys.argv[2])
timeoutSeconds = int(sys.argv[3])

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("127.0.0.1", serverPort))

# start thread for timing out inactive users
disconnectIdle = Thread(target=disconnect_idle_clients)
disconnectIdle.start()

# start thread for unblocking blocked users
disconnectIdle = Thread(target=unblock_users)
disconnectIdle.start()

# start welcome process
while True:
    serverSocket.listen()
    clientSocket, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSocket)
    clientThread.start()
    
#endregion

