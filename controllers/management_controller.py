from flask import json
from models.base_model import db
from handlers.producer import create_producer
from random import randint
from models.task import Task
from models.device import Device


def install_app(mac, app):
    print(app)
    sequence_number = randint(0, 10000)
    message = {
        'action' : 'install',
        'app' : app,
        'sequence_number' : sequence_number,
        'version' : 'latest',
    }

    task_new = Task(app=app, sequence_number=sequence_number, action='install', done=False, owner = Device.query.filter(Device.mac == mac).first())
    db.session.add(task_new)
    db.session.commit()

    producer = create_producer()
    producer.send(mac.replace(':', '')+'_MANAGEMENT', json.dumps(message).encode('utf-8'))
    del producer

def uninstall_app(mac, app):
    message = {
        'action' : 'uninstall',
        'app' : app,
        'sequence_number' : randint(0, 10000),
        'version' : 'latest',
    }

    producer = create_producer()
    producer.send(mac.replace(':', '')+'_MANAGEMENT', json.dumps(message).encode('utf-8'))
    del producer
