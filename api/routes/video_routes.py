from ..models.videos import Video
from ..models.users import User
from ..models.cities import City
from .. import video_ns
from flask_restx import Resource, fields, reqparse, inputs
from .. import db, api
from ..utils.url import verify_youtube_url
from ..utils.APIKEY.require_key import require_api_key


get_parser = reqparse.RequestParser()
get_parser.add_argument("url", required=False,
                        type=inputs.URL(schemes=["http", "https"], domains=["youtube.com", "www.youtube.com"]))
get_parser.add_argument("date", required=False,
                        type=inputs.date_from_iso8601, help="date should be iso8601")

patch_parser = get_parser.copy()
patch_parser.add_argument("description", required=False)

post_parser = patch_parser.copy()
post_parser.add_argument("user_id", required=True, type=int)
post_parser.replace_argument("url", required=True,
                             type=inputs.URL(schemes=["http", "https"], domains=["youtube.com", "www.youtube.com"]))

video_model = api.model("Video", {
    "url": fields.String(description="The url of the video"),
    "id": fields.Integer(description="ID of video."),
    "description": fields.String(description="Optional description of the video"),
    "city": fields.String(description="Optional city where video was taken"),
    "user": fields.String(description="The username of the uploader"),
    "date": fields.String(description="Date when video occurred in iso8601 format")

})


@video_ns.route("/")
class VideoList(Resource):
    @video_ns.marshal_list_with(video_model)
    @video_ns.expect(get_parser)
    def get(self):
        """
        If url is provided, searches for video with that url and returns it as a JSON object in a list.
        Otherwise, if a date is provided, searches for all videos with provided date as a property and returns their data as JSON objects in a list.
        Otherwise, returns all videos' data as JSON objects in a list.
        """
        args = get_parser.parse_args()

        if args["url"]:
            video = db.session.execute(
                db.select(Video).filter_by(url=args["url"])).first()

            if video:
                return [video[0].to_dict()]

            return [], 404

        if args["date"]:
            videos = db.session.execute(
                db.select(Video).filter_by(date=args["date"])).all()

            if not videos:
                return {}, 404

            video_list_json = [video[0].to_dict() for video in videos]

            return video_list_json

        video_list = db.session.execute(db.select(Video)).all()
        video_list_json = [video[0].to_dict() for video in video_list]

        return video_list_json

    @video_ns.marshal_with(video_model)
    @video_ns.expect(post_parser)
    def post(self):
        """
        Verifies that url provided is valid, and if so, creates a new video in database associated with the user whose ID was provided.
        Returns a JSON object containing the data of the entry created in database.
        """
        args = post_parser.parse_args()

        if not verify_youtube_url(args['url']):
            return {}, 400

        user = User.get_by_id(args["user_id"])
        new_video = Video(
            url=args["url"], user=user, date=args["date"], description=args["description"])
        new_video.save()

        return new_video.to_dict()


@video_ns.route("/<int:id>")
class Videos(Resource):
    method_decorators = [require_api_key]

    @video_ns.marshal_with(video_model)
    def get(self, id):
        """
        Returns JSON of data from video whose ID was specified.
        """
        video = Video.get_by_id(id)

        return video.to_dict()

    @video_ns.marshal_with(video_model)
    @video_ns.expect(post_parser)
    def put(self, id):
        """
        Updates all video fields using provided data and returns comment data as JSON.
        """
        video = Video.get_by_id(id)
        args = post_parser.parse_args()

        if not verify_youtube_url(args['url']):
            return {}, 400

        video.update_from_args(args)

        return video.to_dict()

    @video_ns.marshal_with(video_model)
    @video_ns.expect(patch_parser)
    def patch(self, id):
        """
        Updates any video fields using provided data and returns comment data as JSON.
        """
        args = patch_parser.parse_args()

        if not verify_youtube_url(args['url']):
            return {}, 400

        video = Video.get_by_id(id)
        video.update_from_args(args)

        return video.to_dict()

    def delete(self, id):
        """
        Deletes video with ID provided from database and returns JSON object with a message indicating it's been deleted and the ID of the video.
        """
        video = Video.get_by_id(id)
        db.session.delete(video)
        db.session.commit()

        return {"contents": "video delete", "id": id}
