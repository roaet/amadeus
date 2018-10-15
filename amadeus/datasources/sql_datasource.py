import logging

import jinja2

from amadeus.datasources import base


LOG = logging.getLogger(__name__)


class SQLDatasource(base.BaseDatasource):
    def __init__(self, yaml_obj, conf, connection_manager):
        super(SQLDatasource, self).__init__(
            yaml_obj, conf, connection_manager)
        self.query = self.yaml_obj['query']
        self.conf = conf
        self.connection_manager = connection_manager
        self.connection = self._select_connection()

    def _select_connection(self):
        return self.yaml_obj.get(
            'connection_name', self.yaml_obj.get('connection_string', None))

    def __repr__(self):
        s = super(SQLDatasource, self).__repr__()
        return "%s-%s:%s" % (s, self.connection, self.query)

    def _render(self, **conf):
        template = jinja2.Template(self.query)
        return template.render(**conf)

    def _hash_seed(self, **conf):
        return "%s_%s_%s" % (self.connection, self.query, str(conf))

    def _get_data(self, **conf):
        con_str = self.yaml_obj.get('connection_string', None)
        con_name = self.yaml_obj.get('connection_name', None)
        connection = self.connection_manager.get_connection(con_name, con_str)
        df = connection.query_to_df(self.render_with_args(**conf))
        return df

    def render_with_args(self, **conf):
        if conf is None or not conf:
            conf = self.defaults

        return self._render(**conf)

    @staticmethod
    def check(yaml_obj, yaml_file):
        base.BaseDatasource.check(yaml_obj, yaml_file, base.TOP_LEVEL_KEY)
        required_keys = ['query']
        problems = 0
        for k in required_keys:
            if k not in yaml_obj['datasource']:
                LOG.warning("Missing required '%s' key" % k)
                problems += 1
        if (
            'connection_string' not in yaml_obj['datasource'] and
            'connection_name' not in yaml_obj['datasource']
        ):
            LOG.warning("Missing one of connection_string or connection_name")
            problems += 1
        if problems > 0:
            return False
        return True
