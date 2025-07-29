import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS}|{extra[request_id]}|{extra[model_id]}|{level: <8}|{name}:{function}:{line}|{message}",
)

# this is the entry point for WSGI server in production
from xxy.web import app
