"""
Watson Agent Schemas

This module provides Pydantic schemas for Watson Agent requests and responses.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.common.enums import ImpactType

class NewsForAnalysis(BaseModel):
    """
    Schema for news data being sent to Watson for analysis
    """
    title: str
    content: str
    summary: Optional[str] = None
    source: str
    published_date: datetime
    urls: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class WatsonNewsAnalysisRequest(BaseModel):
    """
    Schema for a Watson Agent news analysis request
    """
    news: List[NewsForAnalysis]
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "news": [
                    {
                        "title": "Fed Raises Interest Rates by 0.25%",
                        "content": "The Federal Reserve raised interest rates by 0.25% today...",
                        "summary": "Fed raises rates by 0.25%",
                        "source": "Financial Times",
                        "published_date": "2025-09-19T14:30:00Z",
                        "urls": ["https://ft.com/news/123"]
                    }
                ],
                "context": {
                    "market_state": "volatile",
                    "recent_trends": ["inflation concerns", "tech sector growth"]
                }
            }
        }

class NewsAnalysisResult(BaseModel):
    """
    Schema for the result of a Watson news analysis
    """
    news_id: str  # Identifier to match the result to the original news item
    impact_prediction: ImpactType
    impact_prediction_justification: str
    confidence_score: float = Field(ge=0.0, le=1.0)  # Confidence score between 0 and 1
    related_assets: List[Dict[str, Any]] = Field(default_factory=list)
    key_entities: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "news_id": "news_ft_12345",
                "impact_prediction": "negative",
                "impact_prediction_justification": "Rate hikes typically have a negative impact on stock markets in the short term.",
                "confidence_score": 0.85,
                "related_assets": [
                    {"type": "stock", "symbol": "AAPL", "impact": "negative"},
                    {"type": "bond", "symbol": "US10Y", "impact": "positive"}
                ],
                "key_entities": ["Federal Reserve", "interest rates", "inflation"]
            }
        }

class WatsonNewsAnalysisResponse(BaseModel):
    """
    Schema for a Watson Agent news analysis response
    """
    results: List[NewsAnalysisResult]
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "news_id": "news_ft_12345",
                        "impact_prediction": "negative",
                        "impact_prediction_justification": "Rate hikes typically have a negative impact on stock markets in the short term.",
                        "confidence_score": 0.85,
                        "related_assets": [
                            {"type": "stock", "symbol": "AAPL", "impact": "negative"},
                            {"type": "bond", "symbol": "US10Y", "impact": "positive"}
                        ],
                        "key_entities": ["Federal Reserve", "interest rates", "inflation"]
                    }
                ],
                "request_id": "req_abc123",
                "timestamp": "2025-09-19T15:30:00Z"
            }
        }