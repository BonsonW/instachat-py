
class User:
    def __init__(self, name, pswd):
        self.name = name
        self.pswd = pswd
        self.messages = []
        self.blocked = []

    def blocks(self, other):
        return other in self.blocked
    
    def block(self, other):
        if not self.blocks(other):
            self.blocked.append(other)
            return True
        return False

    def unblock(self, other):
        if self.blocks(other):
            self.blocked.remove(other)
            return True
        return False
    
    def get_messages(self):
        messages = self.messages.copy()
        self.messages.clear()
        return messages