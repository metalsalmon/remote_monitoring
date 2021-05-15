import os
from flask import Flask
from dotenv import load_dotenv


class BaseConfig(object):

    load_dotenv()
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(PROJECT_ROOT)

    SECRET_KEY = os.urandom(24)
    SERVER_HOST = os.getenv('FLASK_RUN_HOST')
    SERVER_PORT = os.getenv('FLASK_RUN_PORT')

    #DB
    DB_STRING = f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASS')}" \
                f"@{os.getenv('DATABASE_IP')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
    SQLALCHEMY_DATABASE_URI = DB_STRING
    SQLALCHEMY_TRACK_MODIFICATIONS = False