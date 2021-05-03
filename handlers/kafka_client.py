from handlers.listeners import KafkaClient

kafka_client = KafkaClient()

def initialize_kafka(app):
    kafka_client.initialize_app(app)
    kafka_client.register_listeners()
    kafka_client.create_dynamic_topics()