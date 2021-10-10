# internal
from core import auth, user

users = []

#region methods

def get_user(name):
    for user in users:
        if user.name == name:
            return user
    return None

def add_user(name):
    users.append(user.User(name))

def user_initialized(name):
    return get_user(name) is not None

#endregion

# add all existing users to database
with open(auth.cred_path, "r") as f:
    creds = f.readlines()
for cred in creds:
    name = cred.split()[0]
    add_user(name)
