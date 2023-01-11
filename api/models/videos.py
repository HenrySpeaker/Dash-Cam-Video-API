from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from .. import db


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", back_populates="videos")
    comments = relationship("Comment", back_populates="video")
    url = db.Column(db.String(2000), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text)
    city_id = db.Column(db.Integer, db.ForeignKey("city.id"))
    city = relationship("City", back_populates="videos")

    def update_from_args(self, args):
        """
        Updates properties of entry using provided args.
        """
        if "url" in args:
            self.url = args["url"]

        if "date" in args:
            self.date = args["date"]

        if "description" in args:
            self.description = args["description"]

        db.session.commit()

    def save(self):
        """
        Saves current video to database.
        """
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """
        Returns a dictionary of data from the given video.
        """
        video_dict = {}
        video_dict["url"] = self.url
        video_dict["user"] = self.user.username
        video_dict["date"] = str(self.date) if self.date else ""
        video_dict["description"] = self.description if self.description else ""
        video_dict["id"] = self.id
        video_dict["user"] = self.user.username

        return video_dict

    @classmethod
    def get_by_id(cls, id):
        """
        Returns the video object from the given ID if it exists, otherwise raises a 404 error.
        """
        video = db.get_or_404(cls, id)

        return video
