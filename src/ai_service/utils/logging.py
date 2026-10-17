import logging
import sys


def configure_logging() -> logging.Logger:
    """Configure logging to stdout, including inside a container."""
    logger = logging.getLogger("ai_service")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
