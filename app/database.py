import asyncpg
import logging
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

# Module level SINGLETON POOL for DB connection
_pool: Optional[asyncpg.Pool] = None


async def init_db_pool() -> None:
    """
    To create pool on app startup

    Fetch variable from .env file, Only one instance is allowed
    to pursue consistency and raise error on failure
    """
    global _pool
    if _pool is None:
        try:
            _pool = await asyncpg.create_pool(
                dsn=os.getenv("DATABASE_URL"),
                min_size=int(os.getenv("MIN_POOL_SIZE",2)),
                max_size=int(os.getenv("MAX_POOL_SIZE",10)),
                command_timeout=int(os.getenv("POOL_CMD_TIMEOUT",60  )),
            )
            # Pool created successfully
            logger.info("Database Pool initialized successfully")
        except Exception as e:
            # Failed to initialize pool
            logger.error("Failed to initialize database pool: %s", e)
            raise


async def close_db_pool() -> None:
    """
    To shutdown app on shutdown in graccefull manner

    Close all DB connection and set _pool to none
    so that get_pool does not return false state
    """
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        # All connections are closed
        logger.info("Database pool closed")


def get_pool() -> asyncpg.Pool:
    """
    Return current active pool

    TO be used by dependancy.py for eacch request and raise error if on startup pool was not
    initialized
    """
    if _pool is None:
        # Raise Error if pool not initialized at startup of app
        raise RuntimeError("Database is not initialized")
    return _pool
