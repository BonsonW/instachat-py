# external
from os import times
from socket import *
from threading import Thread
import sys, select
from time import strptime

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
        self.user = None
        
        print("===== new connection created for: ", clientAddress)
        self.alive = True
        
    def run(self):
        response = []
        while self.alive:
            data = self.clientSocket.recv(1024)

            try:
                method, params = data.decode().split(' ', 1)
            except:
                continue
                
            if self.authorised:
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
                elif method == ELSE:
                    user, timeStamp = params.split(' ', 1)
                    if (timeStamp == "None"):
                        response = self.who_else_now(user)
                    else:
                        response = self.who_else_since(user, float(timeStamp))
                else:
                    response = [INVALID_METHOD, "the method you have requested is not available"]
            else:
                if method == QUIT:
                    self.alive = False
                    response = [CONNECTION_END, "ending connection, goodbye"]
                elif method == HELO:
                    response = self.welcome(params)
                elif method == LOGN:
                    user, pswd = params.split(' ', 1)
                    response = self.login(user, pswd)
                else:
                    response = [INVALID_METHOD, "the method you have requested is not available"]

            self.clientSocket.send(' '.join(response).encode())

#region request method processes

    def logout(self, user):
        self.alive = False
        data.set_offline(user)
        return [CONNECTION_END, "ending connection, goodbye"]

    def welcome(self, user):
        if not data.user_exists(user):
            return [NONE_FOUND, "hello", user, "please enter a password for your new account"]
        if user == data.ALL_USERS:
            return [INVALID_PARAMS, "invalid username entered"]
        return [ACTION_COMPLETE, "welcome", user, "please enter your password"]
        
        
    def login(self, user, pswd):
        self.user = user
        if self.authorised:
            return [ACTION_COMPLETE, "you are already logged into account", user]
            
        # create new acc
        if not data.user_exists(user):
            auth.add_cred(user, pswd)
            data.add_user(user, pswd)
            data.set_online(user)
            self.authorised = True
            return [ACTION_COMPLETE, "welcome", user, "you are logged into your new account"]

        # or check password
        self.authorised = data.password_match(user, pswd)
        if self.authorised:
            data.set_online(user)
            return [ACTION_COMPLETE, "welcome", user, "you are successfully logged in"]
        else:
            return [INVALID_PARAMS, "incorrect password provided for", user]
    
    def get_messages(self, user):
        messages = message.get_messages(user)
        if messages:
            return [ACTION_COMPLETE, '\n'.join(messages)]
        else:
            return [NONE_FOUND, "None"]

    def send_message(self, senderName, recipientName, messageBody):
        if not data.user_exists(recipientName):
            return [NONE_FOUND, "invalid user"]
        message.send(senderName, recipientName, messageBody)
        return [ACTION_COMPLETE, "None"]

    def block(self, user, other):
        if not data.user_exists(user):
            return [NONE_FOUND, "invalid user"]
        user = data.get_user(user)
        if not user.blocks(other):
            user.block(other)
            return [ACTION_COMPLETE, other, "is now blocked"]
        else:
            user.unblock(other)
            return [ACTION_COMPLETE, other, "is now blocked"]

    def who_else_since(self, user, timeStamp):
        onlineSince = data.get_online_since(timeStamp)
        if user in onlineSince:
            onlineSince.remove(user)
        if onlineSince:
            return [ACTION_COMPLETE, "previously logged on:\n", '\n'.join(onlineSince)]
        else:
            return [ACTION_COMPLETE, "no users were logged in since this time"]

    def who_else_now(self, user):
        onlineNow = data.get_online_now()
        onlineNow.remove(user)
        if onlineNow:
            return [ACTION_COMPLETE, " online now:\n", '\n'.join(onlineNow)]
        else:
            return [ACTION_COMPLETE, "no other useres are online right now"]

    def req_address(self, user):
        if not data.user_exists(user):
            return [NONE_FOUND, "invalid user"]
        addr = data.get_address(user)
        if addr is None:
            return [NONE_FOUND, "user not currently online"]
        # send confimration to addr before sending address
        return [ACTION_COMPLETE, addr[0], str(addr[1])]

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

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

print("\n===== server is running")
print("===== waiting for connection request from clients...")

while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    clientThread.start()
    
#endregion