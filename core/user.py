import queue

class User:
    def __init__(self, name):
        self.name = name
        self.messages = queue.Queue()
        self.blocked = []