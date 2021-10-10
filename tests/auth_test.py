import pytest
import os.path as path
from core import auth

#region fixtures

@pytest.fixture
def valid_user_cred():
    return ("foo", "bar")

@pytest.fixture
def invalid_user_cred():
    return ("bar", "foo")

#endregion

#region tests

def test_get_pswd_success(valid_user_cred):
    assert auth.get_pswd(valid_user_cred[0]) != None

def test_get_pswd_fail(invalid_user_cred):
    assert auth.get_pswd(invalid_user_cred[0]) == None

#endregion