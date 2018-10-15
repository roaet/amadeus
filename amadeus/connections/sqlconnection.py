import logging
import time

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import exc as saexc

from amadeus import exceptions as exc
from amadeus import utils


LOG = logging.getLogger(__name__)

SERVER_STR_FORMAT = 'mssql+pyodbc:///?odbc_connect=%s'


class SqlalchemyConnection():
    def __init__(self, conf, connection_string):
        self.connection_string = connection_string
        self.echo = False
        self.conf = conf

    def query_to_df(self, query):
        res = None
        con = None
        max_retry = 2
        for i in xrange(max_retry):
            try:
                con = self.get_connection()

                LOG.debug("Executing query %s" % query.__class__.__name__)
                t0 = time.time()
                res = con.execute(query)
                t1 = time.time()
                LOG.debug(
                    "Query took %f seconds (total: %f)" %
                    ((t1 - t0), (t1 - t0)))
                columns = res.keys()
                results = res.fetchall()
                t2 = time.time()
                LOG.debug(
                    "Fetch took %f seconds (total: %f)" %
                    ((t2 - t1), (t2 - t0)))
                if results is None:
                    LOG.warning("Result set is None")
                else:
                    LOG.debug("Returned %d results" % len(results))

                dataframe = pd.DataFrame(results, columns=columns)
                t3 = time.time()
                LOG.debug(
                    "DF took %f seconds (total: %f)" % ((t3 - t2), (t3 - t0)))
                return dataframe
            except saexc.ProgrammingError as e:
                e_str = str(e).replace('\\n', '\n')
                if i == max_retry - 1:
                    LOG.debug('Error: Giving up. %s' % e_str)
                else:
                    LOG.debug('Possible deadlock. Retrying.')
            finally:
                if res is not None:
                    res.close()
                if con is not None:
                    con.close()
        return None

    def _create_engine(self, conn_str):
        return create_engine(conn_str, echo=self.echo)

    def get_connection(self):
        connect_str = SERVER_STR_FORMAT % utils.url_encode(
            self.connection_string)
        eng = self._create_engine(connect_str)
        try:
            con = eng.connect()
        except (saexc.DBAPIError, saexc.ProgrammingError):
            LOG.error("Failed to connect")
            raise exc.ConnectionFailed()
        return con
