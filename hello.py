import sys
from typing import Dict, Optional

import duckdb
import pandas as pd
import requests
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO")


def extrair_api_e_salvar_duckdb(
    url_api: str,
    tabela_destino: str,
    caminho_duckdb: str,
    parametros: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    metodo: str = "GET",
) -> None:
    """
    Extrai dados de uma API REST e armazena em uma tabela DuckDB.

    Args:
        url (str): URL da API a ser consultada.
        tabela (str): Nome da tabela para armazenar os dados no DuckDB.
        caminho_duckdb (str): Caminho do arquivo .duckdb onde será salvo.
        parametros (Optional[Dict[str, str]]): Parâmetros da query string para a API (ex: {"page": "1"}).
        headers (Optional[Dict[str, str]]): Headers HTTP a serem usados na requisição (ex: autenticação).
        metodo (str): Método HTTP, normalmente "GET" ou "POST". Default: "GET".

    Returns:
        None

    Exemplos:
        >>> extrair_api_e_salvar_duckdb(
        ...     url="https://jsonplaceholder.typicode.com/posts",
        ...     tabela="posts",
        ...     caminho_duckdb="dados.duckdb"
        ... )

        >>> extrair_api_e_salvar_duckdb(
        ...     url="https://api.exemplo.com/data",
        ...     tabela="api_data",
        ...     caminho_duckdb="meu_banco.duckdb",
        ...     headers={"Authorization": "Bearer token123"}
        ... )
    """
    logger.info(f"Iniciando requisição para a API: {url_api}")
    try:
        response = requests.request(
            method=metodo, url=url_api, params=parametros, headers=headers
        )
        response.raise_for_status()
        dados_json = response.json()
        logger.info("Dados recebidos com sucesso da API.")

        df = pd.DataFrame(dados_json)
        logger.info(
            f"DataFrame criado com {len(df)} registros e {len(df.columns)} colunas."
        )

        conn = duckdb.connect(caminho_duckdb)
        conn.execute(f"DROP TABLE IF EXISTS {tabela_destino};")  # Drop existing table
        conn.execute(
            f"CREATE TABLE {tabela_destino} AS SELECT * FROM df;"
        )  # Create new table with data
        conn.close()

        logger.success(
            f"Dados inseridos com sucesso na tabela '{tabela_destino}' do banco '{caminho_duckdb}'."
        )

    except requests.RequestException as e:
        logger.error(f"Erro na requisição HTTP: {e}")
    except Exception as e:
        logger.error(f"Erro ao processar ou salvar dados: {e}")


if __name__ == "__main__":
    logger.info("Iniciando extração de dados das APIs...")
    DUCKDB_PATH = "dados.duckdb"

    extrair_api_e_salvar_duckdb(
        url_api="https://jsonplaceholder.typicode.com/posts",
        tabela_destino="posts",
        caminho_duckdb=DUCKDB_PATH,
        parametros={"page": "1"},
        headers={"Authorization": "Bearer token123"},
        metodo="GET",
    )

    extrair_api_e_salvar_duckdb(
        url_api="https://jsonplaceholder.typicode.com/users",
        tabela_destino="users",
        caminho_duckdb=DUCKDB_PATH,
        parametros={"page": "1"},
        headers={"Authorization": "Bearer token123"},
        metodo="GET",
    )
