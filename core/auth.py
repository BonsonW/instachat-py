cred_path = "core/credentials.txt"

def add_cred(name, pswd):
    if cred_exists(name, pswd):
        return
    tcred = ' '.join([name, pswd])
    credsFile = open(cred_path, 'a')
    credsFile.write("\n" + tcred)

def user_exists(tname):
    with open(cred_path, "r") as f:
        creds = f.readlines()
    for cred in creds:
        name = cred.split()[0]
        if name == tname:
            return True
    return False

def cred_exists(name, pswd):
    tcred = ' '.join([name, pswd])
    credsFile = open(cred_path, 'r')
    creds = credsFile.readlines()
    for cred in creds:
        if cred.strip("\n") == tcred:
            return True
    return False

