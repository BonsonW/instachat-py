# external
import pytest

# internal
from src.user import User

#region fixtures

@pytest.fixture
def user0():
    return User("bar", "foo")

@pytest.fixture
def user1():
    return User("bar", "foo")

#endregion

def test_block_unblock_success(user0, user1):
    user0.block(user1.name)
    assert user0.blocks(user1.name) == True
    user0.unblock(user1.name)
    assert user0.blocks(user1.name) == False