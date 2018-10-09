import hashlib
import logging

import numpy as np
import pandas as pd
import yaml

from amadeus import constants
from amadeus import utils


LOG = logging.getLogger(__name__)


class BaseDatasource(object):
    def __init__(self, yaml_file, conf, connection_manager):
        """Assumes that yaml_file is valid."""
        self.yaml_file = yaml_file
        self.filename = utils.basename(self.yaml_file)
        self.conf = conf
        self.connection_manager = connection_manager
        with open(yaml_file, 'r') as stream:
            self.yaml_obj = yaml.load(stream)['datasource']
        self.type = self.yaml_obj['type']
        self.defaults = self._gather_defaults()
        self.dtypes = self.yaml_obj.get('types', {})
        self.do_cache = True
        LOG.debug("Loading datasource from %s" % self.yaml_file)

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

    def _gather_defaults(self):
        return self.yaml_obj.get('defaults', {})

    @property
    def _cache_dir(self):
        name = "%s_%s" % (self.filename, self.type)
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
        return "df_%s.csv" % suffix

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

    def _load_from_cache(self, filename):
        LOG.debug("Loading DF from cache %s" % filename)
        df = pd.read_csv(filename)
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
        return utils.does_file_exist(filename)

    def _precache(self, **configuration):
        filename = self._create_target_filename(**configuration)
        return self._load_from_cache(filename)

    def _postcache(self, df, **configuration):
        if df is None or len(df) == 0:
            return None
        filename = self._create_target_filename(**configuration)
        df.to_csv(filename, index=False)
        LOG.debug("Wrote cache file %s" % filename)
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

    def as_dataframe(self, configuration):
        final = self._merge_defaults(configuration)
        return self._cached_as_dataframe(**final)

    def __repr__(self):
        return "DS(%s:%s)" % (self.type, self.filename)

    @staticmethod
    def check(yaml_obj):
        if 'datasource' not in yaml_obj:
            LOG.warning(
                "Missing required 'datasource' top-level key "
                "of file %s" % yaml_file)
            return False
        if 'type' not in yaml_obj['datasource']:
            LOG.warning(
                "Missing required 'type' 2nd-level key of file %s" %
                yaml_file)
            return False
        ds_type = yaml_obj['datasource']['type']
        if ds_type not in constants.DATASOURCE_TYPES:
            LOG.warning("%s not a known datasource type from %s" %
                (ds_type, yaml_file))
            return False
        return True

