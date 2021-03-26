from models.device import Device
from models.package import Package
from flask import json
from models.base_model import db
from handlers.create_kafka_topic import create_device_topic
import app

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
    print(data)
