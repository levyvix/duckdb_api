import sys
from pathlib import Path

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add(Path(__file__).parent.parent / "logs" / "app.log", level="INFO")


def get_logger():
    return logger
