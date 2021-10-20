# external
import pytest
import os.path as path

# internal
from src import auth

#region fixtures

@pytest.fixture
def existing_user_cred():
    auth.add_cred("real", "guy")
    return ("real", "guy")

@pytest.fixture
def missing_user_cred():
    return ("fake", "guy")

#endregion

#region tests

def test_credentials_file_exists():
    assert path.exists(auth.cred_path) == True

def test_user_exists_success(existing_user_cred):
    assert auth.user_exists(existing_user_cred[0]) == True

def test_user_exists_fail(missing_user_cred):
    assert auth.user_exists(missing_user_cred[0]) == False

def test_cred_exists_success(existing_user_cred):
    assert auth.cred_exists(existing_user_cred[0], existing_user_cred[1]) == True

def test_cred_exists_fail(missing_user_cred):
    assert auth.cred_exists(missing_user_cred[0], missing_user_cred[1]) == False

#endregion