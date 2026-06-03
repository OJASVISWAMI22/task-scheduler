import logging
from uuid import UUID,uuid4
from datetime import datetime, timezone

from fastapi import APIRouter,Depends, HTTPException

from app.models import ProcessResponse,ProcessRequest,StatusResponse
from app.dependencies import get_db,get_redis
from app.constants import QUEUE_MAP


router = APIRouter()

logger = logging.getLogger("my_app")

@router.get("/status/{request_id}")
async def get_request_status(request_id:UUID,db = Depends(get_db)):

  """
  GET /status/{request_id}
  Fetch status of any task from database.
  Returns task status, output and processing time as it's status .
  """

  query = """
    SELECT r.id, r.status, r.created_at, res.output_data, res.processing_time, res.processed_at
    FROM requests r
    LEFT JOIN results res ON res.request_id = r.id
    WHERE r.id = $1
    """
  
  try:
    logger.info("Getting user request:%s 's state from database",request_id)
    postgres = await db.fetchrow(query,request_id)
    logger.info("State fetch successful for request_id: %s",request_id)
  except Exception as e:
    logger.error("Failed to get request : %s from database",request_id)
    raise HTTPException(500, detail="Database error")
  
  if not postgres:
      raise HTTPException(404, detail="Request not found")
  
  return StatusResponse(status=postgres["status"], output_data=postgres["output_data"], processing_ms=postgres["processing_time"], created_at=postgres["created_at"], processed_at=postgres["processed_at"])



@router.post("/process")
async def post_request(body : ProcessRequest,
                       db = Depends(get_db),
                       redis = Depends(get_redis)):
  """
  POST /process
  Accept user task request, insert into DB and push to Redis priority queue.
  Returns request_id and PENDING status.
  """

  request_id = uuid4()
  time_now = datetime.now(timezone.utc)

  try:
    logger.info("Inserting user request from user_id:%s into db ",body.user_id)

    await db.execute(
    "INSERT INTO requests (id, user_id, user_name, payload, operation, priority, status, created_at, updated_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
    request_id, body.user_id, body.user_name,
    body.payload, body.operation, body.priority,
    "pending", time_now, time_now)

    logger.info("Db Entry successful for userId:%s",body.user_id)

  except Exception as e:
    logger.error("Failed to insert user request from user_id: %s",body.user_id)
    raise HTTPException(500)
  
  queue_name = QUEUE_MAP[body.priority]

  try:
    logger.info("Pushing request id:%s in Redis",request_id)
    await redis.lpush(queue_name,str(request_id))
    logger.info("Request : %s successfully pushed into Redis",request_id)
  except Exception as e:
    logger.error("Unable to push request id:%s into redis",request_id)
    raise RuntimeError
  
  return ProcessResponse(request_id=request_id,
                         status="pending", message="Task accepted")
  



  
