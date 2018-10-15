import logging

import click
import pika

from amadeus import broker
from amadeus.compositions import factory
from amadeus.compositions import loader
from amadeus.entries import runnable


LOG = logging.getLogger(__name__)


class Conductor(runnable.Runnable):
    def __init__(self, debug):
        super(Conductor, self).__init__(debug)
        self.bus = broker.AMQPBroker(self.conf)

    def sim(self, composition):
        CF = factory.CompositionFactory(self.conf)
        CL = loader.CompositionLoader(self.conf, CF)
        if CL.has_composition(composition):
            LOG.debug("Found composition")
        else:
            LOG.debug("Composition not found %s" % composition)

        comp = CL.load_composition(composition)
        if comp is None:
            LOG.debug("Something wrong with composition %s" % composition)
        LOG.debug(comp)
        comp.run()

    def recv(self, ch, method, props, body):
        LOG.debug(body)
        CF = factory.CompositionFactory(self.conf)
        CL = loader.CompositionLoader(self.conf, CF)
        LOG.debug(CL.load_composition_str(body))
        self.bus.blocking_send('conductor', 'amadeus', 'test', "Hello")
        response = "Said hi to player"
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id),
            body=response)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self, conf):
        self.bus.rpc_listen('rpc_test', 'amacontrol_rpc', self.recv)

    def _on_message(self, channel, method_frame, header_frame, body):
        LOG.debug(method_frame.delivery_tag)
        LOG.debug(body)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)


@click.command(context_settings={'ignore_unknown_options': True})
@click.option('--debug', is_flag=True,
              help='Debug mode flag for development mode. '
              'Sets logging to debug level')
@click.argument('configurations', nargs=-1)
def run(debug, configurations):
    conf = runnable.parse_configurations(configurations)
    Conductor(debug).run(conf)


@click.command(context_settings={'ignore_unknown_options': True})
@click.option('--debug', is_flag=True,
              help='Debug mode flag for development mode. '
              'Sets logging to debug level')
@click.argument('composition')
@click.argument('configurations', nargs=-1)
def simfsm(debug, composition, configurations):
    runnable.parse_configurations(configurations)
    Conductor(debug).sim(composition)
