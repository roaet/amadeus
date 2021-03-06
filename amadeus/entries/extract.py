import logging

import click

from amadeus.actions import factory as action_factory
from amadeus.entries import runnable


LOG = logging.getLogger(__name__)


class RunExtract(runnable.Runnable):
    def __init__(self, debug, no_cache, purge):
        super(RunExtract, self).__init__(debug)
        self.conf['no_cache'] = no_cache
        self.conf['purge'] = purge

    def run(self, datasource, conf):
        AF = action_factory.ActionFactory(self.conf)
        """
        Action = AF.get_action('extract')
        if Action is None:
            LOG.debug("Could not find action")
            exit(1)
        Action(self.conf).run(datasource, conf)
        """
        AF('extract', 'poop', limit=10)
        AF('print', 'Hi there')
        AF('loop', 2)


@click.command(context_settings={'ignore_unknown_options': True})
@click.option('--debug', is_flag=True,
              help='Debug mode flag for development mode. '
              'Sets logging to debug level')
@click.option('--no_cache', is_flag=True,
              help='Will not use cache, but will still create it')
@click.option('--purge_cache', is_flag=True,
              help='Remove all caches for datasource and exit')
@click.argument('datasource')
@click.argument('configurations', nargs=-1)
def extract(debug, no_cache, purge_cache, datasource, configurations):
    conf = runnable.parse_configurations(configurations)
    RunExtract(debug, no_cache, purge_cache).run(datasource, conf)
