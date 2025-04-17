from unittest.mock import Mock

import pandas as pd
import requests
from requests import Response

from api.json_placeholder import JsonPlaceholderExtractor


def test_init():
    """Test JsonPlaceholderExtractor initialization."""
    extractor = JsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
    )
    assert extractor.url_api == "https://test.api/posts"
    assert extractor.tabela_destino == "test_table"
    assert extractor.metodo == "GET"
    assert extractor.parametros == {}
    assert extractor.headers == {}


def test_extract_success(mocker, sample_data):
    """Test successful data extraction."""
    mock_response = Mock(spec=Response)
    mock_response.json.return_value = sample_data
    mock_response.raise_for_status.return_value = None

    mocker.patch("requests.request", return_value=mock_response)

    extractor = JsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
    )

    result = extractor.extract()
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_data)
    assert not result.empty


def test_extract_http_error(mocker):
    """Test extraction with HTTP error."""
    mocker.patch(
        "requests.request", side_effect=requests.RequestException("HTTP Error")
    )

    extractor = JsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
    )

    result = extractor.extract()
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_save_success(temp_db_path, sample_df):
    """Test successful data saving."""
    extractor = JsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
        caminho_duckdb=temp_db_path,
    )

    success = extractor.save(sample_df)
    assert success is True


def test_save_error(temp_db_path):
    """Test saving with invalid DataFrame."""
    extractor = JsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
        caminho_duckdb=temp_db_path,
    )

    # Try to save an invalid DataFrame
    invalid_df = "not a dataframe"
    success = extractor.save(invalid_df)  # type: ignore
    assert success is False


def test_run_success(mocker, sample_data, temp_db_path):
    """Test successful complete run."""
    mock_response = Mock(spec=Response)
    mock_response.json.return_value = sample_data
    mock_response.raise_for_status.return_value = None

    mocker.patch("requests.request", return_value=mock_response)

    extractor = JsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
        caminho_duckdb=temp_db_path,
    )

    success = extractor.run()
    assert success is True


def test_run_empty_data(mocker, temp_db_path):
    """Test run with empty data response."""
    mock_response = Mock(spec=Response)
    mock_response.json.return_value = []
    mock_response.raise_for_status.return_value = None

    mocker.patch("requests.request", return_value=mock_response)

    extractor = JsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
        caminho_duckdb=temp_db_path,
    )

    success = extractor.run()
    assert success is False


def test_check_table_success(temp_db_path, sample_df):
    """Test successful table check."""
    extractor = JsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
        caminho_duckdb=temp_db_path,
    )

    # First save some data
    extractor.save(sample_df)

    # Then check the table
    exists = extractor.check_table()
    assert exists is True


def test_check_table_nonexistent(temp_db_path):
    """Test checking nonexistent table."""
    extractor = JsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="nonexistent_table",
        caminho_duckdb=temp_db_path,
    )

    exists = extractor.check_table()
    assert exists is False
