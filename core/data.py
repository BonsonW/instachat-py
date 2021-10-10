# internal
from auth import cred_path
from user import User

users = []

# add all existing users to database
with open(cred_path, "r") as f:
    creds = f.readlines()
for cred in creds:
    name = cred.split()[0]
    users.append(User(name))

