"""
Pydantic schemas for News API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from app.db.models import ImpactType

class CategoryModel(BaseModel):
    """
    Pydantic model for news categories
    """
    id: Optional[int] = None
    name: str
    
    class Config:
        from_attributes = True

class SourceModel(BaseModel):
    """
    Pydantic model for news sources
    """
    id: Optional[int] = None
    codename: str
    name: str
    website: str
    
    class Config:
        from_attributes = True

class NewsUrlModel(BaseModel):
    """
    Pydantic model for news URLs linking sources to news articles
    """
    id: Optional[int] = None
    source_id: int
    news_id: Optional[int] = None
    url: str
    published_at: datetime
    source_rel: Optional[SourceModel] = None
    
    class Config:
        from_attributes = True

class NewsModel(BaseModel):
    """
    Pydantic model for financial news articles
    """
    id: Optional[int] = None
    title: str
    content: str
    summary: Optional[str] = None
    url: str
    published_at: datetime
    image_url: Optional[str] = None

    impact_prediction: Optional[ImpactType] = None
    impact_prediction_justification: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    categories: List[CategoryModel] = Field(default_factory=list)
    news_urls: List[NewsUrlModel] = Field(default_factory=list)
    sources: List[SourceModel] = Field(default_factory=list)
    
    class Config:
        from_attributes = True  # Allows the model to be created from an ORM model
        schema_extra = {
            "example": {
                "title": "Fed Raises Interest Rates by 0.25%",
                "content": "The Federal Reserve raised interest rates by 0.25% today...",
                "summary": "Fed raises rates by 0.25%",
                "url": "https://ft.com/news/123",
                "published_at": "2025-09-19T14:30:00Z",
                "image_url": "https://ft.com/images/news123.jpg",
                "impact_prediction": "negative",
                "impact_prediction_justification": "Rate hikes typically have a negative impact on stock markets in the short term.",
                "impact_score": -0.75,
                "categories": [
                    {"name": "monetary policy"},
                    {"name": "interest rates"},
                    {"name": "federal reserve"}
                ],
                "sources": [
                    {
                        "codename": "ft",
                        "name": "Financial Times",
                        "website": "https://ft.com"
                    }
                ]
            }
        }

# Create model for creating new news articles
class NewsCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    url: str
    published_at: datetime
    image_url: Optional[str] = None
    impact_prediction: Optional[str] = None
    impact_prediction_justification: Optional[str] = None
    
    # For creating relationships
    category_names: List[str] = Field(default_factory=list)
    source_urls: List[Dict[str, str]] = Field(default_factory=list, description="List of dictionaries with source_id and url")

# Update model for updating news articles
class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    impact_prediction: Optional[str] = None
    impact_prediction_justification: Optional[str] = None
    
    # For updating relationships
    category_names: Optional[List[str]] = None
    source_urls: Optional[List[Dict[str, str]]] = None