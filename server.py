# external
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

            if method == QUIT:
                response = self.logout(params)
            elif method == HELO:
                response = self.welcome(params)
            elif method == LOGN:
                name, pswd = params.split(' ', 1)
                response = self.login(name, pswd)
            elif method == GETM:
                response = self.get_messages(params)
            elif method == MSSG:
                senderName, recipientName, messageBody = params.split(' ', 2)
                response = self.send_message(senderName, recipientName, messageBody)
            elif method == BLCK:
                name, other = params.split(' ', 1)
                response = self.block(name, other)
            elif method == ELSE:
                name, timeStamp = params.split(' ', 1)
                response = self.who_else(name, float(timeStamp))
            else:
                response = [INVALID_METHOD, "the method you have requested is not available"]

            self.clientSocket.send(' '.join(response).encode())

#region request method processes

    def logout(self, name):
        self.alive = False
        data.set_offline(name)
        return [CONNECTION_END, "ending connection, goodbye"]

    def welcome(self, name):
        if not data.user_exists(name):
            return [NONE_FOUND, "hello", name, "please enter a password for your new account"]
        if name == data.ALL_USERS:
            return [INVALID_PARAMS, "invalid username entered"]
        return [ACTION_COMPLETE, "welcome", name, "please enter your password"]
        
        
    def login(self, name, pswd):
        if self.authorised:
            return [ACTION_COMPLETE, "you are already logged into account", name]
            
        # create new acc
        if not data.user_exists(name):
            auth.add_cred(name, pswd)
            data.add_user(name, pswd)
            data.set_online(name)
            self.authorised = True
            return [ACTION_COMPLETE, "welcome", name, "you are logged into your new account"]

        # or check password
        self.authorised = data.password_match(name, pswd)
        if self.authorised:
            data.set_online(name)
            return [ACTION_COMPLETE, "welcome", name, "you are successfully logged in"]
        else:
            return [INVALID_PARAMS, "incorrect password provided for", name]
    
    def get_messages(self, name):
        messages = message.get_messages(name)
        if messages:
            return [ACTION_COMPLETE, '\n'.join(messages)]
        else:
            return [NONE_FOUND, "None"]

    def send_message(self, senderName, recipientName, messageBody):
        if not data.user_exists(recipientName):
            return [NONE_FOUND, "invalid user"]
        message.send(senderName, recipientName, messageBody)
        return [ACTION_COMPLETE, "None"]

    def block(self, name, other):
        if not data.user_exists(name):
            return [NONE_FOUND, "invalid user"]
        user = data.get_user(name)
        if not user.blocks(other):
            user.block(other)
            return [ACTION_COMPLETE, other, "is now blocked"]
        else:
            user.unblock(other)
            return [ACTION_COMPLETE, other, "is now blocked"]

    def who_else(self, name, timeStamp):
        res = data.get_online_since(timeStamp)
        res.remove(name)
        if res:
            return [ACTION_COMPLETE, '\n'.join([res])]
        else:
            return [NONE_FOUND, "None"]

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