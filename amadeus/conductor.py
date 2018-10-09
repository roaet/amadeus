import logging

import click

from amadeus.config import Configuration
from amadeus.playbooks import factory
from amadeus.playbooks import loader
from amadeus.logger import Logger
from amadeus import utils


LOG = logging.getLogger(__name__)


class Runnable(object):
    def __init__(self, debug):
        self.conf = Configuration().config
        Logger(self.conf, debug).configure()


class Conductor(Runnable):
    def __init__(self, debug, no_cache):
        super(Conductor, self).__init__(debug)
        self.no_cache = no_cache

    def run(self, playbook, configuration):
        LOG.debug('Conducting playbook %s' % playbook)
        fact = factory.PlaybookFactory(self.conf)
        pb_loader = loader.PlaybookLoader(self.conf, fact)
        if not pb_loader.has_playbook(playbook):
            LOG.warning("Does not have playbook %s" % playbook)
            exit(1)
        pb = pb_loader.load_playbook(playbook)


def parse_configurations(confs):
    out = {}
    for conf in confs:
        key, val = conf.split('=')
        out[key] = val
    return out


@click.command(context_settings={'ignore_unknown_options': True})
@click.option('--debug', is_flag=True,
              help='Debug mode flag for development mode. '
              'Sets logging to debug level')
@click.option('--no_cache', is_flag=True,
              help='Will not use cache, but will still create it')
@click.argument('playbook')
@click.argument('configurations', nargs=-1)
def play(debug, no_cache, playbook, configurations):
    conf = parse_configurations(configurations)
    Conductor(debug, no_cache).run(playbook, conf)
