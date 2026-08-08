from typing import Optional, Any, Dict
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[Any] = None
    code: Optional[str] = None
