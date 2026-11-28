""" The test user every test acts as; set up once per session by conftest. """

from types import SimpleNamespace

TEST_USER_ID = None
TEST_TOKEN = None


def auth_header():
    return {"Authorization": f"Bearer {TEST_TOKEN}"}


def test_user():
    """What the API layer receives from its auth dependency (only the id is used)."""
    return SimpleNamespace(id=TEST_USER_ID)
