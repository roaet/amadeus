import logging
import zipfile

import pandas as pd

from amadeus import utils


LOG = logging.getLogger(__name__)


class CacheObject(object):
    def __init__(self, filename):
        self.filename = filename
        self.zip_filename = "%s.zip" % self.filename

    def exists(self):
        return utils.does_file_exist(self.zip_filename)
    
    def write(self, df):
        """
        Create directory with filename
        Create data.csv in directory
        Create other supporting files in directory
        Add directory to new ZipFile named filename
        """
        temp_dir = self.filename
        utils.make_directory(temp_dir, force=True)
        csv_filename = utils.path_join(temp_dir, 'data.csv')
        df.to_csv(csv_filename, index=False)

        utils.zipdir(self.zip_filename, temp_dir)
        LOG.debug("Wrote cache file %s" % self.zip_filename)
        utils.rmtree(temp_dir)

    def read(self):
        LOG.debug("Loading DF from cache %s" % self.filename)
        temp_dir = self.filename

        utils.make_directory(temp_dir, force=True)
        utils.unziptodir(self.zip_filename, temp_dir)

        csv_file = utils.path_join(temp_dir, 'data.csv')
        df = pd.read_csv(csv_file)
        utils.rmtree(temp_dir)
        return df
