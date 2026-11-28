import uuid

import allure
import pytest
from tests.conftest import TestingSessionLocal, delete_user
from tracker_db import users as cli
from tracker_db.auth import hash_token
from tracker_db.models import User


def run(capsys, *argv):
    cli.main(list(argv), session_factory=TestingSessionLocal)
    return capsys.readouterr().out.strip()


@pytest.fixture(name="name")
def name_fixture():
    name = f"cli-{uuid.uuid4().hex[:12]}"
    yield name
    session = TestingSessionLocal()
    try:
        for user in session.query(User).filter(User.name.like(f"{name}%")):
            delete_user(user.id)
    finally:
        session.close()


def stored(name):
    session = TestingSessionLocal()
    try:
        return session.query(User).filter(User.name == name).one()
    finally:
        session.close()


@allure.epic("Unit tests")
@allure.feature("Users CLI")
def test_add_prints_a_token_whose_hash_is_stored(capsys, name):
    token = run(capsys, "add", name)

    assert len(token) >= 40
    assert stored(name).token_hash == hash_token(token)


@allure.epic("Unit tests")
@allure.feature("Users CLI")
def test_token_replaces_the_previous_token(capsys, name):
    first = run(capsys, "add", name)
    second = run(capsys, "token", name)

    assert first != second
    assert stored(name).token_hash == hash_token(second)


@allure.epic("Unit tests")
@allure.feature("Users CLI")
def test_rename_and_list(capsys, name):
    run(capsys, "add", name)
    run(capsys, "rename", name, f"{name}-new")

    listing = run(capsys, "list")
    assert f"\t{name}-new\ttoken set\t0 tasks\t0 categories" in listing


@allure.epic("Unit tests")
@allure.feature("Users CLI")
@pytest.mark.parametrize("argv", [("token", "nobody-{}"), ("add", "{}"), ("add", "")])
def test_errors_exit_without_changes(capsys, name, argv):
    run(capsys, "add", name)
    with pytest.raises(SystemExit):
        run(capsys, argv[0], argv[1].format(name) if "{}" in argv[1] else argv[1])
