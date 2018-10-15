import hashlib
import logging

import numpy as np
import pandas as pd

from amadeus import constants
from amadeus.datasources import cache
from amadeus import utils
from amadeus import yaml_object as yo


LOG = logging.getLogger(__name__)

TOP_LEVEL_KEY = 'datasource'


class BaseDatasource(yo.YAMLBackedObject):
    def __init__(self, yaml_obj, conf, connection_manager):
        super(BaseDatasource, self).__init__(yaml_obj, conf, TOP_LEVEL_KEY)
        self.connection_manager = connection_manager
        self.defaults = self._gather_defaults()
        self.dtypes = self.yaml_obj.get('types', {})
        self.do_cache = True

    def _gather_defaults(self):
        return self.yaml_obj.get('defaults', {})

    @property
    def _cache_dir(self):
        name = "%s_%s" % (self.name, self.type)
        cache_dir = utils.path_join(constants.CACHE_DIR, name)
        return cache_dir

    def _create_cache_directory(self):
        if not utils.does_directory_exist(self._cache_dir):
            utils.make_directory(self._cache_dir)
            LOG.debug("Made cache directory %s" % self._cache_dir)

    def _hash_seed(self, **configuration):
        return str(configuration)

    def _generate_df_suffix_from_conf(self, **configuration):
        if not configuration:
            return "0" * 32
        hash_arg = self._hash_seed(**configuration)
        suffix = hashlib.md5(hash_arg).hexdigest()
        return suffix

    def _generate_cache_filename(self, **configuration):
        suffix = self._generate_df_suffix_from_conf(**configuration)
        return "cache_%s" % suffix

    def _target_cache_file(self, **configuration):
        filename = self._generate_cache_filename(**configuration)
        abs_filepath = utils.path_join(self._cache_dir, filename)
        return abs_filepath

    def _set_types(self, df_in):
        df = df_in.copy()
        for col in df.columns:
            target_type = self.dtypes.get(col, 'string')
            if target_type == 'string':
                df[col] = df[col].astype(str)
            if target_type == 'date':
                df[col] = pd.to_datetime(df[col])
            if target_type == 'int':
                df[col] = df[col].astype(np.int64)
            if target_type == 'float':
                df[col] = df[col].astype(np.float64)
        return df

    def _write_cache(self, filename, df):
        cache_obj = cache.CacheObject(filename)
        cache_obj.write(df)

    def _read_cache(self, filename):
        cache_obj = cache.CacheObject(filename)
        df = cache_obj.read()
        return df

    def _load_from_cache(self, filename):
        df = self._read_cache(filename)
        LOG.debug("Loaded types: %s" % df.dtypes)
        df = self._set_types(df)
        LOG.debug("Set types: %s" % df.dtypes)
        return df

    def _create_target_filename(self, **configuration):
        self._create_cache_directory()
        return self._target_cache_file(**configuration)

    def _hascache(self, **configuration):
        if not self.do_cache:
            return False
        filename = self._create_target_filename(**configuration)
        cache_obj = cache.CacheObject(filename)
        return cache_obj.exists()

    def _precache(self, **configuration):
        filename = self._create_target_filename(**configuration)
        return self._load_from_cache(filename)

    def _postcache(self, df, **configuration):
        if df is None or len(df) == 0:
            return None
        filename = self._create_target_filename(**configuration)
        self._write_cache(filename, df)
        return self._load_from_cache(filename)

    def _get_data(self, **configuration):
        return pd.DataFrame([])

    def _cached_as_dataframe(self, **configuration):
        if self._hascache(**configuration):
            return self._precache(**configuration)

        df = self._get_data(**configuration)

        return self._postcache(df, **configuration)

    def _merge_defaults(self, configuration):
        final = self.defaults.copy()
        for k, v in configuration.iteritems():
            final[k] = v
        return final

    def __repr__(self):
        return "DS(%s:%s)" % (self.type, self.name)

    def purge_cache(self):
        cache_dir = self._cache_dir
        try:
            utils.rmtree(cache_dir)
        except OSError:
            LOG.info("Nothing happened")
            return False
        return True

    def set_cache(self, flag):
        self.do_cache = flag

    def as_dataframe(self, configuration):
        final = self._merge_defaults(configuration)
        return self._cached_as_dataframe(**final)

    @staticmethod
    def check(yaml_obj, yaml_file, TOP_LEVEL_KEY):
        return yo.YAMLBackedObject.check(
            yaml_obj, yaml_file, TOP_LEVEL_KEY, constants.DATASOURCE_TYPES)
