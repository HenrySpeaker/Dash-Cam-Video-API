from sqlalchemy.orm import relationship
from .. import db
from ..models.users import User
from ..models.videos import Video


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"))
    video = relationship("Video", back_populates="comments")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", back_populates="comments")
    body = db.Column(db.Text, nullable=False)

    def update_from_args(self, args):
        """
        Updates properties of entry using provided args.
        """
        if args["user_id"]:
            user = User.get_by_id(int(args["user_id"]))
            self.user = user

        if args["video_id"]:
            video = Video.get_by_id(int(args["video_id"]))
            self.video = video

        self.body = args["body"]
        db.session.commit()

    def save(self):
        """
        Saves current video to database.
        """
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """
        Returns a dictionary of data from the given comment.
        """
        comment_dict = {}
        comment_dict["body"] = self.body
        comment_dict["video"] = self.video.url
        comment_dict["user"] = self.user.username
        comment_dict["id"] = self.id

        return comment_dict

    @classmethod
    def get_by_id(cls, id):
        """
        Returns the comment object from the given ID if it exists, otherwise raises a 404 error.
        """
        comment = db.get_or_404(cls, id)

        return comment
