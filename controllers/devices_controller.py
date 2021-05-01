from models.device import Device
from models.package import Package
from models.task import Task
from flask import json
from models.base_model import db
from handlers.create_kafka_topic import create_device_topic
import app
from ws.events import socketio
import subprocess
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import os


def process_msg(self, data):
    device_info = json.loads(data.value.decode("utf-8"))
    with self.app.app_context(): 
        device = Device.query.filter_by(mac = device_info["mac"]).first()
        if device is None:
            device_new = Device(name=device_info['name'], ip=device_info['ip'], mac=device_info['mac'], distribution=device_info['distribution'], version=device_info['version'])
            db.session.add(device_new)
            db.session.commit()
            create_device_topic(device_info['mac'])

            for package in device_info['packages']:
                if Package.query.filter_by(name = package['package'], owner = device_new).first() is None:
                    #print(package)    
                    add_package = Package(name = package['package'], version = package['version'], latest_version = package['latest_version'], owner = device_new)    
                    db.session.add(add_package)
                    db.session.commit()
        else:
            for package in device_info['packages']:
                print(package)
                db_package = Package.query.filter_by(name = package['package'], owner = device).first()
                if db_package is None:
                    add_package = Package(name = package['package'], version = package['version'], latest_version = package['latest_version'], owner = device)    
                    db.session.add(add_package)
                    db.session.commit()
                else:
                    db_package.version = package['version']
                    db_package.latest_version = package['latest_version']
                    db.session.commit()


def get_devices():
    devices = Device.query.all()
    return json.dumps(
        [item.summary() for item in devices]
    )

def get_tasks():
    tasks = Task.query.all()
    return json.dumps(
        [item.summary() for item in tasks]
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

def download_agent(ip, username, ssh_password, sudo_password, agent_os):
    try:
        code = subprocess.run(['sudo', 'sshpass' , '-p' , sudo_password , 'scp', os.getenv('AGENT_LOCATION'), username + '@' + ip + ':' + os.getenv('REMOTE_AGENT_LOCATION') + os.getenv("AGENT_NAME")])

        if code.returncode == 0:
            agent_location = os.getenv('REMOTE_AGENT_LOCATION') + os.getenv("AGENT_NAME")
            command = "sudo -S -p '' %s" % agent_location
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=ssh_password)
            stdin, stdout, stderr = ssh.exec_command(command=command)
            stdin.write(sudo_password + "\n")
            stdin.flush()

    except Exception as e:
        print(e)

def process_request_result(self, data):
    with self.app.app_context():
        device = Device.query.filter(Device.mac == data['mac']).first()
        device_task = Task.query.filter(Task.device_id == device.id, Task.done == False, Task.id == data['sequence_number']).first()
        if device_task is not None: 
            device_task.result =  'sucess' if data['result_code'] == 0  else 'error'

            if data['result_code'] == 1000:
                device_task.message = 'already installed'
                socketio.emit('notifications', device_task.app + ': already installed')
                device_task.done = True
            else:        
                device_task.message = data['message']
                device_task.done = True
                if device_task.action == 'install':
                    if data['result_code'] == 0:
                        add_package = Package(name = device_task.app, version = data['version'], owner = device)
                        db.session.add(add_package)
                        db.session.commit()  
                    socketio.emit('notifications', device_task.app + ': successfully installed' if data['result_code'] == 0 else ': error ' + str(data['result_code']))
                elif device_task.action == 'remove':
                    if data['result_code'] == 0:
                        Package.query.filter(Package.name == device_task.app).delete()
                    socketio.emit('notifications', device_task.app + ': successfully removed' if data['result_code'] == 0 else ': error ' + str(data['result_code']))
                elif device_task.action == 'update':
                    if data['result_code'] == 0:
                        package = Package.query.filter(Package.name == device_task.app)
                        if package is not None:
                            package.version = data['version']
                            db.session.commit()
                            socketio.emit('notifications', device_task.app + ': successfully updated'+ data['version'] if data['result_code'] == 0 else ': error ' + str(data['result_code']))

            db.session.commit()

