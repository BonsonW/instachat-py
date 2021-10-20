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
    success = True
    for name in data.get_online_now():
        if name != senderName:
            success = success and send(senderName, name, messageBody)
    return success