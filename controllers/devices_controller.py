from models.device import Device
from models.package import Package
from models.task import Task
from flask import json
from models.base_model import db
from handlers.create_kafka_topic import create_device_topic
import app
from ws.events import socketio

def process_msg(self, data):
    device_info = json.loads(data.value.decode("utf-8"))
    with self.app.app_context(): 
        if Device.query.filter_by(mac = device_info["mac"]).first() is None:
            device_new = Device(name=device_info["name"], mac=device_info["mac"], distribution=device_info["distribution"], version=device_info["version"])
            db.session.add(device_new)
            db.session.commit()
            create_device_topic(device_info["mac"])

            for package in device_info['packages']:
                if Package.query.filter_by(name = package["package"], version = package['version'], owner = device_new).first() is None:
                    print(package)    
                    add_package = Package(name = package['package'], version = package['version'], owner = device_new)    
                    db.session.add(add_package)
                    db.session.commit()

def get_devices():
    devices = Device.query.all()
    return json.dumps(
        [item.summary() for item in devices]
    )

def get_device(mac):
    device = Device.query.filter(Device.mac == mac).first()
    return device.summary()

def get_device_packages(mac):
    device = Device.query.filter(Device.mac == mac).first()
    device_packages = Package.query.filter(Package.device_id == device.id)
    
    return json.dumps(
        [item.summary() for item in device_packages]
    )

def process_request_result(self, data):
    with self.app.app_context():
        device = Device.query.filter(Device.mac == data['mac']).first()
        device_task = Task.query.filter(Task.device_id == device.id, Task.done == False, Task.sequence_number == data['sequence_number']).first()
        if device_task is not None: 
            device_task.result = data['result']

            if data['result_code'] == 1000:
                device_task.message = 'already installed'
                socketio.emit('notifications', device_task.app + ': already installed')
            else:         
                device_task.message = data['message']
                device_task.done = True
                if device_task.action == 'install':
                    socketio.emit('notifications', device_task.app + ': successfully installed' if data['result'] == 'success' else ': error')
                elif device_task.action == 'remove':
                    socketio.emit('notifications', device_task.app + ': successfully removed' if data['result'] == 'success' else ': error')
            db.session.commit()

