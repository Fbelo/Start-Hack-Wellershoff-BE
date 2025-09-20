from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict
from datetime import datetime

class UserModel(BaseModel):
    """
    Model for application users
    """
    id: Optional[str] = None
    name: str
    email: EmailStr
    profile_picture: Optional[str] = None
    preferences: Dict[str, bool] = Field(default_factory=dict)  # User preferences like notification settings
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    class Config:
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
    
    def to_dict(self):
        """Convert to dictionary for Firestore"""
        return {
            "name": self.name,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "preferences": self.preferences,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login
        }