
class User:
    def __init__(self, name, pswd):
        self.name = name
        self.pswd = pswd
        self.messages = []
        self.blocked = []
        self.online = False

    def blocks(self, other):
        return other in self.blocked
    
    def block(self, other):
        self.blocked.append(other)

    def unblock(self, other):
        self.blocked.remove(other)
    
    def get_messages(self):
        messages = self.messages.copy()
        self.messages.clear()
        return messages