import logging

from amadeus.connections import manager
from amadeus.datasources import factory
from amadeus.datasources import loader
from amadeus.actions.basic import base_action as base


LOG = logging.getLogger(__name__)


class Extract(base.BaseAction):
    cmd = 'extract'
    args = ['str']

    def __init__(self, conf):
        super(Extract, self).__init__(conf)
        self.purge = self.conf.get('purge', False)
        self.no_cache = self.conf.get('no_cache', False)

    def run(self, datasource, **conf):
        super(Extract, self).run(**conf)
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
        LOG.debug(ds.render_with_args(**conf))
        ds.as_dataframe(conf)
        # TODO(roaet): need to output to shared storage
