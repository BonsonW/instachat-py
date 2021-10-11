# internal
from src import auth
from src.user import User

users = []

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

def user_exists(name):
    return get_user(name) is not None

def password_match(name, pswd):
    user = get_user(name)
    return user.pswd == pswd

#endregion

# add all existing users to database
with open(auth.cred_path, "r") as f:
    creds = f.readlines()
for cred in creds:
    name, pswd = cred.split()
    add_user(name, pswd)
