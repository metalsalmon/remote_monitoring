from kafka import KafkaConsumer as kafka_consumer
import threading
from dotenv import load_dotenv
load_dotenv()
import os
from controllers import monitoring_controller
from controllers import devices_controller
from models.base_model import db
from models.device import Device
import json
from kafka.admin import KafkaAdminClient, NewTopic

class KafkaClient(object):

    def __init__(self, app):
        self.app = app


    def register_listeners(self):
        self.register_kafka_listener('MONITORING', self.monitoring_listener)
        self.register_kafka_listener('DEVICE_INFO', self.device_info_listener)

    def create_dynamic_topics(self):
        devices = Device.query.all()

        kafka_admin_client = KafkaAdminClient(
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS')
        )
        
        topics = []
        try:
            for device in devices:
                topics.append(NewTopic(name=f"{device.mac}_MANAGEMENT".replace(':',""), num_partitions=1, replication_factor=1))

            kafka_admin_client.create_topics(new_topics=topics, validate_only=False)

        except Exception as e:
            print("Unable to create topics or topic already exists -> check db")

    def register_kafka_listener(self, topic, listener):

        def poll():
            consumer = kafka_consumer(topic, bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'))

            consumer.poll(timeout_ms=5000)
            for msg in consumer:
                listener(msg)
                
        t_kafka = threading.Thread()
        t_kafka._target = poll
        t_kafka.daemon = True
        t_kafka.start()

    def monitoring_listener(self, data):
        try:
            monitoring_controller.process_msg(self, data)
        except:
            print("Non registred device") 

    def device_info_listener(self, data):
        
        device_info_controller.process_msg(self, data)
    