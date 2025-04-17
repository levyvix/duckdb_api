import asyncio

from api import AsyncJsonPlaceholderExtractor
from utils import get_logger

# Initialize logger with module context
logger = get_logger({"module": "main"})


async def main() -> None:
    """Main function to run the data extraction process."""
    logger.info(
        "Starting data extraction process",
        extra={
            "process": "data_extraction",
            "status": "starting",
        },
    )

    try:
        # Extract posts
        posts_extractor = AsyncJsonPlaceholderExtractor(
            url_api="https://jsonplaceholder.typicode.com/posts",
            tabela_destino="posts",
            parametros={"page": "1"},
        )
        posts_success = await posts_extractor.run()
        logger.info(
            "Posts extraction completed",
            extra={
                "table": "posts",
                "success": posts_success,
            },
        )

        if posts_success:
            posts_extractor.check_table()

        # Extract users
        users_extractor = AsyncJsonPlaceholderExtractor(
            url_api="https://jsonplaceholder.typicode.com/users",
            tabela_destino="users",
            parametros={"page": "1"},
        )
        users_success = await users_extractor.run()
        logger.info(
            "Users extraction completed",
            extra={
                "table": "users",
                "success": users_success,
            },
        )

        if users_success:
            users_extractor.check_table()

        logger.success(
            "Data extraction process completed",
            extra={
                "process": "data_extraction",
                "status": "completed",
                "posts_success": posts_success,
                "users_success": users_success,
            },
        )

    except Exception as e:
        logger.error(
            "Error in data extraction process",
            extra={
                "process": "data_extraction",
                "status": "failed",
                "error": str(e),
            },
        )
        raise


if __name__ == "__main__":
    asyncio.run(main())
