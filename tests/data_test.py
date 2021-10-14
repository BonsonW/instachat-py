# external
import pytest
import time

# internal
from src import data, auth


#region fixtures

@pytest.fixture
def existing_user_cred():
    auth.add_cred("foo", "bar")
    return ("foo", "bar")

@pytest.fixture
def missing_user_cred():
    return ("bar", "foo")

#endregion


#region tests

def test_user_list_initialized():
    for user in data.users:
        assert auth.user_exists(user.name)

def test_add_remove_user_success(missing_user_cred):
    data.add_user(missing_user_cred[0], missing_user_cred[1])
    assert data.user_exists(missing_user_cred[0]) == True
    data.remove_user(missing_user_cred[0])
    assert data.user_exists(missing_user_cred[0]) == False

def test_password_match_success(existing_user_cred):
    assert data.password_match(existing_user_cred[0], existing_user_cred[1]) == True

def test_password_match_fail(existing_user_cred):
    assert data.password_match(existing_user_cred[0], existing_user_cred[0]) == False

def test_get_user_success(existing_user_cred):
    assert data.get_user(existing_user_cred[0]) is not None

def test_get_user_success(missing_user_cred):
    assert data.get_user(missing_user_cred[0]) is None

def test_user_exists_success(existing_user_cred):
    assert data.user_exists(existing_user_cred[0]) == True
    assert data.user_exists(data.ALL_USERS) == True

def test_get_user_success(missing_user_cred):
    assert data.user_exists(missing_user_cred[0]) == False

def test_set_online_offline_success(existing_user_cred):
    data.set_online(existing_user_cred[0])
    assert len(data.logs) == 1
    assert len(data.get_online_now()) == True
    data.set_offline(existing_user_cred[0])
    assert len(data.get_online_now()) == False

def test_get_online_since_before(existing_user_cred):
    ctime = time.time()
    data.set_online(existing_user_cred[0])
    assert len(data.get_online_since(ctime-1)) == 1
    data.set_offline(existing_user_cred[0])

def test_get_online_since_after(existing_user_cred):
    data.set_online(existing_user_cred[0])
    ctime = time.time()
    assert len(data.get_online_since(ctime+1)) == 0
    data.set_offline(existing_user_cred[0])

#endregion