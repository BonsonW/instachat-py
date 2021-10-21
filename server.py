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
from tests.message_test import recipientName, senderName

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
        self.timeout = 0

        self.alive = True
        
    def run(self):
        response = []
        while self.alive:

            data = self.clientSocket.recv(1024)
            

            try:
                method, params = data.decode().split(' ', 1)
            except:
                continue
            if self.timeout > 0:
                response = ' '.join([ERROR, "you are currently timed out"])
                self.timeout -= 1
                sleep(1)
            elif self.authorised:
                if method == QUIT:
                    response = self.logout(params)
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
                    response = self.req_address(params)
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

            self.clientSocket.send(' '.join(response).encode())

#region request method processes

    def logout(self, user):
        self.alive = False
        data.set_offline(user, self)
        return [CONNECTION_END, "ending connection, goodbye"]

    def welcome(self, user, listeningPort):
        self.listeningPort = listeningPort
        if not data.user_exists(user):
            return [ERROR, "hello", user, "please enter a password for your new account"]
        if user == data.ALL_USERS:
            return [ERROR, "invalid username entered"]
        return [ACTION_COMPLETE, "welcome", user, "please enter your password"]
               
    def login(self, user, pswd):
        self.user = user
        if self.authorised:
            return [ACTION_COMPLETE, "you are already logged into account", user]
            
        # create new acc
        if not data.user_exists(user):
            auth.add_cred(user, pswd)
            data.add_user(user, pswd)
            data.set_online(user, self)
            message.send(user, data.ALL_USERS, "logged on")
            self.authorised = True
            return [ACTION_COMPLETE, "welcome", user, "you are logged into your new account"]

        # or check password
        # timeout after 3 failed attempts
        self.authorised = data.password_match(user, pswd)
        if self.authorised:
            data.set_online(user, self)
            message.send(user, data.ALL_USERS, "logged on")
            return [ACTION_COMPLETE, "welcome", user, "you are successfully logged in"]
        else:
            self.attempts += 1
            if self.attempts >= 3:
                self.attempts = 0
                self.timeout = blockDuration
                return [ERROR, "incorrect password, you will be timed out", "seconds"]
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
            return [ACTION_COMPLETE, "no other useres are online right now"]

    def req_address(self, user):
        if not data.user_exists(user):
            return [ERROR, "invalid user"]
        addr = data.get_address(user)
        if addr is None:
            return [ERROR, "user not currently online"]

        peerThread = data.get_clientThread(user)
        peerSock = peerThread.clientSocket
        
        # if not queued up as peer, send request to recipient
        # otherwise start connection
        if user not in self.peerRequests:
            peerSock.send(' '.join([CONFIRMATION, "would you like to start a private connection with", self.user, "? (y/n)", "|startprivate", self.user, "|deny", self.user]).encode())
            if self.user not in peerThread.peerRequests:
                peerThread.peerRequests.append(self.user)
            return [ERROR, "private connection has been requested"]
        peerSock.send(' '.join([ACTION_COMPLETE, "private connection started with", self.user]).encode())
        return [ACTION_COMPLETE, addr[0], str(addr[1])]

    def deny_request(self, user):
        if user in self.peerRequests:
            self.peerRequests.remove(user)
            message.send("server", user, ' '.join([self.user, "has denied your request"]))
            return [ACTION_COMPLETE, "None"]
        return [ERROR, "invalid user"]
#endregion

#endregion

#region welcome process

# acquire server host and port from command line parameter
# if len(sys.argv) != 2:
#     print("\n===== Error usage, python3 TCPServer3.py SERVER_PORT ======\n");
#     exit(0);
serverHost = "127.0.0.1"
serverPort =  8080 # int(sys.argv[1])
serverAddress = (serverHost, serverPort)

blockDuration = 10

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

while True:
    serverSocket.listen()
    clientSocket, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSocket)
    clientThread.start()
    
#endregion