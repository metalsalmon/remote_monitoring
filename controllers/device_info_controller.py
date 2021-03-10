from models.device import Device
from models.package import Package
from flask import json
from models.base_model import db

def process_msg(self, data):
    device_info = json.loads(data.value.decode("utf-8"))
        #print(device_info)
    with self.app.app_context(): 
        if Device.query.filter_by(mac = device_info["mac"]).first() is None:
            device_new = Device(name=device_info["name"], mac=device_info["mac"], distribution=device_info["distribution"], version=device_info["version"])
            db.session.add(device_new)
            db.session.commit()

            for package in device_info['packages']:
                if Package.query.filter_by(name = package["package"], version = package['version'], owner = device_new).first() is None:
                    print(package)    
                    add_package = Package(name = package['package'], version = package['version'], owner = device_new)    
                    db.session.add(add_package)
                    db.session.commit()
