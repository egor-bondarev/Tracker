import uuid
from datetime import datetime, timedelta

import allure
import requests
from fastapi import status
from tests import config

BASE_URL = config.ClientSettings().base_url
GRAPHQL_URL = config.AnalyticsSettings().graphql_url
TIMEOUT = 10
FAR_FUTURE = datetime(2999, 6, 1, 9, 0, 0)


def unique(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def create_category(cleanup, name=None):
    response = requests.post(f"{BASE_URL}/categories", json={"name": name or unique("cat")},
                             timeout=TIMEOUT)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    cleanup["categories"].append(response.json()["id"])
    return response.json()


def start_task(cleanup, timestamp, category_id=None, description=None):
    response = requests.post(
        f"{BASE_URL}/add-record/new/?is_task_finished=false",
        json={"description": description or unique("task"), "timestamp": str(timestamp),
              "category_id": category_id},
        timeout=TIMEOUT)
    if response.status_code == status.HTTP_200_OK:
        cleanup["tasks"].append(response.json()["id"])
    return response


def graphql(query):
    response = requests.post(GRAPHQL_URL, json={"query": query}, timeout=TIMEOUT)
    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert not body.get("errors"), body
    return body["data"]


@allure.epic("Component tests")
@allure.feature("API")
@allure.story("Categories")
def test_category_lifecycle(cleanup):
    created = create_category(cleanup)

    duplicate = requests.post(f"{BASE_URL}/categories", json={"name": created["name"]},
                              timeout=TIMEOUT)
    assert duplicate.status_code == status.HTTP_409_CONFLICT

    renamed = requests.patch(f"{BASE_URL}/categories/{created['id']}",
                             json={"name": unique("renamed"), "archived": True}, timeout=TIMEOUT)
    assert renamed.status_code == status.HTTP_200_OK
    assert renamed.json()["archived"] is True

    active = requests.get(f"{BASE_URL}/categories", timeout=TIMEOUT).json()
    every = requests.get(f"{BASE_URL}/categories?include_archived=true", timeout=TIMEOUT).json()
    assert created["id"] not in [c["id"] for c in active]
    assert created["id"] in [c["id"] for c in every]

    missing = requests.patch(f"{BASE_URL}/categories/0", json={"archived": True}, timeout=TIMEOUT)
    assert missing.status_code == status.HTTP_404_NOT_FOUND


@allure.epic("Component tests")
@allure.feature("API")
@allure.story("Tasks")
def test_task_lifecycle(cleanup):
    cat = create_category(cleanup)
    started = start_task(cleanup, FAR_FUTURE, category_id=cat["id"])
    assert started.status_code == status.HTTP_200_OK, started.text
    task_id = started.json()["id"]

    active = requests.get(f"{BASE_URL}/tasks/active", timeout=TIMEOUT)
    assert active.json()["id"] == task_id
    assert active.json()["category_id"] == cat["id"]
    assert active.json()["duration"] is None

    patched = requests.patch(f"{BASE_URL}/tasks/{task_id}", json={
        "description": "corrected",
        "finish_timestamp": str(FAR_FUTURE + timedelta(hours=25, minutes=1))}, timeout=TIMEOUT)
    assert patched.status_code == status.HTTP_200_OK, patched.text
    assert patched.json()["description"] == "corrected"
    assert patched.json()["duration"] == "25:01:00"

    reversed_range = requests.patch(f"{BASE_URL}/tasks/{task_id}", json={
        "finish_timestamp": str(FAR_FUTURE - timedelta(minutes=1))}, timeout=TIMEOUT)
    assert reversed_range.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    deleted = requests.delete(f"{BASE_URL}/tasks/{task_id}", timeout=TIMEOUT)
    assert deleted.status_code == status.HTTP_204_NO_CONTENT
    assert requests.get(f"{BASE_URL}/tasks/{task_id}", timeout=TIMEOUT).status_code == \
        status.HTTP_404_NOT_FOUND


@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
def test_new_task_with_unknown_category(cleanup):
    response = start_task(cleanup, datetime.now().replace(microsecond=0), category_id=0)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
def test_new_task_in_the_past(cleanup):
    response = start_task(cleanup, datetime.now().replace(microsecond=0) - timedelta(days=3))

    assert response.status_code == status.HTTP_200_OK, response.text


@allure.epic("Component tests")
@allure.feature("Analytics")
@allure.story("GraphQL")
def test_graphql_returns_category_and_running_task(cleanup):
    cat = create_category(cleanup)
    running = start_task(cleanup, FAR_FUTURE, category_id=cat["id"], description=unique("run"))
    assert running.status_code == status.HTTP_200_OK, running.text

    data = graphql(f'''{{
        tasksInPeriod(startDate: "{FAR_FUTURE.date()}", endDate: "{FAR_FUTURE.date()} 23:59:59") {{
            id finishTimestamp duration categoryId category {{ id name archived }}
        }}
        categories {{ id name }}
    }}''')

    tasks = {t["id"]: t for t in data["tasksInPeriod"]}
    task = tasks[running.json()["id"]]
    assert task["finishTimestamp"] is None
    assert task["duration"] is None
    assert task["categoryId"] == cat["id"]
    assert task["category"] == {"id": cat["id"], "name": cat["name"], "archived": False}
    assert cat["id"] in [c["id"] for c in data["categories"]]
