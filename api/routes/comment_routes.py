from ..models.comments import Comment
from ..models.videos import Video
from ..models.users import User
from .. import comment_ns
from flask_restx import Resource, reqparse, fields
from .. import db, api
from ..utils.apikey import require_api_key


get_parser = reqparse.RequestParser()
get_parser.add_argument("user_id", required=False, type=int)
get_parser.add_argument("video_id", required=False, type=int)

patch_parser = get_parser.copy()
patch_parser.add_argument("body", required=True)

post_parser = patch_parser.copy()
post_parser.replace_argument("user_id", required=True, type=int)
post_parser.replace_argument("video_id", required=True, type=int)

comment_model = api.model("Comment", {
    "body": fields.String,
    "user": fields.String,
    "video": fields.String,
    "id": fields.Integer
})


@comment_ns.route("/")
class CommentList(Resource):
    @comment_ns.marshal_list_with(comment_model)
    @comment_ns.expect(get_parser)
    def get(self):
        """
        First checks parser for any video id, and if none exists, checks if any user id exists. 
        If either do exist, any comments that pertain to that id are returned as a list. 
        Otherwise, all comments for all videos are returned as a list.
        """
        args = get_parser.parse_args()

        if args["video_id"]:
            video = Video.get_by_id(int(args["video_id"]))
            comments = video.comments
            comments_list = [comment.to_dict() for comment in comments]

        elif args["user_id"]:
            user = User.get_by_id(int(args["user_id"]))
            comments_list = [comment.to_dict() for comment in user.comments]

        else:
            comments = db.session.execute(db.select(Comment)).all()
            comments_list = [comment[0].to_dict() for comment in comments]

        return comments_list

    @comment_ns.marshal_with(comment_model)
    @comment_ns.expect(post_parser)
    def post(self):
        """
        Creates a new comment with data provided in post and then returns the comment data as JSON.
        """
        args = post_parser.parse_args()
        user = User.get_by_id(int(args["user_id"]))
        video = Video.get_by_id(int(args["video_id"]))
        new_comment = Comment(user=user, video=video, body=args["body"])
        new_comment.save()

        return new_comment.to_dict()


@comment_ns.route("/<int:id>")
class Comments(Resource):
    method_decorators = [require_api_key]

    @comment_ns.marshal_with(comment_model)
    def get(self, id):
        """
        Looks for comment with given ID, returns JSON data of the comment if it exists, and a 404 error otherwise.
        """
        comment = Comment.get_by_id(id)

        return comment.to_dict()

    @comment_ns.marshal_with(comment_model)
    @comment_ns.expect(post_parser)
    def put(self, id):
        """
        Updates all comment fields using provided data and returns comment data as JSON.
        """
        args = post_parser.parse_args()
        comment = Comment.get_by_id(id)
        comment.update_from_args(args)

        return comment.to_dict()

    @comment_ns.marshal_with(comment_model)
    @comment_ns.expect(patch_parser)
    def patch(self, id):
        """
        Updates any comment fields using provided data and returns comment data as JSON.
        """
        args = patch_parser.parse_args()
        comment = Comment.get_by_id(id)
        comment.update_from_args(args)

        return comment.to_dict()

    def delete(self, id):
        """
        Deletes comment with ID provided from database and returns JSON object with a message indicating it's been deleted and the ID of the comment.
        """
        comment = Comment.get_by_id(id)
        db.session.delete(comment)
        db.session.commit()

        return {"contents": "comment delete", "id": id}
