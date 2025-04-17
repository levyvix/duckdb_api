"""API package for DuckDB API."""

from .async_json_placeholder import AsyncJsonPlaceholderExtractor
from .json_placeholder import JsonPlaceholderExtractor

__all__ = ["AsyncJsonPlaceholderExtractor", "JsonPlaceholderExtractor"]
