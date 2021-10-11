# external
import pytest

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

def test_add_user_success(missing_user_cred):
    data.add_user(missing_user_cred[0], missing_user_cred[1])
    assert data.user_exists(missing_user_cred[0]) == True

def test_password_match(existing_user_cred):
    assert data.password_match(existing_user_cred[0], existing_user_cred[1]) == True

#endregion