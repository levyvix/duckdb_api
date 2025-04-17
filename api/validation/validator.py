"""
Data validation for JSON Placeholder API data.
"""

from typing import Any, ClassVar, TypeVar

import duckdb
from loguru import logger
from pydantic import BaseModel, ValidationError

from .models import Album, Comment, Photo, Post, Todo, User
from .schema import DuckDBSchema

T = TypeVar("T", bound=BaseModel)


class DataValidator:
    """Data validator for JSON Placeholder API data."""

    MODEL_MAPPING: ClassVar[dict[str, type[BaseModel]]] = {
        "users": User,
        "posts": Post,
        "comments": Comment,
        "todos": Todo,
        "albums": Album,
        "photos": Photo,
    }

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        """
        Initialize the data validator.

        Args:
            conn: DuckDB connection
        """
        self.conn = conn
        self.schema_validator = DuckDBSchema()

    def validate_data(self, table_name: str, data: dict[str, Any] | list[dict[str, Any]]) -> list[BaseModel]:
        """
        Validate data against the corresponding Pydantic model.

        Args:
            table_name: Name of the table/model to validate against
            data: Data to validate (single dict or list of dicts)

        Returns:
            List[BaseModel]: List of validated model instances

        Raises:
            ValueError: If table_name is unknown or data validation fails
        """
        if table_name not in self.MODEL_MAPPING:
            raise ValueError(f"Unknown table: {table_name}")

        model_class = self.MODEL_MAPPING[table_name]

        # Convert single dict to list
        if isinstance(data, dict):
            data = [data]

        validated_data = []

        for item in data:
            try:
                validated_item = model_class(**item)
                validated_data.append(validated_item)
            except ValidationError as e:
                logger.error(f"Validation error for {table_name}: {e}")
                raise ValueError(f"Data validation failed for {table_name}: {e}") from e

        return validated_data

    def validate_and_save(self, table_name: str, data: dict[str, Any] | list[dict[str, Any]]) -> bool:
        """
        Validate data and save to DuckDB if valid.

        Args:
            table_name: Name of the table to save to
            data: Data to validate and save

        Returns:
            bool: True if validation and save successful, False otherwise
        """
        try:
            # Validate schema first
            if not self.schema_validator.validate_schema(self.conn, table_name):
                return False

            # Validate data
            validated_data = self.validate_data(table_name, data)

            # Convert validated models to dicts for insertion
            data_dicts = [model.model_dump() for model in validated_data]

            # Insert data
            if data_dicts:
                placeholders = ", ".join(["?" for _ in range(len(data_dicts[0]))])
                columns = ", ".join(data_dicts[0].keys())

                for data_dict in data_dicts:
                    values = tuple(data_dict.values())
                    self.conn.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)

                logger.info(f"Successfully saved {len(data_dicts)} records to {table_name}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to validate and save data to {table_name}: {e}")
            return False

    def validate_relationships(self, table_name: str, data: dict[str, Any] | list[dict[str, Any]]) -> bool:
        """
        Validate foreign key relationships.

        Args:
            table_name: Name of the table to validate
            data: Data to validate relationships for

        Returns:
            bool: True if relationships are valid, False otherwise
        """
        try:
            if isinstance(data, dict):
                data = [data]

            for item in data:
                # Check user relationships
                if "userId" in item:
                    result = self.conn.execute("SELECT COUNT(*) FROM users WHERE id = ?", [item["userId"]]).fetchone()
                    if result is None:
                        return False
                    count = result[0]

                    if count == 0:
                        logger.error(f"Invalid userId {item['userId']} in {table_name}")
                        return False

                # Check post relationships
                if "postId" in item:
                    result = self.conn.execute("SELECT COUNT(*) FROM posts WHERE id = ?", [item["postId"]]).fetchone()
                    if result is None:
                        return False
                    count = result[0]

                    if count == 0:
                        logger.error(f"Invalid postId {item['postId']} in {table_name}")
                        return False

                # Check album relationships
                if "albumId" in item:
                    result = self.conn.execute("SELECT COUNT(*) FROM albums WHERE id = ?", [item["albumId"]]).fetchone()
                    if result is None:
                        return False
                    count = result[0]

                    if result == 0:
                        logger.error(f"Invalid albumId {item['albumId']} in {table_name}")
                        return False

            return True

        except Exception as e:
            logger.error(f"Failed to validate relationships for {table_name}: {e}")
            return False
