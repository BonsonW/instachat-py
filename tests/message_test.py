# external
import pytest

# internal
from src import message, data


#region fixtures

@pytest.fixture
def senderName():
    data.add_user("foo", "bar")
    return "foo"

@pytest.fixture
def recipientName():
    data.add_user("bar", "foo")
    return "bar"

#endregion

#region tests

def test_send_success(senderName, recipientName):
    message.send(senderName, recipientName, "this is a message")
    assert len(message.get_messages(recipientName)) == 1
    assert len(message.get_messages(recipientName)) == 0

def test_send_blocked(senderName, recipientName):
    recipient = data.get_user(recipientName)
    recipient.block(senderName)
    message.send(senderName, recipientName, "this is a message")
    assert len(message.get_messages(recipientName)) == 0
    recipient.unblock(senderName)

def test_broadcast_success(senderName, recipientName):
    message.send(senderName, data.ALL_USERS, "this is a message")
    for user in data.users:
        if user.name != senderName:
            assert len(message.get_messages(user.name)) == 1
        else:
            assert len(message.get_messages(user.name)) == 0

def test_broadcast_blocked(senderName, recipientName):
    recipient = data.get_user(recipientName)
    recipient.block(senderName)
    message.send(senderName, data.ALL_USERS, "this is a message")
    for user in data.users:
        if user.name != senderName and user.name != recipientName:
            assert len(message.get_messages(user.name)) == 1
        else:
            assert len(message.get_messages(user.name)) == 0
    recipient.unblock(senderName)

#endregion