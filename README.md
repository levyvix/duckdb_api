# DuckDB API

A Python application that extracts data from REST APIs and stores it efficiently in DuckDB, a fast analytical database. Features robust error handling, detailed logging, and type safety through static type checking.


## Features

- DuckDB data warehouse
- Data manipulation with Pandas
- Logging with Loguru
- HTTP requests handling
- Type checking support
- Comprehensive test suite with pytest

## Prerequisites

- Python 3.12 or higher
- uv package manager

## Installation

### Installing uv

First, install uv package manager:

```bash
pip install uv
```

### Setting up the project

1. Clone the repository:
```bash
git clone https://github.com/yourusername/duckdb-api.git
cd duckdb-api
```

2. Install dependencies:

For production use (without development dependencies):
```bash
uv sync --no-default-groups
```

For development (with all dependencies):
```bash
uv sync
```

## Running Tests

To run the test suite:

```bash
uv pip install pytest pytest-mock
pytest
```

For more verbose output:
```bash
pytest -v
```

To run specific test files:
```bash
pytest tests/test_json_placeholder.py
```

## Project Structure

```
duckdb-api/
├── api/           # API Extractor
├── utils/         # Utility functions (log)
├── logs/          # Log files (will appear when code runs)
├── tests/         # Test suite
├── main.py        # Main application entry point
├── dados.duckdb   # DuckDB database file (will appear when code runs)
└── pyproject.toml # Project configuration and dependencies (using UV)
```

## Dependencies

### Main Dependencies
- duckdb>=1.2.2
- loguru>=0.7.3
- pandas>=2.2.3
- requests>=2.32.3

### Development Dependencies
- pyright>=1.1.399
- pytest>=8.1.1
- pytest-mock>=3.12.0

