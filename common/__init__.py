from . import logger
import os
config_file = 'log.yml' # default

f = os.environ.get('LOG_CONFIG')
if f:
    config_file = f

log = logger.init_logging_yaml(config_file)
