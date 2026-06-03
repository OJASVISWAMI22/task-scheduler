import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db_pool, init_redis_pool, close_db_pool, close_redis_pool, get_pool, get_redis_pool
from app.logging_config import setup_logging
from app.middleware import RateLimitMiddleware
from app.routes import router

setup_logging()

logger = logging.getLogger("my_app")

@asynccontextmanager
async def lifespan(app:FastAPI):
  """
  Generator to persist connections required across app lifespan.
  """
  logger.info("Starting FastAPI app.")
  await init_db_pool()
  await init_redis_pool()

  db_connection = get_pool()
  redis_connection = get_redis_pool()

  app.state.db = db_connection
  app.state.redis = redis_connection

  yield 

  logger.info("Shutdown initiated. Closing connections...")
  await close_redis_pool()
  await close_db_pool()
  logger.info("SHUTDOWN Recieved! Closing app")



app = FastAPI(lifespan=lifespan)

app.add_middleware(RateLimitMiddleware)
app.include_router(router)