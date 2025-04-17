import duckdb
import pandas as pd
import requests

from utils.log import get_logger, log_error_with_context

logger = get_logger({"module": "json_placeholder"})

# Constants
DEFAULT_METHOD = "GET"
DUCKDB_PATH = "dados.duckdb"


class JsonPlaceholderExtractor:
    """
    A class to extract data from REST APIs and store it in DuckDB tables.

    This class handles the entire process of fetching data from an API,
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

    def extract(self) -> pd.DataFrame:
        """
        Extract data from the API and return it as a pandas DataFrame.

        Returns:
            pd.DataFrame: The extracted data, or an empty DataFrame if an error occurs
        """
        try:
            response = requests.request(
                method=self.metodo,
                url=self.url_api,
                params=self.parametros,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            dados_json = response.json()
            logger.info(
                "Successfully received data from API",
                extra={
                    "url": self.url_api,
                    "method": self.metodo,
                    "params": self.parametros,
                },
            )

            df = pd.DataFrame(dados_json)
            logger.info(
                "Created DataFrame from API data",
                extra={
                    "rows": len(df),
                    "columns": len(df.columns),
                    "table": self.tabela_destino,
                },
            )
            return df

        except requests.RequestException as e:
            log_error_with_context(
                e,
                {
                    "url": self.url_api,
                    "method": self.metodo,
                    "params": self.parametros,
                    "error_type": "http_error",
                },
            )
            return pd.DataFrame()
        except Exception as e:
            log_error_with_context(
                e,
                {
                    "url": self.url_api,
                    "method": self.metodo,
                    "error_type": "processing_error",
                },
            )
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
                conn.execute(f"CREATE TABLE {self.tabela_destino} AS SELECT * FROM dataframe")
            logger.success(
                "Successfully saved data to DuckDB",
                extra={
                    "table": self.tabela_destino,
                    "rows": len(dataframe),
                    "database": self.caminho_duckdb,
                },
            )
            return True
        except Exception as e:
            log_error_with_context(
                e,
                {
                    "table": self.tabela_destino,
                    "database": self.caminho_duckdb,
                    "error_type": "database_error",
                },
            )
            return False

    def run(self) -> bool:
        """
        Execute the complete extraction and saving process.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            dataframe = self.extract()
            if dataframe.empty:
                logger.warning(
                    "No data to save - DataFrame is empty",
                    extra={
                        "table": self.tabela_destino,
                        "url": self.url_api,
                    },
                )
                return False
            return self.save(dataframe)
        except Exception as e:
            log_error_with_context(
                e,
                {
                    "table": self.tabela_destino,
                    "url": self.url_api,
                    "error_type": "pipeline_error",
                },
            )
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
                logger.info(
                    "Table verification successful",
                    extra={
                        "table": self.tabela_destino,
                        "database": self.caminho_duckdb,
                        "status": "accessible",
                    },
                )
                return True
        except Exception as e:
            log_error_with_context(
                e,
                {
                    "table": self.tabela_destino,
                    "database": self.caminho_duckdb,
                    "error_type": "table_check_error",
                },
            )
            return False
