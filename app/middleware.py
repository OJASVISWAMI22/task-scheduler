from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.constants import RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS
from app.database import get_redis_pool
class RateLimitMiddleware(BaseHTTPMiddleware):

  """"
  Middleware to enforce rate limit on request sent by each user
  Blocks user if no of request are more than set threshold
  """

  async def dispatch(self,request:Request, call_next) -> Response:
    user_id = request.headers.get("x-user-id")

    if user_id is None:
      return JSONResponse({"error":"User Id not passed. Can not proceed with request."},status_code=400)
    
    redis_pool=get_redis_pool()

    key = f"rate_limit:{user_id}"

    request_count=  await redis_pool.get(key)

    if request_count is None:

      await redis_pool.incr(key)
      await redis_pool.expire(key, RATE_LIMIT_WINDOW_SECONDS)
    elif int(request_count) >= RATE_LIMIT_MAX_REQUESTS:

      time_remaining = await redis_pool.ttl(key)
      return JSONResponse({"error":"Rate Limit Exceeded",
                           "retry_after_seconds":time_remaining},status_code=429)
    else:
      await redis_pool.incr(key)
      
    return await call_next(request)