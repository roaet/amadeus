import logging

import click

from amadeus import broker
from amadeus.entries import runnable


LOG = logging.getLogger(__name__)


class Player(runnable.Runnable):
    def __init__(self, debug):
        super(Player, self).__init__(debug)
        self.bus = broker.AMQPBroker(self.conf)

    def _on_message(self, channel, method_frame, header_frame, body):
        LOG.debug(method_frame.delivery_tag)
        LOG.debug(body)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def run(self, conf):
        self.bus.blocking_listen(
            'player', conf, 'test', self._on_message)


@click.command(context_settings={'ignore_unknown_options': True})
@click.option('--debug', is_flag=True,
              help='Debug mode flag for development mode. '
              'Sets logging to debug level')
@click.argument('configurations', nargs=-1)
def run(debug, configurations):
    conf = runnable.parse_configurations(configurations)
    Player(debug).run(conf)
