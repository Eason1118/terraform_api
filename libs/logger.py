#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/22 16:43
# @Author  : harilou
# @Describe:

import logging
import os
from settings import LOG_FILE, LOG_LEVEL
from logging.handlers import RotatingFileHandler


def get_log(name, file_path, log_level):
    """Generate a standard logger
      Args:
        name - logger object
        file_path - the log file path
        log_level - log level, defalt value is INFO
    """
    # Create the directory if it does not exist
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as msg:
            raise Exception("Can't make directory %s. %s" % (directory, msg))

    # Get log level
    if log_level.upper() == "DEBUG":
        logging_level = logging.DEBUG
    elif log_level.upper() == "INFO":
        logging_level = logging.INFO
    elif log_level.upper() == "WARNING":
        logging_level = logging.WARNING
    elif log_level.upper() == "ERROR":
        logging_level = logging.ERROR
    elif log_level.upper() == "CRITICAL":
        logging_level = logging.CRITICAL
    else:
        logging_level = logging.INFO

    file_handler = RotatingFileHandler(file_path, maxBytes=10 * 1024 * 1024,
                                       backupCount=5, encoding="UTF-8")
    fmt = "%(asctime)s [%(levelname)s] %(threadName)s %(filename)s:%(lineno)d - %(message)s"
    formatter = logging.Formatter(fmt)
    file_handler.setFormatter(formatter)
    _logger = logging.getLogger(name)
    _logger.addHandler(file_handler)
    _logger.setLevel(logging_level)

    class ContextualFilter(logging.Filter):
        def filter(self, log_record):
            # no logger for logview thread
            if log_record.threadName.startswith('logview'):
                return False
            return True

    _logger.addFilter(ContextualFilter())
    return _logger


# init logger
logger = get_log(__name__, LOG_FILE, log_level=LOG_LEVEL)