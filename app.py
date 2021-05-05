from flask import Flask, flash, request, redirect, url_for, session
import os
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
from api.routes import api
from models.base_model import initialize_db
from handlers.kafka_client import initialize_kafka
from api.errors import register_error_handlers
from settings import base_config
from ws.events import socketio

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(base_config.BaseConfig)
    initialize_db(app)
    
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        CORS(app)

        register_error_handlers(app)

        app.register_blueprint(api)

        initialize_kafka(app)

        socketio.init_app(app)

    return app
