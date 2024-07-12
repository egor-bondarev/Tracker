""" Helper for working with API. """

import json
from datetime import datetime
import requests
from tests import config

def get_service_url():
    client_config = config.ClientSettings()
    return client_config.service_url

SERVICE_URL = get_service_url()

def post_new_task(description: str, timestamp: datetime, is_task_finished: bool):
    return requests.post(
        f"{SERVICE_URL}/new/?is_task_finished={is_task_finished}",
        json={"description": f"{description}", "timestamp": f"{timestamp}"},
        timeout=1000
    )

def post_new_task_custom_body(body: json, is_task_finished: bool):
    return requests.post(
        f"{SERVICE_URL}/new/?is_task_finished={is_task_finished}",
        json=body,
        timeout=1000
    )

def post_new_task_without_is_task_finished_flag(description: str, timestamp: datetime):
    return requests.post(
        f"{SERVICE_URL}/new/",
        json={"description": f"{description}", "timestamp": f"{timestamp}"},
        timeout=1000
    )

def post_new_task_wrong_is_task_finished_flag(description: str, timestamp: datetime, is_task_finished):
    return requests.post(
        f"{SERVICE_URL}/new/?is_task_finished={is_task_finished}",
        json={"description": f"{description}", "timestamp": f"{timestamp}"},
        timeout=1000
    )

def post_finish_task(task_id: int, timestamp: datetime):
    return requests.post(
        f"{SERVICE_URL}/finish/",
        json={"id": f"{task_id}", "timestamp": f"{timestamp}"},
        timeout=1000
    )

def post_finish_task_custom_body(body: json):
    return requests.post(
        f"{SERVICE_URL}/finish/",
        json=body,
        timeout=1000
    )
