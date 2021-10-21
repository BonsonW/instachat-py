# external
import pytest
import time

# internal
from src import data, auth
from tests.test_helper import DummyThread
#region fixtures

@pytest.fixture
def user_real_0():
    auth.add_cred("foo", "bar")
    data.add_user("foo", "bar")
    return {"name": "foo", "pswd": "bar", "thread": DummyThread(('127.0.0.1', 5555), "foo", 9998)}

@pytest.fixture
def user_real_1():
    auth.add_cred("bar", "foo")
    data.add_user("bar", "foo")
    return {"name": "bar", "pswd": "foo", "thread": DummyThread(('127.0.0.1', 4444), "foo", 9999)}

@pytest.fixture
def user_fake_0():
    return {"name": "fake", "pswd": "guy", "thread": None}

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
    data.clear()

def test_password_match_success(user_real_0):
    assert data.password_match(user_real_0["name"], user_real_0["pswd"]) == True
    data.clear()

def test_password_match_fail(user_real_0):
    assert data.password_match(user_real_0["name"], user_real_0["name"]) == False
    data.clear()

def test_get_user_success(user_real_0):
    assert data.get_user(user_real_0["name"]) is not None
    data.clear()

def test_get_user_success(user_fake_0):
    assert data.get_user(user_fake_0["name"]) is None
    data.clear()

def test_user_exists_success(user_real_0):
    assert data.user_exists(user_real_0["name"]) == True
    assert data.user_exists(data.ALL_USERS) == True
    data.clear()

def test_get_user_success(user_fake_0):
    assert data.user_exists(user_fake_0["name"]) == False
    data.clear()

def test_set_online_offline_success(user_real_0):
    data.set_online(user_real_0["name"], user_real_0["thread"])
    assert len(data.logs) == 1
    assert len(data.clientThreads) == 1
    data.set_offline(user_real_0["name"], user_real_0["thread"])
    assert len(data.clientThreads) == 0
    data.clear()

def test_get_online_since_before_login(user_real_0, user_real_1):
    ctime = time.time()
    data.set_online(user_real_0["name"], user_real_0["thread"])
    data.set_offline(user_real_0["name"], user_real_0["thread"])
    assert len(data.get_online_since(ctime-1, user_real_1["name"])) == 1
    data.clear()

def test_get_online_since_after_login(user_real_0, user_real_1):
    data.set_online(user_real_0["name"], user_real_0["thread"])
    data.set_offline(user_real_0["name"], user_real_0["thread"])
    ctime = time.time()
    assert len(data.get_online_since(ctime+1, user_real_1["name"])) == 0
    data.clear()

def test_get_online_since_before_server(user_real_0, user_real_1):
    data.set_online(user_real_0["name"], user_real_0["thread"])
    data.set_offline(user_real_0["name"], user_real_0["thread"])
    assert len(data.get_online_since(0, user_real_1["name"])) == 1
    data.clear()

def test_get_online_since_query_self(user_real_0):
    ctime = time.time()
    data.set_online(user_real_0["name"], user_real_0["thread"])
    data.set_offline(user_real_0["name"], user_real_0["thread"])
    assert len(data.get_online_since(ctime-1, user_real_0["name"])) == 0
    data.clear()

def test_get_online_since_query_blocked(user_real_0, user_real_1):
    ctime = time.time()
    data.set_online(user_real_1["name"], user_real_1["thread"])
    data.set_offline(user_real_1["name"], user_real_1["thread"])
    data.get_user(user_real_1["name"]).block(user_real_0["name"])
    assert len(data.get_online_since(ctime-1, user_real_1["name"])) == 0
    data.clear()

def test_get_address_success(user_real_0):
    data.set_online(user_real_0["name"], user_real_0["thread"])
    assert data.get_address(user_real_0["name"]) is not None
    data.clear()

def test_get_address_fail(user_fake_0):
    assert data.get_address(user_fake_0["name"]) is None
    data.clear()

#endregion