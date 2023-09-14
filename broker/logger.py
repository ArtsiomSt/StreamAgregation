import logging

import structlog

logger_structlog = structlog.get_logger()
logger_standard = logging.getLogger("broker_logger")
logging.basicConfig(level=logging.INFO)
