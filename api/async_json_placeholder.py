from typing import Dict, Optional

import aiohttp
import duckdb
import pandas as pd

from utils.log import get_logger

logger = get_logger()

# Constants
DEFAULT_METHOD = "GET"
DUCKDB_PATH = "dados.duckdb"


class AsyncJsonPlaceholderExtractor:
    """
    An asynchronous class to extract data from REST APIs and store it in DuckDB tables.

    This class handles the entire process of fetching data from an API asynchronously,
    converting it to a pandas DataFrame, and storing it in a DuckDB database.

    Attributes:
        url_api (str): The URL of the API to query
        tabela_destino (str): Name of the table to store data in DuckDB
        caminho_duckdb (str): Path to the .duckdb file
        parametros (Optional[Dict[str, str]]): Query string parameters
        headers (Optional[Dict[str, str]]): HTTP headers for the request
        metodo (str): HTTP method (default: "GET")
    """

    def __init__(
        self,
        url_api: str,
        tabela_destino: str,
        caminho_duckdb: str = DUCKDB_PATH,
        parametros: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        metodo: str = DEFAULT_METHOD,
    ) -> None:
        self.url_api = url_api
        self.tabela_destino = tabela_destino
        self.caminho_duckdb = caminho_duckdb
        self.parametros = parametros or {}
        self.headers = headers or {}
        self.metodo = metodo.upper()

    async def extract(self) -> pd.DataFrame:
        """
        Extract data from the API asynchronously and return it as a pandas DataFrame.

        Returns:
            pd.DataFrame: The extracted data, or an empty DataFrame if an error occurs
        """
        try:
            session = aiohttp.ClientSession()
            async with session:
                response = await session.request(
                    method=self.metodo,
                    url=self.url_api,
                    params=self.parametros,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                )
                await response.raise_for_status()
                dados_json = await response.json()
                logger.info(f"Successfully received data from {self.url_api}")

                df = pd.DataFrame(dados_json)
                logger.info(
                    f"Created DataFrame with {len(df)} records and {len(df.columns)} columns"
                )
                return df

        except aiohttp.ClientError as e:
            logger.error(f"HTTP request error: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            return pd.DataFrame()

    def save(self, dataframe: pd.DataFrame) -> bool:
        """
        Save the DataFrame to DuckDB.

        Args:
            dataframe (pd.DataFrame): The DataFrame to save

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with duckdb.connect(self.caminho_duckdb) as conn:
                conn.register("dataframe", dataframe)
                conn.execute(f"DROP TABLE IF EXISTS {self.tabela_destino}")
                conn.execute(
                    f"CREATE TABLE {self.tabela_destino} AS SELECT * FROM dataframe"
                )
            logger.success(f"Successfully saved data to table '{self.tabela_destino}'")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False

    async def run(self) -> bool:
        """
        Execute the complete extraction and saving process asynchronously.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            dataframe = await self.extract()
            if dataframe.empty:
                logger.warning("No data to save - DataFrame is empty")
                return False
            return self.save(dataframe)
        except Exception as e:
            logger.error(f"Error in extraction and saving process: {e}")
            return False

    def check_table(self) -> bool:
        """
        Verify if the table exists and is accessible.

        Returns:
            bool: True if table exists and is accessible, False otherwise
        """
        try:
            with duckdb.connect(self.caminho_duckdb) as conn:
                conn.execute(f"describe {self.tabela_destino}")
                logger.info(f"Table '{self.tabela_destino}' exists and is accessible")
                return True
        except Exception as e:
            logger.error(f"Error checking table '{self.tabela_destino}': {e}")
            return False
