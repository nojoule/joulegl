import logging


def setup_logger(name: str, level: int = 10) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s][%(filename)s] - %(message)s"
    )
    logger.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)
    file_handler = logging.FileHandler(f"{name}.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


LOGGER = setup_logger("joulegl")
