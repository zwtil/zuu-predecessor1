import logging
import sys


def basic_debug(level=logging.DEBUG):
    """
    Sets up basic logging configuration with the specified logging level and stream.

    Args:
        level (int, optional): The logging level to set. Defaults to logging.DEBUG.

    Returns:
        None
    """
    logging.basicConfig(level=level, stream=sys.stdout)


def file_debug(file, level=logging.DEBUG):
    """
    Sets up basic logging configuration with the specified logging level and file.

    Args:
        file (str): The path to the file where the log messages will be written.
        level (int, optional): The logging level to set. Defaults to logging.DEBUG.

    Returns:
        None
    """
    logging.basicConfig(level=level, filename=file)
