# internal
from core import data

def send(senderName, recipientName, message):
    recipent = data.get_user(recipientName)
    recipent.messages.put({"sender": senderName, "message": message})

def get_messages(recipientName):
    user = data.get_user(recipientName)
    messages = []
    while not user.messages.empty():
        messages.append(user.messages.get())
    return messages