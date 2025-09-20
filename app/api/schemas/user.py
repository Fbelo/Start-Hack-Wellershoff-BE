"""
Pydantic schemas for User API
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict
from datetime import datetime

class UserModel(BaseModel):
    """
    Pydantic model for application users
    """
    id: Optional[int] = None
    name: str
    email: EmailStr
    profile_picture: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    news: Optional[list] = None
    
    class Config:
        from_attributes = True  # Allows the model to be created from an ORM model
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "profile_picture": "https://example.com/profile/123.jpg",
                "preferences": {
                    "daily_news_digest": True,
                    "portfolio_alerts": True,
                    "market_updates": False
                }
            }
        }

# Create model for creating new users
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    profile_picture: Optional[str] = None

# Update model for updating users
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None
    last_login: Optional[datetime] = None