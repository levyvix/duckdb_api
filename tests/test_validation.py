"""
Tests for the validation system.
"""

import duckdb
import pytest

from api.validation.models import Post, User
from api.validation.schema import DuckDBSchema
from api.validation.validator import DataValidator


@pytest.fixture
def db_connection():
    """Create a test database connection."""
    conn = duckdb.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def validator(db_connection):
    """Create a test validator instance."""
    return DataValidator(db_connection)


def test_valid_user_data(validator):
    """Test validation of valid user data."""
    valid_user = {
        "id": 1,
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "address": {
            "street": "123 Main St",
            "suite": "Apt 4",
            "city": "Anytown",
            "zipcode": "12345",
            "geo": {"lat": "-37.3159", "lng": "81.1496"},
        },
        "phone": "1-234-567-8900",
        "website": "example.com",
        "company": {"name": "Example Corp", "catchPhrase": "Making examples since 2024", "bs": "example business"},
    }

    validated = validator.validate_data("users", valid_user)
    assert len(validated) == 1
    assert isinstance(validated[0], User)
    assert validated[0].name == "John Doe"


def test_invalid_user_data(validator):
    """Test validation of invalid user data."""
    invalid_user = {
        "id": 1,
        "name": "",  # Invalid: empty name
        "username": "johndoe",
        "email": "invalid-email",  # Invalid email format
        "address": {"street": "123 Main St", "city": "Anytown"},
        "phone": "1-234-567-8900",
        "website": "example.com",
        "company": {"name": "Example Corp"},
    }

    with pytest.raises(ValueError):
        validator.validate_data("users", invalid_user)


def test_valid_post_data(validator):
    """Test validation of valid post data."""
    valid_post = {"id": 1, "userId": 1, "title": "Test Post", "body": "This is a test post body"}

    validated = validator.validate_data("posts", valid_post)
    assert len(validated) == 1
    assert isinstance(validated[0], Post)
    assert validated[0].title == "Test Post"


def test_schema_creation(db_connection):
    """Test creation of database schema."""
    schema = DuckDBSchema()
    assert schema.create_all_tables(db_connection)

    # Verify tables were created
    result = db_connection.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
    """).fetchall()

    table_names = [r[0] for r in result]
    expected_tables = ["users", "posts"]

    for table in expected_tables:
        assert table in table_names


def test_relationship_validation(validator):
    """Test validation of relationships between entities."""
    # Create user first
    user_data = {
        "id": 1,
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "address": {
            "street": "123 Main St",
            "suite": "Apt 4",
            "city": "Anytown",
            "zipcode": "12345",
            "geo": {"lat": "-37.3159", "lng": "81.1496"},
        },
        "phone": "1-234-567-8900",
        "website": "example.com",
        "company": {"name": "Example Corp", "catchPhrase": "Making examples since 2024", "bs": "example business"},
    }

    assert validator.validate_and_save("users", user_data)

    # Test post with valid user relationship
    post_data = {"id": 1, "userId": 1, "title": "Test Post", "body": "This is a test post body"}

    assert validator.validate_relationships("posts", post_data)

    # Test post with invalid user relationship
    invalid_post = {
        "id": 2,
        "userId": 999,  # Non-existent user
        "title": "Test Post",
        "body": "This is a test post body",
    }

    assert not validator.validate_relationships("posts", invalid_post)


def test_batch_validation(validator):
    """Test validation of multiple records at once."""
    users = [
        {
            "id": 1,
            "name": "John Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "address": {
                "street": "123 Main St",
                "suite": "Apt 4",
                "city": "Anytown",
                "zipcode": "12345",
                "geo": {"lat": "-37.3159", "lng": "81.1496"},
            },
            "phone": "1-234-567-8900",
            "website": "example.com",
            "company": {"name": "Example Corp", "catchPhrase": "Making examples since 2024", "bs": "example business"},
        },
        {
            "id": 2,
            "name": "Jane Doe",
            "username": "janedoe",
            "email": "jane@example.com",
            "address": {
                "street": "456 Oak St",
                "suite": "Unit 8",
                "city": "Somewhere",
                "zipcode": "67890",
                "geo": {"lat": "40.7128", "lng": "-74.0060"},
            },
            "phone": "1-234-567-8901",
            "website": "example.org",
            "company": {
                "name": "Another Corp",
                "catchPhrase": "Making more examples since 2024",
                "bs": "more business",
            },
        },
    ]

    validated = validator.validate_data("users", users)
    assert len(validated) == 2
    assert all(isinstance(user, User) for user in validated)
    assert validator.validate_and_save("users", users)
