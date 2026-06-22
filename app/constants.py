# constants.py
# Constants across app and services are defined here
from enum import Enum
import os
from dotenv import load_dotenv
load_dotenv()
# Rate limiter
RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 20
RATE_LIMIT_KEY_PREFIX = "rate_limit:"

#Payload config
MAXIMUM_PAYLOAD_SIZE = 1000
# Redis queue
QUEUE_HIGH = "queue:high"
QUEUE_NORMAL = "queue:normal"
QUEUE_LOW = "queue:low"

# operation to be performed
class Operation(str,Enum):
  ENCRYPT = "Encrypt"
  HASH = "Hash"
  TRANSFORM = "Transform"
  DECRYPT = "Decrypt"
  DECOMPRESS = "Decompress"

# Task status
class TaskStatus(str,Enum):
  PENDING = "pending"
  DONE = "done"
  IN_PROGRESS = "in_progress"
  FAILED = "failed"

# Task Priority   
class PriorityLevel(int,Enum):
  LOW = 1
  MEDIUM = 2
  HIGH = 3


QUEUE_MAP = {
    PriorityLevel.LOW: QUEUE_LOW,
    PriorityLevel.MEDIUM: QUEUE_NORMAL,
    PriorityLevel.HIGH: QUEUE_HIGH,
}
# Cpp service url

CPP_SERVICE_URL = os.getenv("CPP_SERVICE_URL", "http://cpp_service:8080")

