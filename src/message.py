# internal
from src import data

def send(senderName, recipientName, messageBody):
    if (recipientName == data.ALL_USERS):
        return broadcast(senderName, messageBody)
    recipient = data.get_user(recipientName)
    if recipient.blocks(senderName):
        return False
    recipient.messages.append(' '.join([senderName + ":", messageBody]))
    return True

def get_messages(name):
    user = data.get_user(name)
    messages = user.get_messages()
    return messages

def broadcast(senderName, messageBody):
    onlineNow = data.get_online_now(senderName)
    for name in onlineNow:
        send(senderName, name, messageBody)
    return len(onlineNow) == len(data.clientThreads) - 1