from typing import Any, ClassVar, TypeVar

import duckdb
from loguru import logger
from pydantic import BaseModel, ValidationError

from .models import Album, Comment, Photo, Post, TestModel, Todo, User
from .schema import DuckDBSchema

T = TypeVar("T", bound=BaseModel)


class DataValidator:
    MODEL_MAPPING: ClassVar[dict[str, type[BaseModel]]] = {
        "users": User,
        "posts": Post,
        "comments": Comment,
        "todos": Todo,
        "albums": Album,
        "photos": Photo,
        "test_table": TestModel,
    }

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn
        self.schema_validator = DuckDBSchema()

    def validate_data(self, table_name: str, data: dict[str, Any] | list[dict[str, Any]]) -> list[BaseModel]:
        if table_name not in self.MODEL_MAPPING:
            raise ValueError(f"Unknown table: {table_name}")

        model_class = self.MODEL_MAPPING[table_name]

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
        try:
            if not self.schema_validator.validate_schema(self.conn, table_name):
                return False

            validated_data = self.validate_data(table_name, data)
            data_dicts = [model.model_dump() for model in validated_data]

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
        try:
            if isinstance(data, dict):
                data = [data]

            for item in data:
                if "userId" in item:
                    result = self.conn.execute("SELECT COUNT(*) FROM users WHERE id = ?", [item["userId"]]).fetchone()
                    if result is None:
                        return False
                    count = result[0]

                    if count == 0:
                        logger.error(f"Invalid userId {item['userId']} in {table_name}")
                        return False

                if "postId" in item:
                    result = self.conn.execute("SELECT COUNT(*) FROM posts WHERE id = ?", [item["postId"]]).fetchone()
                    if result is None:
                        return False
                    count = result[0]

                    if count == 0:
                        logger.error(f"Invalid postId {item['postId']} in {table_name}")
                        return False

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
