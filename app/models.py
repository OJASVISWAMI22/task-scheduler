from datetime import datetime
from pydantic import BaseModel,Field,ConfigDict
from typing import Optional
from uuid import UUID,uuid4

from app.constants import Operation,TaskStatus,PriorityLevel,MAXIMUM_PAYLOAD_SIZE,RATE_LIMIT_WINDOW_SECONDS

#Base class for schema defining
class BaseSchema(BaseModel):
  model_config=ConfigDict(str_strip_whitespace=True,use_enum_values=True
                          ,validate_assignment=True)

#base class to validate every request sent by user 
class BaseRequest(BaseSchema):
  user_id:str = Field(pattern=r"^usr_[a-zA-Z0-9]{3,}$",max_length=50)
  user_name:str = Field(pattern=r"^[a-zA-Z0-9@-]{3,30}$")

#To validate user data sent
class ProcessRequest(BaseRequest):
  payload:str = Field(min_length=1,max_length=MAXIMUM_PAYLOAD_SIZE)
  operation : Operation
  priority : PriorityLevel = Field(default=PriorityLevel.LOW)

# Base class for every response 
class BaseResponse(BaseSchema):
  request_id:UUID = Field(default_factory=uuid4) 

#Response of acceptancce of user request
class ProcessResponse(BaseResponse):
  status:TaskStatus = Field(TaskStatus.PENDING)
  message:str = "Task accepted"

# Response for task status after task completion or GET request
class StatusResponse(BaseResponse):
  status:TaskStatus 
  output_data:Optional[str] =Field(default=None,min_length=1)
  processing_ms:Optional[int] = Field(default=None)
  created_at:datetime 
  processed_at:Optional[datetime] = Field(default=None)   

# Rate Limiting Response 
# for user exceeding allowed no of request per minute
class RateLimitResponse(BaseSchema):
  error:str = "Rate limit exceeded"
  message:str = "You have tried exceeding 10 request per minute limit"
  retry_after_seconds:int = RATE_LIMIT_WINDOW_SECONDS