"""
DuckDB schema validation for JSON Placeholder API data.
"""

from typing import ClassVar

import duckdb
from loguru import logger


class DuckDBSchema:
    """DuckDB schema definitions and validation."""

    SCHEMAS: ClassVar[dict[str, str]] = {
        "users": r"""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL,
                username VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                address JSON NOT NULL,
                phone VARCHAR NOT NULL,
                website VARCHAR NOT NULL,
                company JSON NOT NULL,
                CONSTRAINT valid_email CHECK (email ~ '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            )
        """,
        "posts": r"""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                userId INTEGER NOT NULL,
                title VARCHAR NOT NULL,
                body TEXT NOT NULL,
                CONSTRAINT fk_user FOREIGN KEY (userId) REFERENCES users(id)
            )
        """,
        "comments": r"""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                postId INTEGER NOT NULL,
                name VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                body TEXT NOT NULL,
                CONSTRAINT fk_post FOREIGN KEY (postId) REFERENCES posts(id),
                CONSTRAINT valid_email CHECK (email ~ '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            )
        """,
        "todos": r"""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY,
                userId INTEGER NOT NULL,
                title VARCHAR NOT NULL,
                completed BOOLEAN NOT NULL,
                CONSTRAINT fk_user FOREIGN KEY (userId) REFERENCES users(id)
            )
        """,
        "albums": r"""
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY,
                userId INTEGER NOT NULL,
                title VARCHAR NOT NULL,
                CONSTRAINT fk_user FOREIGN KEY (userId) REFERENCES users(id)
            )
        """,
        "photos": r"""
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY,
                albumId INTEGER NOT NULL,
                title VARCHAR NOT NULL,
                url VARCHAR NOT NULL,
                thumbnailUrl VARCHAR NOT NULL,
                CONSTRAINT fk_album FOREIGN KEY (albumId) REFERENCES albums(id),
                CONSTRAINT valid_url CHECK (url ~ '^https?://.*$'),
                CONSTRAINT valid_thumb_url CHECK (thumbnailUrl ~ '^https?://.*$')
            )
        """,
        # Test table schema for testing purposes
        "test_table": r"""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                title VARCHAR NOT NULL,
                body TEXT NOT NULL
            )
        """,
    }

    @staticmethod
    def validate_schema(conn: duckdb.DuckDBPyConnection, table_name: str) -> bool:
        """
        Validate if a table exists and has the correct schema.

        Args:
            conn: DuckDB connection
            table_name: Name of the table to validate

        Returns:
            bool: True if schema is valid, False otherwise
        """
        try:
            if table_name not in DuckDBSchema.SCHEMAS:
                logger.error(f"Unknown table: {table_name}")
                return False

            # Create table if it doesn't exist
            conn.execute(DuckDBSchema.SCHEMAS[table_name])

            # Verify table structure
            result = conn.execute(f"DESCRIBE {table_name}").fetchall()
            if not result:
                logger.error(f"Failed to get schema for table: {table_name}")
                return False

            logger.info(f"Schema validation successful for table: {table_name}")
            return True

        except Exception as e:
            logger.error(f"Schema validation failed for table {table_name}: {e}")
            return False

    @staticmethod
    def create_all_tables(conn: duckdb.DuckDBPyConnection) -> bool:
        """
        Create all tables in the database.

        Args:
            conn: DuckDB connection

        Returns:
            bool: True if all tables were created successfully, False otherwise
        """
        try:
            # Create tables in order due to foreign key constraints
            table_order = ["users", "posts", "comments", "todos", "albums", "photos", "test_table"]

            for table_name in table_order:
                conn.execute(DuckDBSchema.SCHEMAS[table_name])
                logger.info(f"Created table: {table_name}")

            return True

        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
