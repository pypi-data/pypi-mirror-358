def generate_response(status, headers, body):
    return {
        'statusCode': status,
        'headers': headers,
        'body': body
    }