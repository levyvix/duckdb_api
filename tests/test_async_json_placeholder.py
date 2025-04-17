from unittest.mock import AsyncMock

import aiohttp
import pandas as pd
import pytest
from aiohttp import ClientResponse
from pytest_mock import MockerFixture

from api.async_json_placeholder import AsyncJsonPlaceholderExtractor


def test_init():
    """Test AsyncJsonPlaceholderExtractor initialization."""
    extractor = AsyncJsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
    )
    assert extractor.url_api == "https://test.api/posts"
    assert extractor.tabela_destino == "test_table"
    assert extractor.metodo == "GET"
    assert extractor.parametros == {}
    assert extractor.headers == {}


@pytest.mark.asyncio
async def test_extract_success(mocker: MockerFixture, sample_data):
    """Test successful async data extraction."""
    # Mock the response
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.raise_for_status = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_data)

    # Mock the session
    mock_session = AsyncMock(spec=aiohttp.ClientSession)
    mock_session.request = AsyncMock(return_value=mock_response)

    # Mock ClientSession creation
    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    extractor = AsyncJsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
    )

    result = await extractor.extract()
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_data)
    assert not result.empty


@pytest.mark.asyncio
async def test_extract_http_error(mocker: MockerFixture):
    """Test extraction with HTTP error."""
    # Mock the session to raise an error
    mock_session = AsyncMock(spec=aiohttp.ClientSession)
    mock_session.request.side_effect = aiohttp.ClientError("HTTP Error")

    # Mock ClientSession creation
    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    extractor = AsyncJsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
    )

    result = await extractor.extract()
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_save_success(temp_db_path, sample_df):
    """Test successful data saving."""
    extractor = AsyncJsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
        caminho_duckdb=temp_db_path,
    )

    success = extractor.save(sample_df)
    assert success is True


def test_save_error(temp_db_path):
    """Test saving with invalid DataFrame."""
    extractor = AsyncJsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
        caminho_duckdb=temp_db_path,
    )

    # Try to save an invalid DataFrame
    invalid_df = "not a dataframe"
    success = extractor.save(invalid_df)  # type: ignore
    assert success is False


@pytest.mark.asyncio
async def test_run_success(mocker: MockerFixture, sample_data, temp_db_path):
    """Test successful complete async run."""
    # Mock the response
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.raise_for_status = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_data)

    # Mock the session
    mock_session = AsyncMock(spec=aiohttp.ClientSession)
    mock_session.request = AsyncMock(return_value=mock_response)

    # Mock ClientSession creation
    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    extractor = AsyncJsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
        caminho_duckdb=temp_db_path,
    )

    success = await extractor.run()
    assert success is True


@pytest.mark.asyncio
async def test_run_empty_data(mocker: MockerFixture, temp_db_path):
    """Test run with empty data response."""
    # Mock the response
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.raise_for_status = AsyncMock()
    mock_response.json = AsyncMock(return_value=[])

    # Mock the session
    mock_session = AsyncMock(spec=aiohttp.ClientSession)
    mock_session.request = AsyncMock(return_value=mock_response)

    # Mock ClientSession creation
    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    extractor = AsyncJsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="test_table",
        caminho_duckdb=temp_db_path,
    )

    success = await extractor.run()
    assert success is False


def test_check_table_success(temp_db_path, sample_df):
    """Test successful table check."""
    extractor = AsyncJsonPlaceholderExtractor(
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
    extractor = AsyncJsonPlaceholderExtractor(
        url_api="https://test.api/posts",
        tabela_destino="nonexistent_table",
        caminho_duckdb=temp_db_path,
    )

    exists = extractor.check_table()
    assert exists is False
