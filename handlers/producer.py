from kafka import KafkaProducer
from dotenv import load_dotenv
load_dotenv()
import os

def create_producer():
    producer = None
    while producer is None:
        try:
            producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'))
        except:
            pass


    return producer