# internal
from core import data, auth

def test_user_list():
    for user in data.users:
        assert auth.user_exists(user.name)