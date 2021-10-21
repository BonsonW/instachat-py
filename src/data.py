# external
import time

# internal
from src import auth
from src.user import User

ALL_USERS = "All"

startTime = time.time()

clientThreads = []
users = []
logs = []

#region methods

def get_user(name):
    for user in users:
        if user.name == name:
            return user
    return None

def add_user(name, pswd):
    if not user_exists(name):
        users.append(User(name, pswd))

def remove_user(name):
    user = get_user(name)
    users.remove(user)

def user_exists(name):
    return get_user(name) is not None or name == ALL_USERS

def password_match(name, pswd):
    user = get_user(name)
    return user.pswd == pswd

def set_online(name, clientThread):
    clientThreads.append(clientThread)
    logs.append({"name": name, "since": time.time()})

def set_offline(name, clientThread):
    clientThreads.remove(clientThread)
    get_user(name).online = False

def get_online_since(timeStamp, name):
    onlineSince = []
    for log in logs:
        other = get_user(log["name"])
        if log["since"] > timeStamp and log["name"] not in onlineSince and not other.blocks(name) and not name == log["name"]:
            onlineSince.append(log["name"])
    return onlineSince

def get_online_now(name):
    onlineNow = []
    for clientThread in clientThreads:
        other = get_user(clientThread.user)
        if clientThread.user != name and not other.blocks(name):
            onlineNow.append(clientThread.user)  
    return onlineNow

def get_address(name):
    clientThread = get_clientThread(name)
    if clientThread is None:
        return None
    return (clientThread.clientAddress[0], clientThread.listeningPort)

def get_clientThread(name):
    for clientThread in clientThreads:
        if clientThread.user == name:
            return clientThread
    return None

def clear():
    users.clear()
    logs.clear()

#endregion

# intitialization
with open(auth.cred_path, "r") as f:
    creds = f.readlines()
for cred in creds:
    name, pswd = cred.split()
    add_user(name, pswd)
