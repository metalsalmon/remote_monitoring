from models.device import Device as Device_db
from models.package import Package as Package_db



def process_msg():
    device_info = json.loads(data.value.decode("utf-8"))
        #print(device_info)

    if Device_db.query.filter_by(mac = device_info["mac"]).first() is None:
        device_new = Device_db(name=device_info["name"], mac=device_info["mac"], distribution=device_info["distribution"], version=device_info["version"])
        db.session.add(device_new)
        db.session.commit()

        for package in device_info['packages']:
            if Package_db.query.filter_by(name = package["package"], version = package['version'], owner = device_new).first() is None:
                print(package)    
                add_package = Package_db(name = package['package'], version = package['version'], owner = device_new)    
                db.session.add(add_package)
                db.session.commit()
