# internal
from core import data

def send(senderName, recipientName, message):
    recipent = data.get_user(recipientName)
    recipent.messages.append({"sender": senderName, "message": message})

def get_messages(recipientName):
    user = data.get_user(recipientName)
    messages = user.messages.copy()
    user.messages.clear()
    return messages