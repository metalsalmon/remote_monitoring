import os
from handlers.producer import producer   
from werkzeug.utils import secure_filename
import json
from models.group import Group
from models.device import Device
from models.task import Task
from models.base_model import db
import time

def file_upload(file, file_type, path, mac): 

    target='./UploadedFiles'
    if not os.path.isdir(target):
        os.mkdir(target)

    if path == '':
        path = './'        

    filename = secure_filename(file.filename)
    
    device = Device.query.filter(Device.mac == mac).first()
    task_new = Task(ip=device.ip, app=filename, action='file upload', done=False, state='sent to the device' , owner = device)
    db.session.add(task_new)
    db.session.commit()


    if file_type == 'script':
        path = './'
        filename = 'script'

    destination="/".join([target, filename])
    file.save(destination)

    data_send = {'fileDownload' : filename, 'location' : os.getenv('SERVER_IP')+'/api/uploads/', 'path' : path, 'type' : file_type, 'sequence_number' : task_new.id} 
    print(data_send)
    producer.send(mac.replace(':', '')+'_CONFIG', data_send)
    task_new.task_message = data_send
    db.session.commit()

def group_file_upload(file, file_type, path, group_name):

    group = Group.query.filter(Group.name == group_name).first()

    target=os.getenv("UPLOAD_FOLDER")
    if not os.path.isdir(target):
        os.mkdir(target)

    if path == '':
        path = './'
    filename = secure_filename(file.filename)
    
    if file_type == 'script':
        path = './'
        filename = 'script'

    destination="/".join([target, filename])
    file.save(destination)
    
    for device in Device.query.filter(Device.owner == group).all():
        task_new = Task(ip=device.ip, app=filename, action='file upload', done=False, state='sent to the device' , owner = device)
        db.session.add(task_new)
        db.session.commit()
        data_send = {'fileDownload' : filename, 'location' : os.getenv('SERVER_IP')+'/api/uploads/', 'path' : path, 'type' : file_type, 'sequence_number' : task_new.id}
        producer.send(device.mac.replace(':', '')+'_CONFIG', data_send)
        task_new.data_send = data_send
        db.session.commit()