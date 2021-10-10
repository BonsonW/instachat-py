# external
from socket import *
import sys

# internal
from request_methods import *

#region client methods

def login(clientSocket):
    name = input("name: ")
    clientSocket.sendall(' '.join([HELO, name]).encode())
    pswd = input("password: ")
    clientSocket.sendall(' '.join([PSWD, pswd]).encode())
    # retry if pswd invalid

def logout(clientSocket):
    pass

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



#region client loop

while True:
    # send method
    message = input("===== please type any messsage you want to send to server: =====\n")
    
    if message == "logout":
        logout()
    # recieve response
    data = clientSocket.recv(1024)
    status, response = data.decode()

    # print response given by server
    print(response)
        
    ans = input('\nDo you want to continue(y/n) :')
    if ans == 'y':
        continue
    else:
        break

#end region

# close the socket
clientSocket.close()

