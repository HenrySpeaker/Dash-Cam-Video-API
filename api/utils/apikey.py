from ..models.users import User
import functools
from werkzeug.security import check_password_hash
from flask import request


def require_api_key(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if request.method == "GET":
            return func(*args, **kwargs)
        elif request.method != "GET" and request.json:
            possible_key = request.json.get("api_key")
            username = request.json.get("username")
            possible_user = User.get_from_username(username)
            print(possible_key)

            if possible_user and check_password_hash(possible_user.hashed_key, possible_key):
                return func(*args, **kwargs)
            else:
                return {"message": "Invalid API key provided"}, 403

        else:
            return {"message": "No API key provided"}, 400

    return inner
