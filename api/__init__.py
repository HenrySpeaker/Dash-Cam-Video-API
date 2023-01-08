from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api
from flask_limiter import Limiter


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


app = Flask(__name__)
app.config.from_object("config.DevConfig")
db = SQLAlchemy(app)
CORS(app)
api = Api(app)
limiter = Limiter(key_func=get_api_key, app=app, default_limits=[
                  "1000 per day", "30 per hour"], storage_uri="memory://")

video_ns = api.namespace("Videos", description="Dash Cam Videos")
user_ns = api.namespace("Users", description="Users")
comment_ns = api.namespace("Comments", description="Comments on videos")


def create_app():
    """
    Returns an app object.
    """
    with app.app_context():
        from .routes.comment_routes import Comments, CommentList
        from .routes.video_routes import Videos, VideoList
        from .routes.user_routes import Users, UserList
        from .utils.db_management import db_cleanup

        db_cleanup()

    return app
