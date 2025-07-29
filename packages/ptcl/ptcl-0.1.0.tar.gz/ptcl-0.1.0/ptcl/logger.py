import logging as __logging

def get_logger(
    logger_name: str = 'ptcl_logger',
    level: int = __logging.INFO,
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    date_format: str = '%Y-%m-%d %H:%M:%S'
) -> __logging.Logger:
    """
    Returns a basic, console-configured logger.

    Args:
        logger_name (str): The name of the logger
        level (int): The minimum logging level
        log_format (str): The format string for log messages.
        date_format (str): The format for the timestamp in log messages.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = __logging.getLogger(logger_name)
    logger.setLevel(level)

    if not logger.handlers:

        console_handler = __logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = __logging.Formatter(log_format, datefmt=date_format)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

logger_ = get_logger()
