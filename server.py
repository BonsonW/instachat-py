# external
from socket import *
from threading import Thread
import sys, select

# internal
from src import auth, data, message
from src.request_methods import *
from src.status_codes import *

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
                self.alive = False
                response = [CONNECTION_END, "ending connection, goodbye"]
            elif method == HELO:
                response = self.welcome(params)
            elif method == LOGN:
                name, pswd = params.split(' ', 1)
                response = self.login(name, pswd)
            elif method == GETM:
                response = self.get_messages(params)
            elif method == MSSG:
                response = self.get_messages(params)
            else:
                response = [INVALID_METHOD, "the method you have requested is not available"]

            self.clientSocket.send(' '.join(response).encode())

#region request method processes

    def welcome(self, name):
        if not auth.user_exists(name):
            return [RESOURCE_NOT_FOUND, "hello", name, "please enter a password for your new account"]
        return [ACTION_COMPLETE, "welcome", name, "please enter your password"]
        
        
    def login(self, name, pswd):
        if self.authorised:
            return [ACTION_COMPLETE, "you are already logged into account", name]
            
        # create new acc
        if not auth.user_exists(name):
            auth.add_cred(name, pswd)
            data.add_user(name)
            self.authorised = True
            return [ACTION_COMPLETE, "welcome", name, "you are logged into your new account"]

        # or check password
        self.authorised = auth.cred_exists(name, pswd)
        if self.authorised:
            return [ACTION_COMPLETE, "welcome", name, "you are successfully logged in"]
        else:
            return [INVALID_PARAMS, "incorrect password provided for", name]
    
    def get_messages(self, name):
        messages = message.get_messages(name)
        if messages:
            return [ACTION_COMPLETE, '\n'.join(messages)]
        else:
            return [RESOURCE_NOT_FOUND, "None"]


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