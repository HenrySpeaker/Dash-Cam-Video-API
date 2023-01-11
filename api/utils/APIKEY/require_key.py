from ...models.users import User
import functools
from flask import request
from ... import db


def require_api_key(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if request.method == "GET":
            return func(*args, **kwargs)
        elif request.method != "GET" and request.json:
            possible_key = request.json.get("api_key")
            # print("possible key is " + str(possible_key))
            if not possible_key:
                return {"message": "No API key provided"}, 400
            users = db.session.query(User)
            for user in users:
                if user.key == possible_key:
                    return func(*args, **kwargs)

            return {"message": "Invalid API key provided"}, 403

        else:
            return {"message": "No API key provided"}, 400

    return inner
