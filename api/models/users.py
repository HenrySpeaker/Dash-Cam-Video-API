from sqlalchemy.orm import relationship
from sqlalchemy.exc import NoResultFound
from ..models.videos import Video
from .. import db
from werkzeug.security import generate_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    videos = relationship("Video", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    username = db.Column(db.String(20), unique=True)
    hashed_key = db.Column(db.String(80))

    def __init__(self, username, key):
        self.username = username
        self.hashed_key = generate_password_hash(
            key, method="pbkdf2:sha256", salt_length=8)

    def update_from_args(self, args):
        """
        Updates properties of entry using provided args.
        """
        if "username" in args:
            self.username = args["username"]

        db.session.commit()

    def save(self):
        """
        Saves current user to database.
        """
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """
        Returns a dictionary of data from the given user.
        """
        user_dict = {}
        user_dict["username"] = self.username
        user_dict["id"] = self.id
        user_videos = db.session.execute(
            db.select(Video).filter_by(user=self)).all()
        user_dict["videos"] = [video[0].to_dict()
                               for video in user_videos]

        return user_dict

    @classmethod
    def get_by_id(cls, id):
        """
        Returns the user object from the given ID if it exists, otherwise raises a 404 error.
        """
        user = db.get_or_404(cls, id)

        return user

    @classmethod
    def get_from_username(cls, username):
        """
        Returns the user object with given username if it exists, otherwise returns None.
        """
        try:
            user = db.session.execute(
                db.select(User).filter_by(username=username)).one()[0]
            return user

        except NoResultFound:
            return None
