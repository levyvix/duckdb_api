from api.json_placeholder import JsonPlaceholderExtractor
from utils.log import get_logger

logger = get_logger()


def main() -> None:
    logger.info("Starting data extraction from APIs...")

    posts_extractor = JsonPlaceholderExtractor(
        url_api="https://jsonplaceholder.typicode.com/posts",
        tabela_destino="posts",
        parametros={"page": "1"},
    )
    posts_extractor.run()
    posts_extractor.check_table()

    users_extractor = JsonPlaceholderExtractor(
        url_api="https://jsonplaceholder.typicode.com/users",
        tabela_destino="users",
        parametros={"page": "1"},
    )
    users_extractor.run()
    users_extractor.check_table()


if __name__ == "__main__":
    main()
