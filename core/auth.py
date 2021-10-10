
cred_path = "core/credentials.txt"

def get_pswd(tname):
    credsFile = open(cred_path, 'r')
    creds = credsFile.readlines()
    for cred in creds:
        name, pswd = cred.split()
        if name == tname:
            return pswd
    return None

def add_cred(name, pswd):
    myCred = ' '.join([name, pswd])
    credsFile = open(cred_path, 'a')
    credsFile.write("\n" + myCred)

def user_exists(tname):
    credsFile = open(cred_path, 'r')
    creds = credsFile.readlines()
    for cred in creds:
        name = cred.split()[0]
        if name == tname:
            return True
    return False

def cred_exists(name, pswd):
    myCred = ' '.join([name, pswd])
    credsFile = open(cred_path, 'r')
    creds = credsFile.readlines()
    for cred in creds:
        if cred == myCred:
            return True
    return False

