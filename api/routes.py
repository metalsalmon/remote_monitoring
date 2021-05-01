from flask import Blueprint, send_from_directory,request
from handlers.producer import create_producer
from dotenv import load_dotenv
load_dotenv()
import os
import logging
from werkzeug.utils import secure_filename
import json
from controllers import monitoring_controller, management_controller
from controllers.devices_controller import get_device, get_devices, get_device_packages, get_tasks, download_agent
from controllers.file_upload import file_upload
from ws.events import socketio

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/uploads/<filename>', methods=['GET', 'POST'])
def download(filename):
    print(os.getenv("UPLOAD_FOLDER"))
    print(filename)
    return send_from_directory(os.getenv("UPLOAD_FOLDER"), filename)

@api.route('/upload', methods=['POST'])
def fileUpload():
    return file_upload(request.files['file'] , request.form['type'], request.form['path'])

@api.route('/monitoring', methods=['GET'])
def monitoring():
    return monitoring_controller.get_monitoring_data()


@api.route('/management', methods=['POST'])
def management():
    
    data = json.loads(request.data.decode("utf-8"))
    print(data)
    action = data['action']
    version = data['version'] if action != 'remove' else ''


    management_controller.manage_app(action, data['mac'], data['package'], version)
    
    return "ok"

@api.route('/devices', methods=['GET'])
def devices():
    return get_devices()

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
    return 'ok'
