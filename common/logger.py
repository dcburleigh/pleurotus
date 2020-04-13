"""Custom Logging Handler.

    in main:

from common import log

    in modules:

from common import logger
log = logger_get_mod_logger(__name__)

"""
import logging
import logging.config
from ruamel.yaml import YAML

import os
config_file = 'log.yml' # default

# https://stackoverflow.com/questions/9065136/allowed-characters-in-map-key-identifier-yaml#21195482
log_root = None
log_file = None

files = []

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

    global log_root, log_file
    yaml=YAML(typ='safe')   # default, if not specfied, is 'rt' (round-trip)
    with open(config_file) as fh:
        text = fh.read()
    cfg = yaml.load(text)

    if 'log_root' in cfg:
        log_root = cfg['log_root']
    #print(f"root={log_root}")
    for l in cfg['loggers'].keys():
        #print(f"root={l}")
        if not log_root:
            # default: first one
            log_root = l

    if not log_root in cfg['loggers']:
        raise Exception(f"invalid log root {log_root}")

    l = cfg['loggers'][log_root]
    #print(f"config={config_file} log level={l['level']}")

    log_file = cfg['handlers']['file']['filename']
    #print(f"log file={log_file} ")
    #print(f"config={config_file} ")
    for h in cfg['handlers']:
        if 'filename' in cfg['handlers'][h]:
            #print(f"handler {h} - f=" )
            files.append(cfg['handlers'][h]['filename'])

    try:
        logging.config.dictConfig(cfg)
    except Exception as err:
        #log.critical(f"bad config file {config_file} - {err}")
        print(f"ERROR bad config file {config_file} - {err}")
        #exit(1)
        return
    return get_mod_logger()


f = os.environ.get('LOG_CONFIG')
if f:
    config_file = f

log = init_logging_yaml(config_file)
