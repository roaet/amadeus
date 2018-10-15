import logging
import uuid

import pika

from amadeus import exceptions as exc


LOG = logging.getLogger(__name__)


class RPCClient(object):
    def __init__(self, conf):
        self.conf = conf
        self.bus = AMQPBroker(self.conf)


class RPCCall(object):
    def __init__(self, conf, connection, channel):
        self.connection = connection
        self.channel = channel
        self.conf = conf

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(
            self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, exchange, routing_key, body):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        properties = pika.BasicProperties(
            reply_to=self.callback_queue, correlation_id=self.corr_id)
        self.channel.basic_publish(
            exchange=exchange, routing_key=routing_key, properties=properties,
            body=body)
        while self.response is None:
            self.connection.process_data_events()
        return self.response


class AMQPBroker(object):
    def __init__(self, conf):
        self.conf = conf
        self.configured_exchanges = []
        self._initialize()
        self.connections = {}

    def _configure_exchanges(self, channel):
        amqp_exchanges = self.conf.get('AMQP_EXCHANGES', [])
        for name, params in amqp_exchanges.iteritems():
            method = params[0]
            durable = params[1] == 'yes'
            channel.exchange_declare(
                exchange=name, exchange_type=method, durable=durable)
            self.configured_exchanges.append(name)

    def _configure_queues(self, channel):
        amqp_queues = self.conf.get('AMQP_QUEUES', [])
        queue_params = ['exchange', 'durable', 'routing_key']
        for name, params in amqp_queues.iteritems():
            if len(params) != len(queue_params):
                LOG.error("Queue params for %s are wrong" % name)
            exchange = '' if params[0] == 'default' else params[0]
            durable = params[1] == 'yes'
            routing_key = '' if params[2] == 'none' else params[2]
            channel.queue_declare(queue=name, durable=durable)
            if exchange != '':
                channel.queue_bind(
                    exchange=exchange, queue=name, routing_key=routing_key)

    def _initialize(self):
        if 'AMQP' not in self.conf:
            raise exc.ConfigError("Missing AMQP key in configuration")
        amqp_conf = self.conf.get('AMQP')
        subkeys = ['server', 'port', 'path', 'username' , 'password']
        if any(x not in amqp_conf for x in subkeys):
            raise exc.ConfigError(
                "Missing required AMQP keys in configuration")
        server, port, path, username, password = tuple(
            [amqp_conf.get(x) for x in subkeys])
        creds = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(server, port, path, creds)

    def _delete_connection(self, name):
        if name not in self.connections:
            return
        try:
            self.connections[name].close()
        except Exception:
            pass
        finally:
            del self.connections[name]

    def _create_connection(self, name):
        self._delete_connection(name)
        connection = pika.BlockingConnection(parameters=self.parameters)
        self.connections[name] = connection
        channel = connection.channel()
        self._configure_exchanges(channel)
        self._configure_queues(channel)
        return connection, channel

    def rpc_listen(
            self, connection_name, routing_key, fx):
        connection, channel = self._create_connection(connection_name)
        channel.queue_declare(queue=routing_key)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(fx, queue=routing_key)
        channel.start_consuming()

    def rpc_send(
            self, connection_name, routing_key, message):
        connection, channel = self._create_connection(connection_name)
        rpc_call = RPCCall(self.conf, connection, channel)
        return rpc_call.call('', routing_key, message)

    def blocking_send(
            self, connection_name, exchange, routing_key, message,
            properties=None, wait=False, wait_fx=None):
        connection, channel = self._create_connection(connection_name)
        channel.basic_publish(
            exchange=exchange, routing_key=routing_key, body=message,
            properties=properties)
        self._delete_connection(connection_name)

    def blocking_listen(
            self, connection_name, configuration, routing_key, fx):
        connection, channel = self._create_connection(connection_name)
        channel.basic_consume(fx, routing_key)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        self._delete_connection(connection_name)
