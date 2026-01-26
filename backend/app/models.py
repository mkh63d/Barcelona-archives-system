from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArchiveBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    date: str

class ArchiveCreate(ArchiveBase):
    pass

class ArchiveUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    date: Optional[str] = None

class Archive(ArchiveBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
