# external
from socket import *
from threading import Thread
import sys, select

# internal
import core.auth as auth
from core.request_methods import *
from core.response_codes import *

#region client thread

class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        self.credentials = None
        self.authorised = False
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
    def run(self):
        response = ""
        while self.clientAlive:
            data = self.clientSocket.recv(1024)
            method, param = data.decode().split(' ', 1)

            if method == QUIT:
                self.clientAlive = False
                response = ' '.join([CONVERSATION_END, "ending connection, goodbye"])
                break
            elif method == HELO:
                self.login(response, param)
            elif method == PSWD:
                try:
                    self.login(response, self.credentials["name"], param)
                except:
                    response = ' '.join([OUT_OF_SEQUENCE, "you must provide your username before your password"])
            else:
                response = ' '.join([INVALID_METHOD, "the method you have requested is not available"])

            self.clientSocket.send(response.encode)

#region request method processes

    def login(self, response, name):
        pswd = auth.get_pswd(name)
        self.credentials = {"name": name, "pswd": pswd}

        if pswd is None:
            response = ' '.join([REQUIRE_NEW_ACC, "hello", name, "please enter a password for your new account"])
        else:
            response = ' '.join([ACTION_COMPLETE, "welcome", name, ", please enter your password"])
        
        
    def login(self, response, name, pswd):
        if self.authorised:
            response = ' '.join([ACTION_COMPLETE, "you are already logged into account", name])
            return

        if self.credentials["pswd"] is not None:
            self.authorised = (pswd == self.credentials["pswd"])
            response = ' '.join([ACTION_COMPLETE, "welcome", name, ", you are successfully logged in"])
        else:
            auth.add_cred(name, pswd)
            self.authorised = True
            response = ' '.join([ACTION_COMPLETE, "welcome", name, ", you are logged into your new account"])


#endregion

#endregion

#region welcome process

# acquire server host and port from command line parameter
if len(sys.argv) != 2:
    print("\n===== Error usage, python3 TCPServer3.py SERVER_PORT ======\n");
    exit(0);
serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")

while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    clientThread.start()

#endregion