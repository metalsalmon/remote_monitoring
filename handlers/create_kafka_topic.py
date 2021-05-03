from kafka.admin import KafkaAdminClient, NewTopic
import os
from dotenv import load_dotenv
load_dotenv()
from handlers.kafka_client import KafkaClient


def create_device_topic(mac):

    kafka_admin_client = KafkaAdminClient(
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    )

    topics = []
    try:
        topics.append(NewTopic(name=f"{mac}_MANAGEMENT".replace(':',""), num_partitions=1, replication_factor=1))
        topics.append(NewTopic(name=f"{mac}_DEVICE_INFO".replace(':',''), num_partitions=1, replication_factor=1))
        register_device_listener(mac)

        kafka_admin_client.create_topics(new_topics=topics, validate_only=False)
        del kafka_admin_client

    except Exception as e:
        print("Unable to create topics or topic already exists -> check db")