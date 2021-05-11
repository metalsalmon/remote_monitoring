from models.device import Device
from models.package import Package
from models.task import Task
from models.group import Group
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


def all_devices_info(self, data):
    device_info = json.loads(data.value.decode("utf-8"))
    with self.app.app_context(): 
        device = Device.query.filter_by(mac = device_info["mac"]).first()
        if device is None:
            device_new = Device(name=device_info['name'], ip=device_info['ip'], mac=device_info['mac'], distribution=device_info['distribution'], version=device_info['version'], connected = True)
            db.session.add(device_new)
            db.session.commit()
            create_device_topic(device_info['mac'])
            socketio.emit('notifications', 'new device added')


def device_info(self, data):
    device_info = json.loads(data.value.decode("utf-8"))
    if 'alive' not in device_info:
        with self.app.app_context(): 
            device = Device.query.filter_by(mac = device_info["mac"]).first()
            if device is None:
                device_new = Device(name=device_info['name'], ip=device_info['ip'], mac=device_info['mac'], distribution=device_info['distribution'], version=device_info['version'], connected = True)
                db.session.add(device_new)
                db.session.commit()
                create_device_topic(device_info['mac'])

                for package in device_info['packages']:
                    #print(package)
                    if Package.query.filter_by(name = package['package'], owner = device_new).first() is None:  
                        add_package = Package(name = package['package'], version = package['version'], latest_version = package['latest_version'], owner = device_new)    
                        db.session.add(add_package)
                        db.session.commit()
            else:
                for package in device_info['packages']:
                    #print(package)
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

def get_groups():
    groups = Group.query.all()
    return json.dumps(
        [item.summary() for item in groups]
    )

def get_tasks():
    tasks = Task.query.order_by(Task.id).all()
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

def send_notification(ip, msg):
    socketio.emit('notifications',ip + " -> " + msg)    

def process_request_result(self, data):
    with self.app.app_context():
        device = Device.query.filter(Device.mac == data['mac']).first()
        device_task = Task.query.filter(Task.device_id == device.id, Task.done == False, Task.id == data['sequence_number']).first()
        if device_task is not None: 
            device_task.result =  'sucess' if data['result_code'] == 0 or data['result_code'] == 1000  else 'error'
            device_task.message = data['message']
            device_task.done = True
            device_task.state = 'finished'
            device_task.finished = db.func.now()

            if device_task.action == 'install':            
                if data['result_code'] == 0:
                    add_package = Package(name = device_task.app, version = data['version'], latest_version = data['latest_version'], owner = device)
                    db.session.add(add_package)
                    db.session.commit()  
                    send_notification(device.ip, device_task.app + ': successfully installed')
                elif data['result_code'] == 1000:
                    device_task.message = 'already installed'
                    send_notification(device.ip, device_task.app + ': already installed')
                else:
                    send_notification(device.ip, device_task.app + ': unable to install')

            elif device_task.action == 'remove':
                if data['result_code'] == 0:
                    Package.query.filter(Package.name == device_task.app).delete()
                    send_notification(device.ip, device_task.app + ': successfully removed')
                elif data['result_code'] == 1000:
                    device_task.message = 'is not installed'
                    send_notification(device.ip, device_task.app + ': is not installed')
                else:
                    send_notification(device.ip, device_task.app + ': unable to remove')

            elif device_task.action == 'update':
                if data['result_code'] == 0:
                    package = Package.query.filter(Package.name == device_task.app).first()
                    if package is not None:
                        package.version = data['version']
                        package.latest_version = data['latest_version']
                        send_notification(device.ip, device_task.app + ': successfully updated'+ data['version'])
                elif data['result_code'] == 1000:
                    device_task.message = 'is not installed'
                    send_notification(device.ip, device_task.app + ': is not installed')
            elif device_task.action == 'Update all':
                if data['result_code'] == 0:
                    send_notification(device.ip, 'successfull update')
                else:
                    send_notification(device.ip, 'unsuccessfull update')
            elif device_task.action == 'file upload':
                if data['result_code'] == 0:
                    send_notification(device.ip, 'file successfully uploaded')
                elif data['result_code'] == 1111:
                    send_notification(device.ip, 'unable to execute the script')

                else:
                    send_notification(device.ip, 'unsuccessfull file upload')

            db.session.commit()

def add_group(group_name):
        group = Group(name=group_name)
        db.session.add(group)
        db.session.commit()

def add_to_group(mac, group_name):
    if group_name == '':
        device = Device.query.filter(Device.mac == mac).first()
        device.owner = None
    else:
        device = Device.query.filter(Device.mac == mac).first()
        device.owner = Group.query.filter(Group.name == group_name).first()
        db.session.commit()
    
    db.session.commit()

def remove_from_group(mac, group_name):
    device = Device.query.filter(Device.mac == mac).first()
    device.owner = None
    db.session.commit()
    send_notification(device.ip, 'removed from '+ group_name)

def update_group(group_name, old_group_name):
    group = Group.query.filter(Group.name == old_group_name).first()
    group.name = group_name
    db.session.commit()
    
def delete_group(group_name):
    Group.query.filter(Group.name == group_name).delete()
    db.session.commit()

def get_group_devices(group_name):
    group = Group.query.filter(Group.name == group_name).first()
    group_devices = Device.query.filter(Device.owner == group).all()

    return json.dumps(
        [item.summary() for item in group_devices]
    )

def get_group_packages(group_name):
    group = Group.query.filter(Group.name == group_name).first()
    group_devices = Device.query.filter(Device.owner == group).all()
    packages = []
    
    for device in group_devices:
        packages += Package.query.filter(Package.owner == device)

    return json.dumps(
        list({v['name']:v for v in [item.summary() for item in packages]}.values())
    )

def download_agent(ip, username, ssh_password, sudo_password, agent_os):
    try:
        remote_location = '/home/' + username + '/' + os.getenv("AGENT_NAME")
        remote_config_location = '/home/' + username + '/' + 'config.json'

        if os.getenv('CUSTOM_REMOTE_LOCATION') == 'TRUE':
            remote_location= os.getenv('REMOTE_AGENT_LOCATION')+'/' + os.getenv("AGENT_NAME")
            remote_config_location= os.getenv('REMOTE_AGENT_LOCATION')+'/' + 'config.json'       
        
        run_agent = "sudo -S -p '' %s" % remote_location
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=ssh_password)
        sftp = ssh.open_sftp()
        
        sftp.put(os.getenv('AGENT_LOCATION'), remote_location)
        sftp.put(os.getenv('AGENT_CONFIG_LOCATION'), remote_config_location)
        sftp.close()

        ssh.exec_command("chmod +x " +remote_location)
        stdin, stdout, stderr = ssh.exec_command(command=run_agent)
        stdin.write(sudo_password + "\n")
        stdin.flush()
        ssh.close()

    except Exception as e:
        stdin, stdout, stderr = ssh.exec_command(command=run_agent)
        stdin.write(sudo_password + "\n")
        stdin.flush()
        ssh.close()
        send_notification(ip, 'unable to download')
        print(e)

            