import asyncio
import json
import logging

import httpx

from app.database import get_pool, get_redis_pool
from app.constants import TaskStatus, QUEUE_HIGH, QUEUE_NORMAL, QUEUE_LOW, CPP_SERVICE_URL
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("my_app")

QUEUES = [QUEUE_HIGH, QUEUE_NORMAL, QUEUE_LOW]


async def process_task(request_id: str, payload: str, operation: str) -> None:
    """
    Process 1 task mark -> IN_PROGRESS, call C++ service, save result
    """
    db = get_pool()

    async with db.acquire() as conn:
        try:
            logger.info("Marking request id:%s as IN_PROGRESS", request_id)
            await conn.execute(
                "UPDATE requests SET status = $1, updated_at = NOW() WHERE id = $2",
                TaskStatus.IN_PROGRESS.value, request_id
            )
        except Exception as e:
            logger.error("Failed to update status for request id:%s — %s", request_id, e)
            return

    try:
        logger.info("Calling Cpp service for request id:%s", request_id)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CPP_SERVICE_URL}/process",
                json={"payload": payload, "operation": operation}
            )
        data = response.json()

        if "error" in data:
            raise Exception(data["error"])

        logger.info("Cpp service responded successfully for request id:%s", request_id)

    except Exception as e:
        logger.error("C++ service call failed for request id:%s — %s", request_id, e)
        async with db.acquire() as conn:
            await conn.execute(
                "UPDATE requests SET status = $1, updated_at = NOW() WHERE id = $2",
                TaskStatus.FAILED.value, request_id
            )
        return

    async with db.acquire() as conn:
        try:
            logger.info("Saving result for request id:%s", request_id)
            await conn.execute(
                """
                INSERT INTO results (id, request_id, output_data, processed_at, processing_ms)
                VALUES (gen_random_uuid(), $1, $2, NOW(), $3)
                """,
                request_id, data["output"], data["processing_ms"]
            )
            await conn.execute(
                "UPDATE requests SET status = $1, updated_at = NOW() WHERE id = $2",
                TaskStatus.DONE.value, request_id
            )
            logger.info("Request id:%s marked as DONE", request_id)
        except Exception as e:
            logger.error("Failed to save result for request id:%s — %s", request_id, e)
            await conn.execute(
                "UPDATE requests SET status = $1, updated_at = NOW() WHERE id = $2",
                TaskStatus.FAILED.value, request_id
            )


async def worker() -> None:
    """
    Main worker loop track Redis queues in priority order
    Pick up task and processes it
    """
    redis = get_redis_pool()
    logger.info("Worker started — listening on queues: %s", QUEUES)

    while True:
        try:
            item = await redis.blpop(QUEUES, timeout=5)
            if not item:
                continue

            _, data = item
            task = json.loads(data)
            logger.info("Picked up task — request id:%s", task["request_id"])

            await process_task(task["request_id"], task["payload"], task["operation"])

        except Exception as e:
            logger.error("Worker loop error: %s", e)


if __name__ == "__main__":
    asyncio.run(worker())