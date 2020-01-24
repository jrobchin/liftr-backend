import json


def response_message(success=True, message='', data={}, error=''):
    return json.dumps({
        "success": success,
        "message": message,
        "data": data,
        "error": error
    })