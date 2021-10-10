# internal
from src import data

def send(senderName, recipientName, message):
    recipent = data.get_user(recipientName)
    recipent.messages.append(' '.join(senderName + ":", message))

def get_messages(name):
    user = data.get_user(name)
    messages = user.messages.copy()
    user.messages.clear()
    return messages