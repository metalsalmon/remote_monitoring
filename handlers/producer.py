from kafka import KafkaProducer
from dotenv import load_dotenv
import json
load_dotenv()
import os

class ProducerKlient():

    producer = None

    def initialize_producer(self):
        while(True):
            try:
                self.producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
                                            acks=1,
                                            value_serializer=lambda x: json.dumps(x).encode('utf-8')
                                        )
                if self.producer != None:
                    break
            except Exception as e:
                print(e)   



