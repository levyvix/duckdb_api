import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

# Remove default logger
logger.remove()

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Add console handler with custom format
logger.add(
    sys.stdout,
    level="INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
    colorize=True,
)

# Add file handler with rotation and custom format
logger.add(
    log_dir / "app_{time}.log",
    rotation="100 MB",  # Rotate when file reaches 100MB
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress rotated logs
    level="DEBUG",
    format=("{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message} | {extra}"),
    serialize=True,  # Enable JSON serialization for structured logging
)


def get_logger(context: dict[str, Any] | None = None) -> Any:
    """
    Get a logger instance with optional context.

    Args:
        context (Dict[str, Any] | None): Additional context to be included in log messages.

    Returns:
        Any: Configured logger instance
    """
    if context:
        logger.configure(extra=context)
    return logger


# Add custom level for business events
logger.level("BUSINESS", no=25, color="<yellow>")

# Add custom level for metrics
logger.level("METRIC", no=15, color="<blue>")


def log_error_with_context(error: Exception, context: dict[str, Any] | None = None) -> None:
    """
    Log an error with additional context and traceback.

    Args:
        error (Exception): The error to log
        context (Dict[str, Any] | None): Additional context to include in the log
    """
    error_context = {
        "error_type": type(error).__name__,
        "error_details": str(error),
        "timestamp": datetime.utcnow().isoformat(),
        **(context or {}),
    }
    logger.bind(**error_context).exception("Error occurred")
