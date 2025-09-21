"""
Pydantic schemas for Reports API
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from app.common.enums import ImpactType

class WeeklyReportNewsItem(BaseModel):
    """
    Schema for news items in the weekly report
    """
    id: int
    title: str
    summary: Optional[str] = None
    url: str
    published_at: datetime
    impact_prediction: ImpactType
    categories: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

class MarketImpactSummary(BaseModel):
    """
    Schema for market impact summary
    """
    positive_count: int
    negative_count: int
    neutral_count: int
    overall_sentiment: str
    key_factors: List[str] = Field(default_factory=list)

class CategoryInsight(BaseModel):
    """
    Schema for category insights
    """
    category: str
    news_count: int
    impact_summary: str
    
    class Config:
        schema_extra = {
            "example": {
                "category": "monetary policy",
                "news_count": 5,
                "impact_summary": "Generally negative impact on markets due to rate hike discussions."
            }
        }

class WeeklyAIReport(BaseModel):
    """
    Schema for the Weekly AI Report
    """
    report_date: date
    week_start: date
    week_end: date
    report_title: str
    executive_summary: str
    market_impact: MarketImpactSummary
    top_news: List[WeeklyReportNewsItem] = Field(default_factory=list)
    category_insights: List[CategoryInsight] = Field(default_factory=list)
    key_trends: List[str] = Field(default_factory=list)
    outlook: str
    
    class Config:
        schema_extra = {
            "example": {
                "report_date": "2025-09-20",
                "week_start": "2025-09-14",
                "week_end": "2025-09-20",
                "report_title": "Weekly Market Intelligence Report",
                "executive_summary": "This week saw significant market movements driven by central bank decisions and geopolitical events.",
                "market_impact": {
                    "positive_count": 12,
                    "negative_count": 15,
                    "neutral_count": 8,
                    "overall_sentiment": "slightly negative",
                    "key_factors": ["Fed rate hike", "inflation concerns", "supply chain disruptions"]
                },
                "top_news": [
                    {
                        "id": 1,
                        "title": "Fed Raises Interest Rates by 0.25%",
                        "summary": "The Federal Reserve raised interest rates by 0.25% on Wednesday.",
                        "url": "https://example.com/news/1",
                        "published_at": "2025-09-15T14:30:00Z",
                        "impact_prediction": "negative",
                        "categories": ["monetary policy", "federal reserve"]
                    }
                ],
                "category_insights": [
                    {
                        "category": "monetary policy",
                        "news_count": 5,
                        "impact_summary": "Generally negative impact on markets due to rate hike discussions."
                    }
                ],
                "key_trends": [
                    "Rising inflation concerns in major economies",
                    "Continued tech sector growth despite market pressures",
                    "Increasing focus on sustainable investments"
                ],
                "outlook": "Markets are expected to remain volatile in the coming week with a focus on upcoming earnings reports and inflation data."
            }
        }

class WeeklyReportRequest(BaseModel):
    """
    Schema for requesting a weekly report
    """
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    max_news_items: Optional[int] = Field(default=10, ge=5, le=50)
    categories_of_interest: Optional[List[str]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "start_date": "2025-09-14",
                "end_date": "2025-09-20",
                "max_news_items": 15,
                "categories_of_interest": ["monetary policy", "technology", "energy"]
            }
        }
