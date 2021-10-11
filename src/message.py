# internal
from src import data

def send(senderName, recipientName, messageBody):
    if (recipientName == data.ALL_USERS):
        broadcast(senderName, messageBody)
        return
    recipent = data.get_user(recipientName)
    recipent.messages.append(' '.join([senderName + ":", messageBody]))

def get_messages(name):
    user = data.get_user(name)
    messages = user.messages.copy()
    user.messages.clear()
    return messages

def broadcast(senderName, messageBody):
    for user in data.users:
        if user.name != senderName:
            send(senderName, user.name, messageBody)