"""
Pydantic schemas for Source API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SourceBase(BaseModel):
    """
    Base Pydantic model for news sources
    """
    codename: str = Field(..., description="Unique code identifier for the source")
    name: str = Field(..., description="Display name of the news source")
    website: str = Field(..., description="Website URL of the news source")

class SourceCreate(SourceBase):
    """
    Pydantic model for creating news sources
    """
    pass

class SourceUpdate(BaseModel):
    """
    Pydantic model for updating news sources
    """
    codename: Optional[str] = Field(None, description="Unique code identifier for the source")
    name: Optional[str] = Field(None, description="Display name of the news source")
    website: Optional[str] = Field(None, description="Website URL of the news source")

class SourceModel(SourceBase):
    """
    Complete Pydantic model for news sources with database fields
    """
    id: int
    
    class Config:
        from_attributes = True