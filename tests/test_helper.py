
class DummyThread:
    def __init__(self, clientAddress, user, listeningPort):
        self.clientAddress = clientAddress
        self.listeningPort = listeningPort
        self.user = user