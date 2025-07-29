import json
from typing import Optional, TypedDict

default_cors_headers = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}


class Response(TypedDict):
    statusCode: int
    headers: dict[str, str]
    body: str


def generate_successful_response(body, status_code: int = 200) -> Response:
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": default_cors_headers
    }


def generate_created_response() -> Response:
    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Create operation successful"}),
        "headers": default_cors_headers
    }


def generate_not_found_response(custom_message: Optional[str] = None) -> Response:
    message = custom_message if custom_message is not None else "Unable to find resource"
    return {
        "statusCode": 404,
        "body": json.dumps({"message": message}),
        "headers": default_cors_headers
    }


def generate_server_error_response(error_message: str) -> Response:
    return {
        "statusCode": 500,
        "body": json.dumps({"message": "Server error: " + error_message}),
        "headers": default_cors_headers
    }
