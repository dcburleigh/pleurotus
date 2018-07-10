"""Custom Logging Handler."""

import logging
import sys
#from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

def init_logging(console_level: str='info', file_level: str='debug',
                 fname: str='debug.log', name='|'):
    """
    Initialize logging for the package.

    This function is executed in the csetup module and imported from there in other modules.

    Args:
        console_level (str): Console logging level
        file_level (str): File logging level
        fname (str): file name for logging to file
        name: root logger name

    Returns:
        Logger object
    """
    levels = {'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN,
              'error': logging.ERROR, 'critical': logging.CRITICAL}

    console_fmt = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    file_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    #console_log = logging.StreamHandler()
    console_log = logging.StreamHandler(stream=sys.stdout)
    console_log.setLevel(levels[console_level.lower()])
    console_log.setFormatter(console_fmt)
    logger.addHandler(console_log)

    err_log = logging.StreamHandler(stream=sys.stderr)
    err_log.setLevel(levels['error'])
    err_log.setFormatter(console_fmt)
    logger.addHandler(err_log)

    try:
        file_log = logging.FileHandler(fname, mode='w')
    except FileNotFoundError:
        logger.error('Cannot create {}, '.format(fname))
        return

    file_log.setLevel(levels[file_level.lower()])
    file_log.setFormatter(file_fmt)
    logger.addHandler(file_log)

    return logger
