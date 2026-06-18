import logging
from logging.handlers import RotatingFileHandler
import os


def configure_logger():

    if not os.path.exists("logs"):
        os.mkdir("logs")

    logger = logging.getLogger()

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        "logs/application.log",
        maxBytes=10485760,
        backupCount=5
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)