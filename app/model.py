from datetime import datetime
from pydantic import BaseModel,Field,field_validator,ConfigDict
from typing import Optional
from uuid import UUID

from app.constants import Operation,TaskStatus,PriorityLevel

class BaseSchema(BaseModel):
  model_config=ConfigDict(str_strip_whitespace=True,use_enum_values=True
                          ,validate_assignment=True)

class BaseRequest(BaseSchema):
  user_id:str = Field(pattern=r"^usr_[a-zA-Z0-9]{3,}$")
  user_name:str = Field(pattern=r"^[a-zA-Z0-9@-]{3,30}$")

class ProcessRequest(BaseRequest):
  payload:str = Field(min_length=1,max_length=10000)
  operation : Operation
  priority : PriorityLevel = Field(default=PriorityLevel.LOW)
