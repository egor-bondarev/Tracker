import uuid
from datetime import datetime, timedelta

import allure
import pytest
import requests
from fastapi import status
from tests import config
from tests.helpers import users

BASE_URL = config.ClientSettings().base_url
GRAPHQL_URL = config.AnalyticsSettings().graphql_url
TIMEOUT = 10
START = datetime(2998, 3, 1, 9, 0, 0)


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def unique(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def call(method, path, token=None, **kwargs):
    headers = bearer(token or users.TEST_TOKEN)
    return requests.request(method, f"{BASE_URL}{path}", headers=headers, timeout=TIMEOUT, **kwargs)


def new_category(cleanup, token=None):
    response = call("POST", "/categories", token, json={"name": unique("cat")})
    assert response.status_code == status.HTTP_201_CREATED, response.text
    if token is None:
        cleanup["categories"].append(response.json()["id"])
    return response.json()


def new_task(cleanup, category_id=None, token=None):
    response = call("PUT", f"/tasks/by-client-id/{uuid.uuid4()}", token, json={
        "description": unique("task"), "category_id": category_id,
        "start_timestamp": str(START), "finish_timestamp": str(START + timedelta(minutes=5))})
    assert response.status_code == status.HTTP_201_CREATED, response.text
    if token is None:
        cleanup["tasks"].append(response.json()["id"])
    return response.json()


@allure.epic("Component tests")
@allure.feature("Auth")
@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer wrong"},
                                     {"Authorization": "Basic abc"}, {"Authorization": "Bearer"}])
@pytest.mark.parametrize("method, path", [
    ("GET", "/tasks/active"), ("GET", "/categories"), ("POST", "/add-record/new/?is_task_finished=false"),
    ("PUT", f"/tasks/by-client-id/{uuid.uuid4()}"), ("DELETE", "/categories/1"),
])
def test_requests_without_a_valid_token_are_refused(headers, method, path):
    response = requests.request(method, f"{BASE_URL}{path}", headers=headers, json={},
                                timeout=TIMEOUT)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"] == "Bearer"


@allure.epic("Component tests")
@allure.feature("Auth")
def test_readiness_needs_no_token():
    assert requests.get(f"{BASE_URL}/ready", timeout=TIMEOUT).json() == {"status": "ready"}


@allure.epic("Component tests")
@allure.feature("Users")
def test_users_do_not_see_or_change_each_others_data(cleanup, other_user):
    _, other_token = other_user
    category = new_category(cleanup)
    task = new_task(cleanup, category["id"])

    others = call("GET", "/categories?include_archived=true", other_token).json()
    assert category["id"] not in [c["id"] for c in others]
    for method, path, body in [
        ("GET", f"/tasks/{task['id']}", None),
        ("PATCH", f"/tasks/{task['id']}", {"description": "hijacked"}),
        ("DELETE", f"/tasks/{task['id']}", None),
        ("PATCH", f"/categories/{category['id']}", {"archived": True}),
        ("DELETE", f"/categories/{category['id']}", None),
    ]:
        response = call(method, path, other_token, json=body)
        assert response.status_code == status.HTTP_404_NOT_FOUND, (method, path, response.text)

    # Another user's category cannot be assigned either.
    response = call("POST", "/add-record/new/?is_task_finished=false", other_token, json={
        "description": "x", "timestamp": str(START), "category_id": category["id"]})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert call("GET", f"/tasks/{task['id']}").json()["description"] == task["description"]


@allure.epic("Component tests")
@allure.feature("Users")
def test_a_client_id_belongs_to_one_user(cleanup, other_user):
    _, other_token = other_user
    task = new_task(cleanup)

    response = call("PUT", f"/tasks/by-client-id/{task['client_id']}", other_token, json={
        "description": "copy", "start_timestamp": str(START)})

    assert response.status_code == status.HTTP_409_CONFLICT
    assert call("GET", f"/tasks/{task['id']}").json()["description"] == task["description"]


@allure.epic("Component tests")
@allure.feature("Users")
def test_category_names_are_unique_per_user(cleanup, other_user):
    _, other_token = other_user
    name = unique("shared")
    mine = call("POST", "/categories", json={"name": name})
    assert mine.status_code == status.HTTP_201_CREATED
    cleanup["categories"].append(mine.json()["id"])

    assert call("POST", "/categories", other_token, json={"name": name}).status_code == \
        status.HTTP_201_CREATED
    assert call("POST", "/categories", json={"name": name}).status_code == status.HTTP_409_CONFLICT


@allure.epic("Component tests")
@allure.feature("Categories")
def test_delete_empty_category(cleanup):
    category = new_category(cleanup)

    assert call("DELETE", f"/categories/{category['id']}").status_code == status.HTTP_204_NO_CONTENT
    every = call("GET", "/categories?include_archived=true").json()
    assert category["id"] not in [c["id"] for c in every]
    assert call("DELETE", f"/categories/{category['id']}").status_code == status.HTTP_404_NOT_FOUND


@allure.epic("Component tests")
@allure.feature("Categories")
def test_delete_category_with_tasks_needs_detach(cleanup):
    category = new_category(cleanup)
    task = new_task(cleanup, category["id"])

    refused = call("DELETE", f"/categories/{category['id']}")
    assert refused.status_code == status.HTTP_409_CONFLICT
    assert "1 tasks" in refused.json()["detail"]
    assert call("GET", f"/tasks/{task['id']}").json()["category_id"] == category["id"]

    deleted = call("DELETE", f"/categories/{category['id']}?detach_tasks=true")
    assert deleted.status_code == status.HTTP_204_NO_CONTENT
    kept = call("GET", f"/tasks/{task['id']}")
    assert kept.status_code == status.HTTP_200_OK
    assert kept.json()["category_id"] is None


@allure.epic("Component tests")
@allure.feature("Analytics")
def test_graphql_lists_users_and_filters_by_user(cleanup, other_user):
    other_id, other_token = other_user
    mine = new_task(cleanup)
    theirs = new_task(cleanup, token=other_token)

    def query(user_filter):
        body = {"query": f'''{{
            users {{ id name }}
            tasksInPeriod(startDate: "{START.date()}", endDate: "{START.date()} 23:59:59"{user_filter}) {{ id userId }}
        }}'''}
        result = requests.post(GRAPHQL_URL, json=body, timeout=TIMEOUT).json()
        assert not result.get("errors"), result
        return result["data"]

    everyone = query("")
    assert {users.TEST_USER_ID, other_id} <= {u["id"] for u in everyone["users"]}
    assert {mine["id"], theirs["id"]} <= {t["id"] for t in everyone["tasksInPeriod"]}

    only_mine = query(f", userId: {users.TEST_USER_ID}")["tasksInPeriod"]
    assert mine["id"] in [t["id"] for t in only_mine]
    assert all(t["userId"] == users.TEST_USER_ID for t in only_mine)
