from app.database import get_pool,get_redis_pool


async def get_db():
  """
  Method to pre fetch db connection in request
  """
  db=get_pool()
  async with db.acquire() as connection:
    yield connection
 
async def get_redis():
  """
  Method to pre  fetch redis connection object in between request 
  """
  redis=get_redis_pool()
  yield redis