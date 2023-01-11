from flask import request


def get_api_key():
    api_key = None
    content_length = request.content_length
    if not content_length:
        return api_key
    if request.args:
        api_key = request.args.get("api_key")
    elif request.json:
        api_key = request.json.get("api_key")
    return api_key
