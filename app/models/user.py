from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from app.db.postgres.database import Base

# SQLAlchemy model for database operations
class User(Base):
    """
    SQLAlchemy model for users table
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    profile_picture = Column(String, nullable=True)
    preferences = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime, nullable=True)

# Pydantic model for API requests/responses
class UserModel(BaseModel):
    """
    Pydantic model for application users
    """
    id: Optional[int] = None
    name: str
    email: EmailStr
    profile_picture: Optional[str] = None
    preferences: Dict[str, bool] = Field(default_factory=dict)  # User preferences like notification settings
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
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
    preferences: Dict[str, bool] = Field(default_factory=dict)

# Update model for updating users
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None
    preferences: Optional[Dict[str, bool]] = None
    last_login: Optional[datetime] = None