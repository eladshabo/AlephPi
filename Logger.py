import logging
from typing import Callable, Any


def log_function(func: Callable[..., Any]) -> Callable[..., Any]:
    """A wrapper for logging every function entry, exit and exception.

    Args:
        func (Callable): Function to be called, relevant arguments will be set during the actual function call.
    """

    def wrapper(*args, **kwargs):
        try:
            logging.info(f"{func.__name__} started with parameters: {args} {kwargs}")
            return func(*args, **kwargs)
        except Exception as ex:
            logging.exception(ex)
            raise ex
        finally:
            logging.info(f"Function {func.__name__} exited")

    return wrapper


def setup_logger(log_path: str) -> logging.Logger:
    """Setting up logger for all AlephPi activity.

    Args:
        log_path (str): A path to the logging file

    Raises:
        Exception: In case of internal exception in logging module.

    Returns:
        logging.Logger: A valid logger,
    """
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=500000, backupCount=4
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    except Exception as ex:
        raise Exception(f"Cannot init logger - {ex}")
