from models.device import Device
from models.monitoring import Monitoring
from sqlalchemy import desc
from flask import jsonify
from flask import json
from models.base_model import db
from models.task import Task

def get_monitoring_data():
    monitoring_response = []

    devicess = Device.query.all()

    for devic in devicess:
        
        monitoring_row = Monitoring.query.filter_by(device_id = devic.id).order_by(desc(Monitoring.id)).limit(1).first()
        
        if monitoring_row is not None:
            monitoring_row = monitoring_row.summary(devic.name, devic.ip)
            monitoring_response.append(monitoring_row)

    return jsonify({"data": monitoring_response})

def get_graph_monitoring_data():
    monitoring_response = []
    monitor_group = []
    devicess = Device.query.all()

    for devic in devicess:
        
        monitoring_group = Monitoring.query.filter_by(device_id = devic.id).order_by(desc(Monitoring.id)).limit(10).all()

        print(monitoring_group)
        if monitoring_group is not None:
            for row in monitoring_group:
                print(row.summary(devic.name))
                monitor_group.insert(0, row.summary(devic.name))
            
            monitoring_response.append(monitor_group)
            monitor_group = []

    return jsonify({"data": monitoring_response})

def process_msg(self, data):
    data = json.loads(data.value.decode("utf-8"))
    with self.app.app_context():  
        try: 
            if data['cpu_temp'] > 95:
                message = '[{}] Cpu temperature {}°C'.format(data["time"], data['cpu_temp'])
                store_alert(message, data)
            if data["ram_usage"] > 95:
                message = '[{}] RAM usage {}%'.format(data["time"], data['ram_usage'])
                store_alert(message, data)
            if data["cpu_usage"] > 98:
                message = '[{}] CPU usage {}%'.format(data["time"], data['ram_usage'])
                store_alert(message, data)
            if data["disk_space"] - data['used_disk_space'] < 0.2:
                message = '[{}] Less than {} GB free space remaining'.format(data["time"], round((data["disk_space"] - data['used_disk_space']), 4))
                store_alert(message, data)
                
        except Exception as e:
            print(e)

        monitoring_new = Monitoring(time=data["time"], cpu_usage=data["cpu_usage"], ram_usage=data["ram_usage"], disk_space=data["disk_space"], used_disk_space=data["used_disk_space"],cpu_temp=data['cpu_temp'], owner = Device.query.filter(Device.mac == data["mac"]).first())
        db.session.add(monitoring_new)
        db.session.commit()

def store_alert(message, data):
    device = Device.query.filter(Device.mac == data["mac"]).first()
    task_new = Task(ip=device.ip, action='ALERT', done=True, state='reported', message = message, owner = device)
    db.session.add(task_new)
    db.session.commit()