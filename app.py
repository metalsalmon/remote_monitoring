from flask import Flask, flash, request, redirect, url_for, session
import os
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
from api.routes import api
from models.base_model import initialize_db
from handlers.listeners import KafkaClient
from api.errors import register_error_handlers
from settings import base_config

def create_app():
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object(base_config.BaseConfig)

    CORS(app)

    register_error_handlers(app)

    app.register_blueprint(api)
    
    initialize_db(app)

    kafka_client = KafkaClient(app)
    kafka_client.register_listeners()
    kafka_client.create_dynamic_topics()

    return app
