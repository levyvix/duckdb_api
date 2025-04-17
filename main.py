import asyncio

from api.async_json_placeholder import AsyncJsonPlaceholderExtractor
from utils.log import get_logger

logger = get_logger()


async def main() -> None:
    logger.info("Starting data extraction from APIs...")

    posts_extractor = AsyncJsonPlaceholderExtractor(
        url_api="https://jsonplaceholder.typicode.com/posts",
        tabela_destino="posts",
        parametros={"page": "1"},
    )
    await posts_extractor.run()
    posts_extractor.check_table()

    users_extractor = AsyncJsonPlaceholderExtractor(
        url_api="https://jsonplaceholder.typicode.com/users",
        tabela_destino="users",
        parametros={"page": "1"},
    )
    await users_extractor.run()
    users_extractor.check_table()


if __name__ == "__main__":
    asyncio.run(main())
