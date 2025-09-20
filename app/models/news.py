from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from app.db.postgres.database import Base
from app.db.postgres.models import news_categories

class ImpactType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"

# SQLAlchemy model for database operations
class News(Base):
    """
    SQLAlchemy model for news table
    """
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String, nullable=True)
    source = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)
    image_url = Column(String, nullable=True)
    impact_prediction = Column(SQLAEnum(ImpactType), default=ImpactType.UNKNOWN)
    impact_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with categories through association table
    categories = relationship("Category", secondary=news_categories, backref="news_articles")

# Category model for the news categories
class Category(Base):
    """
    SQLAlchemy model for categories table
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

# Pydantic model for API requests/responses
class NewsModel(BaseModel):
    """
    Pydantic model for financial news articles
    """
    id: Optional[int] = None
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
        from_attributes = True  # Allows the model to be created from an ORM model
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

# Create model for creating new news articles
class NewsCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    source: str
    url: str
    published_at: datetime
    image_url: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    impact_prediction: ImpactType = ImpactType.UNKNOWN
    impact_score: float = 0.0

# Update model for updating news articles
class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None
    image_url: Optional[str] = None
    categories: Optional[List[str]] = None
    impact_prediction: Optional[ImpactType] = None
    impact_score: Optional[float] = None