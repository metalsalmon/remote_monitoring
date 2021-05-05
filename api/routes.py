from flask import Blueprint, send_from_directory,request
from handlers.producer import create_producer
from dotenv import load_dotenv
load_dotenv()
import os
import logging
from werkzeug.utils import secure_filename
import json
from controllers import monitoring_controller, management_controller
from controllers.devices_controller import get_device, get_devices, get_device_packages, get_tasks, download_agent, get_groups, add_group, add_to_group, update_group, delete_group, get_group_devices, get_group_packages
from controllers.file_upload import file_upload, group_file_upload
from ws.events import socketio


api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/uploads/<filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(os.getenv("UPLOAD_FOLDER"), filename)

@api.route('/upload/<mac>', methods=['POST'])
def fileUpload(mac):
    file_upload(request.files['file'] , request.form['type'], request.form['path'], mac)
    return '', 200

@api.route('/groupUpload/<group>', methods=['POST'])
def groupUpload(group):
    group_file_upload(request.files['file'] , request.form['type'], request.form['path'], group)
    return '', 200

@api.route('/monitoring', methods=['GET'])
def monitoring():
    return monitoring_controller.get_monitoring_data()

@api.route('/monitoring2', methods=['GET'])
def monitoring2():
    return monitoring_controller.get_graph_monitoring_data()


@api.route('/management', methods=['POST'])
def management():
    
    data = json.loads(request.data.decode("utf-8"))
    print(data)
    action = data['action']
    version = data['version'] if action != 'remove' else ''


    management_controller.manage_app(action, data['mac'], data['package'], version)
    
    return '', 200

@api.route('/devices', methods=['GET'])
def devices():
    return get_devices()

@api.route('/groups', methods=['GET', 'POST'])
def groups():
    if request.method == 'POST':
        data = json.loads(request.data.decode("utf-8"))
        print(data)
        if data['action'] == 'Add':
            add_group(data['name'])
        elif data['action'] == 'Update':
            update_group(data['name'], data['old_name'])
        elif data['action'] == 'Delete':
            delete_group(data['name'])

        return '', 200
    else:   
        return get_groups()

@api.route('/tasks', methods=['GET'])
def tasks():
    return get_tasks()

@api.route('/device/<mac>', methods=['GET'])
def device(mac):
    return get_device(mac)

@api.route('/packages/<mac>')
def packages(mac):
    
    return get_device_packages(mac)

@api.route('/downloadAgent', methods=['GET', 'POST'])
def uploadAgent():
    data = json.loads(request.data.decode("utf-8"))
    download_agent(data['ip'], data['username'], data['sshPass'], data['sudoPass'], data['os'])
    return '', 200

@api.route('/addToGroup', methods=['POST'])
def addToGroup():
    print(request.data)
    data = json.loads(request.data.decode("utf-8"))
    add_to_group(data['mac'], data['name'])
    return '', 200

@api.route('/groupDevices/<group>', methods=['GET'])
def groupDevices(group):
    return get_group_devices(group)

@api.route('/groupPackages/<group>', methods=['GET'])
def groupPackages(group):
    return get_group_packages(group)

@api.route('/groupManagement', methods=['POST'])
def groupManagement():
    data = json.loads(request.data.decode("utf-8"))
    action = data['action']
    version = data['version'] if action != 'remove' else ''
    management_controller.manage_group_app(action, data['group'], data['package'], version)
    return '', 200
