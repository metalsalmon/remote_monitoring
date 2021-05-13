from handlers.producer import ProducerKlient


kafka_producer = ProducerKlient()

def initialize_producer():
    kafka_producer.initialize_producer()