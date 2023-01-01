from ..models.users import User
from .. import user_ns
from flask_restx import Resource, fields, reqparse
from .. import db, api
import uuid
from ..utils.apikey import require_api_key

get_parser = reqparse.RequestParser()
get_parser.add_argument("username", required=False)

post_parser = get_parser.copy()
post_parser.replace_argument("username", required=True)
post_parser.add_argument("api_key")

user_model = api.model("User", {
    "username": fields.String,
    "id": fields.Integer
})

new_user_model = api.inherit('New User', user_model, {
    "key": fields.String
})


@user_ns.route("/")
class UserList(Resource):
    @user_ns.marshal_list_with(user_model)
    @user_ns.expect(get_parser)
    def get(self):
        """
        First checks parser for any username provided and returns that user's data (if it exists) as JSON in a list.
        Otherwise, returns all users' data in JSON objects within a list.
        """
        args = get_parser.parse_args()
        if args["username"]:
            user = db.session.execute(db.select(User).filter_by(
                username=args["username"])).first()

            if user:
                return [user[0].to_dict()]

            return [], 404

        user_list = db.session.execute(db.select(User)).all()
        user_list_json = [user[0].to_dict() for user in user_list]

        return user_list_json

    @user_ns.marshal_with(new_user_model)
    @user_ns.expect(post_parser)
    def post(self):
        """
        Confirms that no user with that username already exists, and if so, creates a new user an returns their data as JSON object.
        """
        args = post_parser.parse_args()
        possible_user = db.session.execute(
            db.select(User).filter_by(username=args["username"])).first()

        if possible_user:
            return {}, 400

        new_user_key = uuid.uuid4().hex
        new_user = User(username=args["username"], key=new_user_key)
        new_user.save()

        user_info = new_user.to_dict()
        user_info["key"] = new_user_key

        return user_info


@user_ns.route("/<int:id>")
class Users(Resource):
    # method_decorators = [require_api_key]

    @user_ns.marshal_with(user_model)
    def get(self, id):
        """
        Gets user by ID, otherwise returns 404.
        """
        user = User.get_by_id(id)

        return user.to_dict()

    @user_ns.marshal_with(user_model)
    @user_ns.expect(post_parser)
    def put(self, id):
        """
        Verifies that no user has given username already and updates all user fields using provided data and returns user data as JSON.
        """
        args = post_parser.parse_args()
        user = User.get_by_id(id)
        possible_user = User.get_from_username(args["username"])

        if possible_user and possible_user.id != user.id:
            return {}, 400

        user.update_from_args(args)

        return user.to_dict()

    @user_ns.marshal_with(user_model)
    @user_ns.expect(get_parser)
    def patch(self, id):
        """
        Verifies that no user has given username already and updates any user fields using provided data and returns user data as JSON.
        """
        args = post_parser.parse_args()
        user = User.get_by_id(id)
        possible_user = User.get_from_username(args["username"])

        if possible_user and possible_user.id != user.id:
            return {}, 400

        user.update_from_args(args)

        return user.to_dict()

    def delete(self, id):
        """
        Deletes user with ID provided from database and returns JSON object with a message indicating it's been deleted and the ID of the user.
        """
        user = User.get_by_id(id)
        db.session.delete(user)
        db.session.commit()

        return {"contents": "user delete", "id": id}
