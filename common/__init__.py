from . import logger
import os 
config_file = 'wxt.log.yml'
config_file = 'gp.log.yml'
config_file = 'log.yml'

f = os.environ.get('LOG_CONFIG')
if f:
    config_file = f 
    
log = logger.init_logging_yaml(config_file)
