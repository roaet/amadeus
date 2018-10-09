import logging

import click

from amadeus.config import Configuration
from amadeus.datasources import factory
from amadeus.datasources import loader
from amadeus.logger import Logger
from amadeus.connections import manager
from amadeus import utils


LOG = logging.getLogger(__name__)


class Runnable(object):
    def __init__(self, debug):
        self.conf = Configuration().config
        Logger(self.conf, debug).configure()


class RunExtract(Runnable):
    def __init__(self, debug, no_cache, purge):
        super(RunExtract, self).__init__(debug)
        self.no_cache = no_cache
        self.purge = purge

    def run(self, datasource, configuration):
        LOG.debug('Running extract of %s' % datasource)
        con_man = manager.ConnectionManager(self.conf)
        fact = factory.DataSourceFactory(self.conf, con_man)
        ds_loader = loader.DatasourceLoader(self.conf, fact)
        if not ds_loader.has_datasource(datasource):
            LOG.warning("Does not have datasource %s" % datasource)
            exit(1)
        else:
            LOG.debug("%s found" % datasource)

        ds = ds_loader.load_datasource(datasource)
        if self.purge:
            ds.purge_cache()
            exit(0)
        ds.set_cache(not self.no_cache)
        LOG.debug(ds.render_with_args(**configuration))
        df = ds.as_dataframe(configuration)


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
@click.option('--purge_cache', is_flag=True,
              help='Remove all caches for datasource and exit')
@click.argument('datasource')
@click.argument('configurations', nargs=-1)
def extract(debug, no_cache, purge_cache, datasource, configurations):
    conf = parse_configurations(configurations)
    RunExtract(debug, no_cache, purge_cache).run(datasource, conf)
