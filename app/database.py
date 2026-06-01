import asyncpg
import logging
import os
from typing import Optional
from dotenv import load_dotenv
from redis import asyncio as airedis
from app.logging_config import setup_logging

setup_logging()
# Load environment variables
load_dotenv()
logger = logging.getLogger("my_app")

# Module level SINGLETON POOL for DB connection
_pool: Optional[asyncpg.Pool] = None

_redis: Optional[airedis.Redis] = None

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
                command_timeout=int(os.getenv("POOL_CMD_TIMEOUT",60)),
            )
            # Pool created successfully
            logger.info("Database Pool initialized successfully")
        except Exception as e:
            # Failed to initialize pool
            logger.error("Failed to initialize database pool: %s", e)
            raise


async def close_db_pool() -> None:
    """
    To shutdown app on shutdown in gracefull manner

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

    TO be used by dependancy.py for each request and raise error if on startup pool was not initialized
    """
    if _pool is None:
        # Raise Error if pool not initialized at startup of app
        raise RuntimeError("Database is not initialized")
    return _pool

async def init_redis_pool() ->None:
    """
    Init function to initialize redis pool
    Run on app startup 
    """
    global _redis

    if _redis is None:
        try:
            _redis = await airedis.from_url(os.getenv("REDIS_URL"))
            logger.info("Redis Pool Initialized successful.")
        except Exception as e:
            logger.error("Failed to initialize redis connection: %s",e)
            raise

async def close_redis_pool() -> None:
    """
    Method to close redis pool gracefully while  exiting the app.
    """
    global _redis
    if _redis:
        await _redis.aclose()
        _redis=None
        logger.info("Redis Pool closed successfully.")

def get_redis_pool() -> airedis.Redis:
    """
    Getter method to be used in dependancy.py 
    To get pool using yeild on startup
    """
    if _redis is None:
        logger.error("Error! Redis pool  not found")
        raise RuntimeError("Redis pool was not initialized at startup")
    return _redis