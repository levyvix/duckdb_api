import aiohttp
import duckdb
import pandas as pd
from typing import Any, cast

from api.validation.schema import DuckDBSchema
from api.validation.validator import DataValidator
from utils.log import get_logger, log_error_with_context

logger = get_logger({'module': 'async_json_placeholder'})

# Constants
DEFAULT_METHOD = 'GET'
DUCKDB_PATH = 'dados.duckdb'

class AsyncJsonPlaceholderExtractor:
    def __init__(
        self,
        url_api: str,
        tabela_destino: str,
        caminho_duckdb: str = DUCKDB_PATH,
        parametros: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        metodo: str = DEFAULT_METHOD,
    ) -> None:
        self.url_api = url_api
        self.tabela_destino = tabela_destino
        self.caminho_duckdb = caminho_duckdb
        self.parametros = parametros or {}
        self.headers = headers or {}
        self.metodo = metodo.upper()
        
        # Initialize validators
        self.conn = duckdb.connect(self.caminho_duckdb)
        self.data_validator = DataValidator(self.conn)
        self.schema_validator = DuckDBSchema()

    async def extract(self) -> pd.DataFrame:
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.request(
                    method=self.metodo,
                    url=self.url_api,
                    params=self.parametros,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                )
                await response.raise_for_status()
                dados_json = await response.json()
                logger.info(
                    'Successfully received data from API',
                    extra={
                        'url': self.url_api,
                        'method': self.metodo,
                        'params': self.parametros,
                    },
                )

                # Validate data before creating DataFrame
                try:
                    validated_data = self.data_validator.validate_data(self.tabela_destino, dados_json)
                    df = pd.DataFrame([model.model_dump() for model in validated_data])
                    logger.info(
                        'Created DataFrame from validated API data',
                        extra={
                            'rows': len(df),
                            'columns': len(df.columns),
                            'table': self.tabela_destino,
                        },
                    )
                    return df
                except ValueError as e:
                    logger.error(
                        'Data validation failed',
                        extra={
                            'table': self.tabela_destino,
                            'error': str(e),
                        },
                    )
                    return pd.DataFrame()

        except aiohttp.ClientError as e:
            log_error_with_context(
                e,
                {
                    'url': self.url_api,
                    'method': self.metodo,
                    'params': self.parametros,
                    'error_type': 'http_error',
                },
            )
            return pd.DataFrame()
        except Exception as e:
            log_error_with_context(
                e,
                {
                    'url': self.url_api,
                    'method': self.metodo,
                    'error_type': 'processing_error',
                },
            )
            return pd.DataFrame()

    def save(self, dataframe: pd.DataFrame) -> bool:
        try:
            # Validate schema before saving
            if not self.schema_validator.validate_schema(self.conn, self.tabela_destino):
                logger.error(
                    'Schema validation failed',
                    extra={
                        'table': self.tabela_destino,
                        'database': self.caminho_duckdb,
                    },
                )
                return False

            # Convert DataFrame to dict for validation
            data_dicts = cast(list[dict[str, Any]], dataframe.to_dict('records'))
            
            # Validate and save data using DataValidator
            success = self.data_validator.validate_and_save(self.tabela_destino, data_dicts)
            
            if success:
                logger.success(
                    'Successfully saved validated data to DuckDB',
                    extra={
                        'table': self.tabela_destino,
                        'rows': len(dataframe),
                        'database': self.caminho_duckdb,
                    },
                )
            return success

        except Exception as e:
            log_error_with_context(
                e,
                {
                    'table': self.tabela_destino,
                    'database': self.caminho_duckdb,
                    'error_type': 'database_error',
                },
            )
            return False

    async def run(self) -> bool:
        try:
            dataframe = await self.extract()
            if dataframe.empty:
                logger.warning(
                    'No data to save - DataFrame is empty',
                    extra={
                        'table': self.tabela_destino,
                        'url': self.url_api,
                    },
                )
                return False
            return self.save(dataframe)
        except Exception as e:
            log_error_with_context(
                e,
                {
                    'table': self.tabela_destino,
                    'url': self.url_api,
                    'error_type': 'pipeline_error',
                },
            )
            return False

    def check_table(self) -> bool:
        try:
            # Use schema validator for table check
            success = self.schema_validator.validate_schema(self.conn, self.tabela_destino)
            if success:
                logger.info(
                    'Table verification successful',
                    extra={
                        'table': self.tabela_destino,
                        'database': self.caminho_duckdb,
                        'status': 'accessible',
                    },
                )
            return success
        except Exception as e:
            log_error_with_context(
                e,
                {
                    'table': self.tabela_destino,
                    'database': self.caminho_duckdb,
                    'error_type': 'table_check_error',
                },
            )
            return False

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()