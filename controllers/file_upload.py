import os
from handlers.producer import producer   
from werkzeug.utils import secure_filename
import json
from models.group import Group
from models.device import Device
import time

def file_upload(file, type, path, mac): 

    target=os.getenv("UPLOAD_FOLDER")
    if not os.path.isdir(target):
        os.mkdir(target)

    if path == '':
        path = './'

    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)
    print(destination)
    data_send = {'fileDownload' : filename, 'location' : os.getenv('SERVER_IP')+'/api/uploads/', 'path' : path}
    producer.send(mac.replace(':', '')+'_CONFIG', data_send)

def group_file_upload(file, file_type, path, group_name):
    print(group_name)
    group = Group.query.filter(Group.name == group_name).first()

    target=os.getenv("UPLOAD_FOLDER")
    if not os.path.isdir(target):
        os.mkdir(target)

    if path == '':
        path = './'

    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)
    
    for device in Device.query.filter(Device.owner == group).all():
        data_send = {'fileDownload' : filename, 'location' : os.getenv('SERVER_IP')+'/api/uploads/', 'path' : path}
        producer.send(device.mac.replace(':', '')+'CONFIG', data_send)