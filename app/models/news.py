from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ImpactType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"

class NewsModel(BaseModel):
    """
    Model for financial news articles
    """
    id: Optional[str] = None
    title: str
    content: str
    summary: Optional[str] = None
    source: str
    url: str
    published_at: datetime
    image_url: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    impact_prediction: ImpactType = ImpactType.UNKNOWN
    impact_score: float = 0.0  # Range from -1.0 (negative) to 1.0 (positive)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Fed Raises Interest Rates by 0.25%",
                "content": "The Federal Reserve raised interest rates by 0.25% today...",
                "summary": "Fed raises rates by 0.25%",
                "source": "Financial Times",
                "url": "https://ft.com/news/123",
                "published_at": "2025-09-19T14:30:00Z",
                "image_url": "https://ft.com/images/news123.jpg",
                "categories": ["monetary policy", "interest rates", "federal reserve"],
                "impact_prediction": "negative",
                "impact_score": -0.75
            }
        }
    
    def to_dict(self):
        """Convert to dictionary for Firestore"""
        return {
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "source": self.source,
            "url": self.url,
            "published_at": self.published_at,
            "image_url": self.image_url,
            "categories": self.categories,
            "impact_prediction": self.impact_prediction,
            "impact_score": self.impact_score,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }