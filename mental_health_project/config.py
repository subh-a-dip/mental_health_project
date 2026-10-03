import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me")
    DEBUG = True
