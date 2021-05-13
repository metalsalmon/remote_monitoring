from kafka import KafkaConsumer as kafka_consumer
import threading
from dotenv import load_dotenv
load_dotenv()
import os
from controllers import monitoring_controller, management_controller
from controllers import devices_controller
from models.base_model import db
from models.device import Device
import json
from kafka.admin import KafkaAdminClient, NewTopic
import time
from models.device import Device
from ws.events import socketio

class KafkaClient():
    timers = {}
    def initialize_app(self, app):
        self.app = app

    def register_device_listener(self, mac):
        
        self.register_kafka_listener(f"{mac}_DEVICE_INFO".replace(':',''), self.device_info_listener)

    def register_listeners(self):
        self.register_kafka_listener('MONITORING', self.monitoring_listener)
        self.register_kafka_listener('DEVICE_INFO', self.all_devices_info_listener)
        self.register_kafka_listener('REQUEST_RESULT', self.request_result_listener)
        self.connectivity_regitster()

        devices = Device.query.all()
        for device in devices:
            self.register_kafka_listener(f"{device.mac}_DEVICE_INFO".replace(':',''), self.device_info_listener)

    def create_dynamic_topics(self):
        devices = Device.query.all()

        kafka_admin_client = KafkaAdminClient(
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS')
        )
        
        topics = []
        try:
            for device in devices:
                device.connected = False
                db.session.commit()
                topics.append(NewTopic(name=f"{device.mac}_MANAGEMENT".replace(':',''), num_partitions=1, replication_factor=1))
                topics.append(NewTopic(name=f"{device.mac}_DEVICE_INFO".replace(':',''), num_partitions=1, replication_factor=1))
                topics.append(NewTopic(name=f"{device.mac}_CONFIG".replace(':',''), num_partitions=1, replication_factor=1))
                self.timers[device.mac] = time.monotonic()

            kafka_admin_client.create_topics(new_topics=topics, validate_only=False)

        except Exception as e:
            print("Unable to create topics or topic already exists -> check db")

    def register_kafka_listener(self, topic, listener):

        consumer = kafka_consumer(topic, bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'))
        
        def poll():
            consumer.poll(timeout_ms=int(os.getenv('KAFKA_POOL_TIMEOUT')))
            for msg in consumer:
                listener(msg)
                
        t_kafka = threading.Thread()
        t_kafka._target = poll
        t_kafka.daemon = True
        t_kafka.start()

    def connectivity_regitster(self):
               
        def connectivity():
            while True:
                for item, value in self.timers.items():
                    if time.monotonic() - value > 6:
                        with self.app.app_context():
                            device = Device.query.filter_by(mac = item).first()
                            if device == None:
                                self.timers[item] = time.monotonic()
                            if device.connected == True:
                                device.connected = False
                                db.session.commit()
                                socketio.emit('notifications', device.ip + ' disconnected')          
                time.sleep(2)
    
        t_connectivity = threading.Thread()
        t_connectivity._target = connectivity
        t_connectivity.daemon = True
        t_connectivity.start()

    def monitoring_listener(self, data):
        try:
            monitoring_controller.process_msg(self, data)
        except:
            print("Non registred device") 

    def all_devices_info_listener(self, data):
        devices_controller.all_devices_info(self, data)

    def device_info_listener(self, data):
        device_info = json.loads(data.value.decode("utf-8"))
        for item, value in self.timers.items():
            if item ==  device_info["mac"]:
                self.timers[item] = time.monotonic()
                with self.app.app_context():
                    device = Device.query.filter_by(mac = item).first()
                    if device != None and device.connected == False:
                        device.connected = True
                        db.session.commit()
                        socketio.emit('notifications', device.ip + ' connected')

        devices_controller.device_info(self, data)
        
    def device_config_listener(self, data):
        devices_controller.device_config(self, data)

    def request_result_listener(self, data):
        devices_controller.process_request_result(self, json.loads(data.value.decode("utf-8")))
    