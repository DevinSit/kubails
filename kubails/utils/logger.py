import logging
import os
import sys
from logging.handlers import RotatingFileHandler


LOG_MAX_SIZE = 512000  # 500KB
LOG_BACKUP_COUNT = 2
PROJECT_NAME = "kubails"


def create_logger() -> logging.Logger:
    log_folder = os.path.join(os.path.expanduser("~"), ".{}".format(PROJECT_NAME))
    log_file = os.path.join(log_folder, "{}.log".format(PROJECT_NAME))

    # Disable creating the log directory if running in a test
    if not hasattr(sys, "_called_from_test") and not os.path.exists(log_folder):  # pragma: no cover
        os.makedirs(log_folder)

    logger = logging.getLogger("")  # Put the logger at the root so that all sub modules can access it
    logger.setLevel(logging.DEBUG)

    console_formatter = logging.Formatter("[KUBAILS] %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(console_handler)

    # Disable creating the file handler if running in a test
    if not hasattr(sys, "_called_from_test"):  # pragma: no cover
        file_formatter = logging.Formatter("[%(levelname)s] (%(asctime)s) %(name)s (%(lineno)s) - %(message)s")

        file_handler = RotatingFileHandler(log_file, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP_COUNT)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)

        logger.addHandler(file_handler)

    return logger
