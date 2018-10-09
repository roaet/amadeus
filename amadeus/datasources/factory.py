from amadeus import constants
from amadeus.datasources import base
from amadeus.datasources import sql_datasource


class DataSourceFactory(object):
    def __init__(self, conf, connection_manager):
        self.conf = conf
        self.connection_manager = connection_manager

    def get_type(
            self, ds_type):
        if ds_type == constants.DS_BASE:
            return base_datasource.BaseDatasource
        if ds_type == constants.DS_SQL:
            return sql_datasource.SQLDatasource
        return None

    def create(self, ds_type, yamlfile):
        ds = None
        if ds_type == constants.DS_BASE:
            ds = base_datasource.BaseDatasource(
                yamlfile, self.conf, self.connection_manager)
        if ds_type == constants.DS_SQL:
            ds = sql_datasource.SQLDatasource(
                yamlfile, self.conf, self.connection_manager)
        return ds

