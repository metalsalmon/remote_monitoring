from flask import json
from models.base_model import db
from handlers.producer import create_producer
from random import randint


def install_app(app):
    print(app)
    message = {
        'action' : 'install',
        'app' : app,
        'sequence_number' : randint(0, 10000),
        'version' : 'latest',
    }

    producer = create_producer()
    producer.send('b827ebaf96a1_MANAGEMENT', json.dumps(message).encode('utf-8'))
    del producer

def uninstall_app(app):
    message = {
        'action' : 'uninstall',
        'app' : app,
        'sequence_number' : randint(0, 10000),
        'version' : 'latest',
    }

    producer = create_producer()
    producer.send('b827ebaf96a1_MANAGEMENT', json.dumps(message).encode('utf-8'))
    del producer
