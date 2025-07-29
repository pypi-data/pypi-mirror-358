import json
from typing import Optional

default_cors_headers = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}


def generate_successful_response(body, status_code: int = 200):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": default_cors_headers
    }


def generate_created_response():
    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Create operation successful"}),
        "headers": default_cors_headers
    }


def generate_not_found_response(custom_message: Optional[str] = None):
    return {
        "statusCode": 404,
        "body": json.dumps({"message": "Unable to find resource"}),
        "headers": default_cors_headers
    }


def generate_server_error_response(error_message):
    return {
        "statusCode": 500,
        "body": json.dumps({"message": "Server error: " + error_message}),
        "headers": default_cors_headers
    }
