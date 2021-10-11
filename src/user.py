

class User:
    def __init__(self, name, pswd):
        self.name = name
        self.pswd = pswd
        self.messages = []
        self.blocked = []