"""
This module allows to create named logger instance with same parameters for all project files.
Function to call - get_logger
"""
import sys
import logging
import os
from django.conf import settings

ROOT = settings.LOGS_ROOT
if not os.path.isdir(ROOT):
    os.mkdir(ROOT)

__loggers = {}


def get_logger(name, filename='actions'):
    """Create and return new logger object with given name."""
    # first check if logger already exists
    # if logger_name in __loggers:
    #    return __loggers[logger_name]

    log_filename = os.path.join(ROOT, f'{filename}.log')

    __formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                    datefmt='%m/%d/%Y %I:%M:%S %p')
    __file_handler = logging.FileHandler(log_filename, encoding='utf8')
    __file_handler.setFormatter(__formatter)
    __console_handler = logging.StreamHandler(sys.stdout)
    __console_handler.setFormatter(__formatter)

    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        logger.addHandler(__console_handler)
        logger.addHandler(__file_handler)
        __loggers[name] = logger
    return logger



