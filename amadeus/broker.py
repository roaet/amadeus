import logging

import pika


LOG = logging.getLogger(__name__)


class AMQPBroker(object):
    def __init__(self, conf, on_message):
        self.conf = conf
        self.on_message = on_message
        self._initialize()

    def _initialize(self):
        creds = pika.PlainCredentials('admin', 'password')
        parameters = pika.ConnectionParameters(
            'localhost', 5672, '/', creds)
        self.connection = pika.BlockingConnection(parameters=parameters)
        self.channel = self.connection.channel()

    def blocking_listen(self, configuration):
        self.channel.basic_consume(self.on_message, 'test')
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        self.connection.close()

    def blocking_send(self, message):
        self.channel.basic_publish(
            exchange='amadeus', routing_key='test', body=message)
        self.connection.close()
