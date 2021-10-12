# external
import time

# internal
from src import auth
from src.user import User

ALL_USERS = "All"

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

def set_online(name):
    get_user(name).online = True
    logs.append({"name": name, "since": time.time()})

def set_offline(name):
    get_user(name).online = False

def get_online_since(timeStamp):
    onlineSince = []
    for log in logs:
        if log["since"] > timeStamp and log["name"] not in onlineSince:
            onlineSince.append(log["name"])
    return onlineSince

def get_online_now():
    onlineNow = []
    for user in users:
        if user.online:
            onlineNow.append(user)
    return onlineNow

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
