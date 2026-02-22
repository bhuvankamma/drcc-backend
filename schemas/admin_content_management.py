# schemas.py

from pydantic import BaseModel
from datetime import datetime

class ContentBase(BaseModel):
    title: str
    type: str
    content: str

class ContentUpdate(BaseModel):
    content: str

class ContentResponse(ContentBase):
    id: int
    updated_at: datetime