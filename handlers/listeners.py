from kafka import KafkaConsumer as kafka_consumer
import threading
from dotenv import load_dotenv
load_dotenv()
import os
from controllers import monitoring_controller
from controllers import device_info_controller

class KafkaConsumer(object):

    def __init__(self, app):
        self.app = app


    def register_listeners(self):
        self.register_kafka_listener('monitoring', self.monitoring_listener)
        self.register_kafka_listener('DEVICE_INFO', self.device_info_listener)

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

        monitoring_controller.process_msg(self, data)

    def device_info_listener(self, data):
        
        device_info_controller.process_msg(data)
    

