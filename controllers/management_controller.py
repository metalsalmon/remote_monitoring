from flask import json
from models.base_model import db
from handlers.producer_in import kafka_producer
from models.task import Task
from models.device import Device
from models.group import Group
import time

def manage_app(action, mac, app, version):
    
    task_new = Task(ip=Device.query.filter(Device.mac == mac).first().ip, app=app, action=action, done=False, state='sent to the device' , owner = Device.query.filter(Device.mac == mac).first())
    db.session.add(task_new)
    db.session.commit()

    message = {
        'action' : action,
        'app' : app,
        'sequence_number' : task_new.id,
        'version' : 'latest' if version == '' else version,
    }

    task_new.task_message = message
    db.session.commit()

    kafka_producer.producer.send(mac.replace(':', '')+'_MANAGEMENT', message)

def manage_group_app(action, group_name, package, version):
    group = Group.query.filter(Group.name == group_name).first()
    group_devices = Device.query.filter(Device.owner == group).all()
    
    for device in group_devices:
        manage_app(action, device.mac, package, version)

def update_all(mac):
    task_new = Task(ip=Device.query.filter(Device.mac == mac).first().ip, action='Update all', done=False, owner = Device.query.filter(Device.mac == mac).first())
    db.session.add(task_new)
    db.session.commit()

    message = {
        'action' : 'update_all',
        'sequence_number' : task_new.id
    }

    kafka_producer.producer.send(mac.replace(':', '')+'_MANAGEMENT', message)

def reboot(mac):
    device = Device.query.filter(Device.mac == mac).first()
    task_new = Task(ip=device.ip, action='reboot', done=True, state='sent to the device' , owner = device)
    db.session.add(task_new)
    db.session.commit()

    data_send = {'reboot' : mac} 
    kafka_producer.producer.send(mac.replace(':', '')+'_CONFIG', data_send)
    task_new.task_message = data_send
    db.session.commit()

def reboot_group(group_name):
    group = Group.query.filter(Group.name == group_name).first()
    group_devices = Device.query.filter(Device.owner == group).all()
    
    for device in group_devices:
        reboot(device.mac)
