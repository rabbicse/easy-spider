import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
FORMATTER = logging.Formatter(
    '%(asctime)s - [%(module)s %(name)s %(processName)s %(threadName)s %(lineno)d] - %(levelname)s - %(message)s')


def setup_formatter(format):
    FORMATTER = logging.Formatter(format)


def setup_rotating_file_logger(file_name, max_bytes=10 * 1024 * 1024, backup_count=10):
    # create file handler which logs even debug messages
    fh = RotatingFileHandler(file_name, maxBytes=max_bytes, backupCount=backup_count)
    fh.setLevel(logging.INFO)
    fh.setFormatter(FORMATTER)

    # add the handlers to the logger
    logger.addHandler(fh)


def setup_stream_logger():
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(FORMATTER)

    # add the handlers to the logger
    logger.addHandler(ch)
