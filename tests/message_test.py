# external
import pytest

# internal
from src import message, data, auth
from tests.test_helper import DummyThread

#region fixtures

@pytest.fixture
def senderName():
    data.add_user("foo", "bar")
    return "foo"

@pytest.fixture
def recipientName():
    data.add_user("real", "guy")
    return "real"

@pytest.fixture
def user_real_0():
    auth.add_cred("real", "guy")
    return {"name": "real", "pswd": "guy", "thread": DummyThread(('127.0.0.1', 5555), "real", 9998)}

#endregion

#region tests

def test_send_success(senderName, recipientName):
    assert message.send(senderName, recipientName, "this is a message") == True
    assert len(message.get_messages(recipientName)) == 1
    assert len(message.get_messages(recipientName)) == 0

def test_send_blocked(senderName, recipientName):
    recipient = data.get_user(recipientName)
    recipient.block(senderName)
    assert message.send(senderName, recipientName, "this is a message") == False
    assert len(message.get_messages(recipientName)) == 0
    recipient.unblock(senderName)

def test_broadcast_success(senderName, user_real_0):
    data.set_online(user_real_0["name"], user_real_0["thread"])
    assert message.send(senderName, data.ALL_USERS, "this is a message") == True
    for user in data.users:
        if user.name == user_real_0["name"]:
            assert len(message.get_messages(user.name)) == 1
        else:
            assert len(message.get_messages(user.name)) == 0
    data.set_offline(user_real_0["name"], user_real_0["thread"])

def test_broadcast_offline(senderName):
    assert message.send(senderName, data.ALL_USERS, "this is a message") == True
    for user in data.users:
        assert len(message.get_messages(user.name)) == 0
            
def test_broadcast_blocked(senderName, recipientName, user_real_0):
    data.set_online(user_real_0["name"], user_real_0["thread"])
    recipient = data.get_user(recipientName)
    recipient.block(senderName)
    assert message.send(senderName, data.ALL_USERS, "this is a message") == False
    for user in data.users:
        assert len(message.get_messages(user.name)) == 0
    recipient.unblock(senderName)
    data.set_offline(user_real_0["name"], user_real_0["thread"])

#endregion