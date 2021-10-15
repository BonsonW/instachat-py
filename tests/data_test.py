# external
import pytest
import time

# internal
from src import data, auth


class DummyThread:
    def __init__(self, clientAddress, user):
        self.clientAddress = clientAddress
        self.user = user

#region fixtures

@pytest.fixture
def user_real_0():
    auth.add_cred("foo", "bar")
    return {"name": "foo", "pswd": "bar", "thread": DummyThread(('127.0.0.1', 5555), "foo")}
@pytest.fixture
def user_fake_0():
    return {"name": "bar", "pswd": "foo", "thread": None}

#endregion


#region tests

def test_user_list_initialized():
    for user in data.users:
        assert auth.user_exists(user.name)

def test_add_remove_user_success(user_fake_0):
    data.add_user(user_fake_0["name"], user_fake_0["pswd"])
    assert data.user_exists(user_fake_0["name"]) == True
    data.remove_user(user_fake_0["name"])
    assert data.user_exists(user_fake_0["name"]) == False

def test_password_match_success(user_real_0):
    assert data.password_match(user_real_0["name"], user_real_0["pswd"]) == True

def test_password_match_fail(user_real_0):
    assert data.password_match(user_real_0["name"], user_real_0["name"]) == False

def test_get_user_success(user_real_0):
    assert data.get_user(user_real_0["name"]) is not None

def test_get_user_success(user_fake_0):
    assert data.get_user(user_fake_0["name"]) is None

def test_user_exists_success(user_real_0):
    assert data.user_exists(user_real_0["name"]) == True
    assert data.user_exists(data.ALL_USERS) == True

def test_get_user_success(user_fake_0):
    assert data.user_exists(user_fake_0["name"]) == False

def test_set_online_offline_success(user_real_0):
    data.set_online(user_real_0["name"], user_real_0["thread"])
    assert len(data.logs) == 1
    assert len(data.get_online_now()) == True
    data.set_offline(user_real_0["name"], user_real_0["thread"])
    assert len(data.get_online_now()) == False

def test_get_online_since_before(user_real_0):
    ctime = time.time()
    data.set_online(user_real_0["name"], user_real_0["thread"])
    assert len(data.get_online_since(ctime-1)) == 1
    data.set_offline(user_real_0["name"], user_real_0["thread"])

def test_get_online_since_after(user_real_0):
    data.set_online(user_real_0["name"], user_real_0["thread"])
    ctime = time.time()
    assert len(data.get_online_since(ctime+1)) == 0
    data.set_offline(user_real_0["name"], user_real_0["thread"])

def test_get_address_success(user_real_0):
    data.set_online(user_real_0["name"], user_real_0["thread"])
    assert data.get_address(user_real_0["name"]) is not None

def test_get_address_fail(user_fake_0):
    assert data.get_address(user_fake_0["name"]) is None

#endregion