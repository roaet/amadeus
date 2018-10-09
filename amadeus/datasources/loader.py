import logging

from amadeus import constants
from amadeus.datasources.base import BaseDatasource
from amadeus import yaml_loader


LOG = logging.getLogger(__name__)


class DatasourceLoader(object):
    def __init__(self, conf, factory):
        self.loader = yaml_loader.YAMLLoader(
            conf, factory, constants.DEFAULT_DATASOURCE_DIR,
            BaseDatasource, 'datasource')

    def has_datasource(self, datasource_name):
        return self.loader.has_entity(datasource_name)

    def load_datasource(self, datasource_name):
        return self.loader.load_entity(datasource_name)
