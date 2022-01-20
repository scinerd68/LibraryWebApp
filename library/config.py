import os


class Config:
    SECRET_KEY = os.environ.get("LIBRARY_WEB_APP")
    SQLALCHEMY_DATABASE_URI = os.environ.get("LIBRARY_DB")
