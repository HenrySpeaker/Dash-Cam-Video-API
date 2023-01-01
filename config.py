from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Set Flask config variables."""
    RESTX_MASK_SWAGGER = False


class ProdConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = environ.get("PROD_DATABASE_URI")


class DevConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get("DEV_DATABASE_URI")
