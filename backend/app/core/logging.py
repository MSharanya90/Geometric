"""
Structured logging configuration for GeoMeasure.
Formats logs consistently with ISO timestamps, module names, and severity.
"""
import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure root and application loggers."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    log_format = (
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
        force=True
    )

    logger = logging.getLogger("geomeasure")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()
