from fastapi import status, HTTPException
from pydantic import ValidationError

def api_field_required(field_name, response):
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert field_name in response.json()["detail"][0]["loc"]

def api_wrong_field_type(field_name, response, data_type):
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert f"Input should be a valid {data_type}" in response.json()["detail"][0]["msg"]
    assert field_name in response.json()["detail"][0]["loc"]

def api_wrong_field_type_custom_msg(field_name, response, message):
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert message in response.json()["detail"][0]["msg"]
    assert field_name in response.json()["detail"][0]["loc"]

def exception_field_required(exception, field_name):
    assert ValidationError == exception.type
    assert exception.value.errors()[0]["loc"][0] == field_name
    assert exception.value.errors()[0]['msg'] == 'Field required'

def exception_wrong_field_type(exception, field_name, data_type):
    assert ValidationError == exception.type
    assert exception.value.errors()[0]["loc"][0] == field_name
    assert f'Input should be a valid {data_type}' in exception.value.errors()[0]["msg"]

def exception_wrong_field_type_custom_msg(exception, field_name, message):
    assert ValidationError == exception.type
    assert exception.value.errors()[0]["loc"][0] == field_name
    assert message in exception.value.errors()[0]["msg"]

def exception_missing_field(exception, field_name):
    assert HTTPException == exception.type
    assert exception.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exception.value.detail == f'Flag {field_name} is missing.'

def exception_validate_field(exception, field_name, expected_error):
    assert ValidationError == exception.type
    assert exception.value.errors()[0]["loc"][0] == field_name
    assert expected_error in exception.value.errors()[0]["msg"]
