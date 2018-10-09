import logging

import click

from amadeus import broker
from amadeus.config import Configuration
from amadeus.playbooks import factory
from amadeus.playbooks import loader
from amadeus.logger import Logger
from amadeus import runnable
from amadeus import utils


LOG = logging.getLogger(__name__)


class Conductor(runnable.Runnable):
    def __init__(self, debug):
        super(Conductor, self).__init__(debug)
        self.bus = broker.AMQPBroker(self.conf, self._on_message)

    def _on_message(self, channel, method_frame, header_frame, body):
        LOG.debug(method_frame.delivery_tag)
        LOG.debug(body)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def run(self, configuration):
        self.bus.blocking_send("Hello")


@click.command(context_settings={'ignore_unknown_options': True})
@click.option('--debug', is_flag=True,
              help='Debug mode flag for development mode. '
              'Sets logging to debug level')
@click.argument('configurations', nargs=-1)
def run(debug, configurations):
    conf = runnable.parse_configurations(configurations)
    Conductor(debug).run(conf)
