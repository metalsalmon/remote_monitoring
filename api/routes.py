from flask import Blueprint, send_from_directory,request
from handlers.producer import create_producer
from dotenv import load_dotenv
load_dotenv()
import os
import logging
from werkzeug.utils import secure_filename
import json
from controllers import monitoring_controller, management_controller


api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/uploads/<filename>', methods=['GET', 'POST'])
def download(filename):
    print("omg")
    print(os.getenv("UPLOAD_FOLDER"))
    print(filename)
    return send_from_directory(os.getenv("UPLOAD_FOLDER"), filename)

@api.route('/upload', methods=['POST'])
def fileUpload():
    target=os.getenv("UPLOAD_FOLDER")
    if not os.path.isdir(target):
        os.mkdir(target)
    
    logger = logging.getLogger('Upload file')
    logger.info("Upload file`")
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)
    print(destination)
    response="ok"
    data_send = {'fileDownload' : filename}
    producer = create_producer()
    producer.send('CONFIG', json.dumps(data_send).encode('utf-8'))
    del producer
    return response

@api.route('/monitoring', methods=['GET'])
def monitoring():
    return monitoring_controller.get_monitoring_data()


@api.route('/management', methods=['POST'])
def management():
    
    data = json.loads(request.data.decode("utf-8"))['formInput']

    if data['action'] == 'install':
        management_controller.install_app(data['package'])
    elif data['action'] == 'remove':
        management_controller.uninstall_app(data['package'])

    
    return "ok"


