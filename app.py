from flask import Flask, flash, request, redirect, url_for, session
import os
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
from api.routes import api
from models.base_model import initialize_db
from handlers.listeners import KafkaConsumer
from api.errors import register_error_handlers

def create_app():
    app = Flask(__name__, instance_relative_config=False)

    CORS(app)

    app.secret_key = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_CONNECTION")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #app.config['FLASK_ENV'] = True

    register_error_handlers(app)

    app.register_blueprint(api)
    
    initialize_db(app)

    omg = KafkaConsumer(app)
    omg.register_listeners()

    return app

app = create_app()
