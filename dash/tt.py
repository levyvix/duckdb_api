import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import get_logger

logger = get_logger({"module": "tt"})

logger.info("Hello, world!")
