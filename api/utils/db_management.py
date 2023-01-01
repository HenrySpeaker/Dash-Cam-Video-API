from .. import app, db


def db_cleanup():
    """
    Clears all contents from database.
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()
