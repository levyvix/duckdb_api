"""
Validation package for JSON Placeholder API data.
"""

from .models import Post, User
from .schema import DuckDBSchema
from .validator import DataValidator

__all__ = ["DataValidator", "DuckDBSchema", "Post", "User"]
