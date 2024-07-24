import json
from datetime import datetime
import requests
from helpers.tests import config

def get_service_url():
    client_config = config.ClientSettings()
    return client_config.service_url

SERVICE_URL = get_service_url()

def post_new_task(description: str, timestamp: str):
    return requests.post(
        f"{SERVICE_URL}/new/?is_task_finished=false",
        json={"description": f"{description}", "timestamp": f"{timestamp}"},
        timeout=1000
    )

def post_finish_task(task_id: int, timestamp: datetime):
    return requests.post(
        f"{SERVICE_URL}/finish/",
        json={"id": f"{task_id}", "timestamp": f"{timestamp}"},
        timeout=1000
    )

def load_data_from_file(file_list: list):
    for file in file_list:
        with open(file,'r+', encoding="utf-8") as json_file:
            try:
                file_data = json.load(json_file)
            except json.decoder.JSONDecodeError as exception:
                print(exception)

            for record in file_data["Tasks"]:
                print(SERVICE_URL)
                print(record['description'])
                start_response = post_new_task(record['description'], record['start_timestamp'])
                assert start_response.status_code == 200
                print(start_response.json()['id'])
                finish_response = post_finish_task(start_response.json()['id'], record['finish_timestamp'])
                assert finish_response.status_code == 200
                
                

def remove_file_data_from_db(): pass

def generate_random_data(): pass

def remove_random_generated_data_from_db(): pass

load_data_from_file(['./helpers/tests/data_generator/data/web_ui.json'])