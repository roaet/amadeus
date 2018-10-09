import logging

from amadeus.connections import sqlconnection


LOG = logging.getLogger(__name__)

DB_CON_FORMAT = (
    'DRIVER=FreeTDS;SERVER=%s;PORT=%s;UID=%s;'
    'PWD=%s;DATABASE=%s;TDS_Version=8.0;')
DEFAULT_PORT = 1433


class ConnectionManager(object):
    def __init__(self, conf):
        self.connections = {}
        self.conf = conf

    def _construct_constr(self, server, username, password, db):
        return DB_CON_FORMAT % (
                server, DEFAULT_PORT, username, password, db
            )

    def _get_constr_by_name(self, name):
        if name in self.conf and 'connection_string' in self.conf.get(name):
            return self.conf.get(name).get('connection_string')
        elif name in self.conf:
            if any(
                [x not in self.conf.get(name) for x in [
                    'server', 'username', 'password', 'db']]):
                return None
            return self._construct_constr(
                self.conf.get(name).get('server'),
                self.conf.get(name).get('username'),
                self.conf.get(name).get('password'),
                self.conf.get(name).get('db'))
        else:  # try connections.yaml
            return None

    def get_connection(self, name, con_str):
        if name:
            con_str = self._get_constr_by_name(name)
        if not con_str:
            return None
        return sqlconnection.SqlalchemyConnection(self.conf, con_str)
