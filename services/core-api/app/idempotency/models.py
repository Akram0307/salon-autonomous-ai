from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class IdempotencyKey(BaseModel):
    key: str
    response_code: int
    response_body: Any
    created_at: datetime
    expires_at: datetime
    
    class Config:
        arbitrary_types_allowed = True
