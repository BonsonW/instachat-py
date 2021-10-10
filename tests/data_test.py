# external
import pytest

# internal
from core import data, auth


#region fixtures

@pytest.fixture
def missing_user_cred():
    return ("bar", "foo")

#endregion


#region tests

def test_user_list_initialized():
    for user in data.users:
        assert auth.user_exists(user.name)

def test_add_user_success(missing_user_cred):
    data.add_user(missing_user_cred[0])
    assert data.get_user(missing_user_cred[0]) is not None

#endregion