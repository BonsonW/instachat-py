# internal
from src import data

# return True if all users sent message successfully
def send(senderName, recipientName, messageBody):
    if (recipientName == data.ALL_USERS):
        broadcast(senderName, messageBody)
        return
    recipient = data.get_user(recipientName)
    if recipient.blocks(senderName):
        return
    recipient.messages.append(' '.join([senderName + ":", messageBody]))

def get_messages(name):
    user = data.get_user(name)
    messages = user.get_messages()
    return messages

# return True if all users sent message successfully
def broadcast(senderName, messageBody):
    for name in data.get_online_now():
        if name != senderName:
            send(senderName, name, messageBody)