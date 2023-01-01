from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS
from flask_restx import Api

app = Flask(__name__)
app.config.from_object("config.DevConfig")
db = SQLAlchemy(app)
CORS(app)
api = Api(app)

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
