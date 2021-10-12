

class User:
    def __init__(self, name, pswd):
        self.name = name
        self.pswd = pswd
        self.messages = []
        self.blocked = []

    def blocks(self, other):
        return other in self.blocked
    
    def block(self, other):
        self.blocked.append(other)

    def unblock(self, other):
        self.blocked.remove(other)