# external
import time

# internal
from src import auth
from src.user import User

ALL_USERS = "All"

users = []
online = []

#region methods

def get_user(name):
    for user in users:
        if user.name == name:
            return user
    return None

def add_user(name, pswd):
    if user_exists(name):
        return
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
    online.append({"name": name, "since": time.time()})

def set_offline(name):
    for log in online:
        if log["name"] == name:
            online.remove(log)
            return

def get_online_since(timeStamp):
    res = []
    for log in online:
        if log["since"] > timeStamp:
            res.append(log["name"])
    return res

#endregion

# intitialization
with open(auth.cred_path, "r") as f:
    creds = f.readlines()
for cred in creds:
    name, pswd = cred.split()
    add_user(name, pswd)
