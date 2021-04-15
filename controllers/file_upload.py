import os
from handlers.producer import create_producer   
from werkzeug.utils import secure_filename
import json

def file_upload(file, type, path): 

    target=os.getenv("UPLOAD_FOLDER")
    if not os.path.isdir(target):
        os.mkdir(target)

    if path == '':
        path = './'

    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)
    print(destination)
    data_send = {'fileDownload' : filename, 'path' : path}
    producer = create_producer()
    producer.send('CONFIG', json.dumps(data_send).encode('utf-8'))
    del producer
    return "ok"