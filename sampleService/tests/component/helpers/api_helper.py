""" Helper for working with API. """

import json
import requests
from sampleService.tests import config

def get_service_url():
    client_config = config.ClientSettings()
    return client_config.service_url

SERVICE_URL = get_service_url()

def post_user(username: str):
    return requests.post(
        f"{SERVICE_URL}/add2db/",
        json={"username": f"{username}"},
        timeout=1000
    )

def post_user_custom_body(body: json):
    return requests.post(
        f"{SERVICE_URL}/add2db/",
        json=body,
        timeout=1000
    )

def post_user_invalid_json(body: str):
    return requests.post(
        f"{SERVICE_URL}/add2db/",
        data=body,
        timeout=1000
    )

def post_user_none_name():
    return requests.post(
        f"{SERVICE_URL}/add2db/",
        json={"username": None},
        timeout=1000
    )

def get_user(user_id):
    return requests.get(
        f"{SERVICE_URL}/{user_id}",
        timeout=1000
    )

def get_user_empty_id():
    return requests.get(
        f"{SERVICE_URL}/",
        timeout=1000
    )
