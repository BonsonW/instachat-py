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

#endregion