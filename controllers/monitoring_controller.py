from models.device import Device
from models.monitoring import Monitoring
from sqlalchemy import desc
from flask import jsonify
from flask import json
from models.base_model import db

def get_monitoring_data():
    monitoring_response = []

    devicess = Device.query.all()

    for devic in devicess:
        
        monitoring_row = Monitoring.query.filter_by(device_id = devic.id).order_by(desc(Monitoring.id)).limit(1).first().summary(devic.name)
        
        if monitoring_row is not None:
            monitoring_response.append(monitoring_row)
        print(monitoring_response)

    return jsonify({"data": monitoring_response})

def process_msg(self, data):
    data = json.loads(data.value.decode("utf-8"))
    print(data)
    with self.app.app_context():   
        monitoring_new = Monitoring(time=data["time"], cpu_usage=data["cpu_usage"], ram_usage=data["ram_usage"], disk_space=data["disk_space"], used_disk_space=data["used_disk_space"], owner = Device.query.filter(Device.mac == data["mac"]).first())
        db.session.add(monitoring_new)
        db.session.commit()