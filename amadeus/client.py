import logging

import click
import pika

from amadeus import broker
from amadeus.compositions.factory import CompositionFactory
from amadeus.compositions.loader import CompositionLoader
from amadeus import runnable


LOG = logging.getLogger(__name__)


class Client(runnable.Runnable):
    def __init__(self, composition, debug):
        super(Client, self).__init__(debug)
        self.composition = composition
        self.bus = broker.AMQPBroker(self.conf)

    def _on_message(self, channel, method_frame, header_frame, body):
        LOG.debug(method_frame.delivery_tag)
        LOG.debug(body)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def run(self, configuration):
        CF = CompositionFactory(self.conf)
        CL = CompositionLoader(self.conf, CF)
        if CL.has_composition(self.composition):
            LOG.debug("Found composition")
        else:
            LOG.debug("Composition not found %s" % self.composition)

        comp = CL.load_composition(self.composition)
        if comp is None:
            LOG.debug("Something wrong with composition %s" % self.composition)
        response = self.bus.rpc_send(
            'rpc_testing', 'amacontrol_rpc', comp.yamldump)
        LOG.debug(response)


@click.command(context_settings={'ignore_unknown_options': True})
@click.option('--debug', is_flag=True,
              help='Debug mode flag for development mode. '
              'Sets logging to debug level')
@click.argument('composition')
@click.argument('configurations', nargs=-1)
def run(debug, composition, configurations):
    conf = runnable.parse_configurations(configurations)
    Client(composition, debug).run(conf)
