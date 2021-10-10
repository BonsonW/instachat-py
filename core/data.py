# internal
from core import auth, user

users = []

# add all existing users to database
with open(auth.cred_path, "r") as f:
    creds = f.readlines()
for cred in creds:
    name = cred.split()[0]
    users.append(user.User(name))

