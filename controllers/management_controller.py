from flask import json
from models.base_model import db
from handlers.producer import create_producer
from models.task import Task
from models.device import Device

def manage_app(action, mac, app, version):
    
    task_new = Task(app=app, action=action, done=False, owner = Device.query.filter(Device.mac == mac).first())
    db.session.add(task_new)
    db.session.commit()

    message = {
        'action' : action,
        'app' : app,
        'sequence_number' : task_new.id,
        'version' : 'latest' if version == '' else version,
    }


    producer = create_producer()
    producer.send(mac.replace(':', '')+'_MANAGEMENT', json.dumps(message).encode('utf-8'))
    del producer
