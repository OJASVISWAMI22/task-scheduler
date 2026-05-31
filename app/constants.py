# constants.py
# Constants across app and services are defined here
from enum import Enum

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

# Cpp service url

CPP_SERVICE_URL = "http://localhost:8080"
