from amadeus.utils import *

DS_BASE = 'base'
DS_SQL = 'sql'

DATASOURCE_TYPES = [
    DS_BASE,
    DS_SQL,
]

COMP_BASE = 'base'

COMPOSITION_TYPES = [
    COMP_BASE,
]

REDACT = '<REDACT>'
ENCODING = 'cp1252'

COST_RSE = 2
COST_ARC = 3
COST_HEX = 8
COST_O365 = 12

PACKAGE_ROOT = dir_name(abs_path_for_file(__file__))
PROJECT_ROOT = abs_path_for_file(path_join(PACKAGE_ROOT, os.pardir))
DEFAULT_SUPPORT_DIR = path_join(PROJECT_ROOT, 'support_files')
DEFAULT_TRAINING_DIR = path_join(PROJECT_ROOT, 'training_files')
DEFAULT_OUTPUT_DIR = path_join(PROJECT_ROOT, 'output_files')
DEFAULT_REPORT_DIR = path_join(PROJECT_ROOT, 'reports')
DEFAULT_SCRATCH_DIR = path_join(PROJECT_ROOT, 'scratch')
DEFAULT_RESOURCE_DIR = path_join(PROJECT_ROOT, 'resources')
DEFAULT_DATASOURCE_DIR = path_join(DEFAULT_RESOURCE_DIR, 'datasources')
DEFAULT_COMPOSITION_DIR = path_join(DEFAULT_RESOURCE_DIR, 'compositions')
DEFAULT_BASE_CONF = path_join(PROJECT_ROOT, 'configuration')

USER_HOME_DIR = path_join(user_dir(), '.amadeus')
CACHE_DIR = path_join(USER_HOME_DIR, 'cache')
SCRATCH_DIR = path_join(USER_HOME_DIR, 'scratch')
TEST_DATA_DIR = path_join(USER_HOME_DIR, 'test_data')
LOG_LOCATION = path_join(USER_HOME_DIR, 'amadeus.log')

CONF_FILENAME = 'amadeus.conf'
CONF_SEARCH_PATHS = [USER_HOME_DIR, get_cwd(), '/etc', DEFAULT_SUPPORT_DIR]
DEFAULT_CONF_DIRS = [
    path_join(path, CONF_FILENAME) for path in CONF_SEARCH_PATHS]
