"""Custom Logging Handler.

    in main:

from common import log

    in modules:

from common import logger
log = logger_get_mod_logger(__name__)

"""
import logging
import logging.config
#import sys
from ruamel.yaml import YAML

# https://stackoverflow.com/questions/9065136/allowed-characters-in-map-key-identifier-yaml#21195482
log_root = 'TOP'
log_file = None

def get_mod_logger(mod_name=None):
    """return a logger object for each module in a project"""

    if mod_name:
        # module: a.b.c
        #  log name:  <root>.c
        name = mod_name.split('.')[-1]
        log_name = '{}.{}'.format( log_root, name )
    else:
        log_name = log_root
    #print("logger='{}'  mod={} name={}".format(log_name, mod_name, name))
    return logging.getLogger(log_name)

def init_logging_yaml(config_file):
    """initialize logging configuration via a dict specified from a YAML file """
    # https://docs.python.org/3/library/logging.config.html#logging-config-api

    global log_root
    yaml=YAML(typ='safe')   # default, if not specfied, is 'rt' (round-trip)
    with open(config_file) as fh:
        text = fh.read()
    cfg = yaml.load(text)

    if 'log_root' in cfg:
        log_root = cfg['log_root']

    logging.config.dictConfig(cfg)
    return get_mod_logger()
