"""
IBM WatsonX AI Integration Package

This package provides integration with the IBM WatsonX AI service for analyzing financial news
and predicting their market impact.

Main components:
- client: Handles API connections to the IBM WatsonX service
- schemas: Defines request/response models for WatsonX AI
- processor: Processes news data through WatsonX API
- service: Integrates WatsonX with the rest of the application
"""

from app.watsonx.client import WatsonAgentClient
from app.watsonx.schemas import (
    NewsForAnalysis, 
    WatsonNewsAnalysisRequest,
    WatsonNewsAnalysisResponse, 
    NewsAnalysisResult
)
from app.watsonx.processor import NewsProcessor
from app.watsonx.service import WatsonService

# Create a singleton instance of the Watson service
# This can be imported and used throughout the application
watson_service = WatsonService()

__all__ = [
    'WatsonAgentClient',
    'NewsForAnalysis',
    'WatsonNewsAnalysisRequest',
    'WatsonNewsAnalysisResponse',
    'NewsAnalysisResult',
    'NewsProcessor',
    'WatsonService',
    'watson_service',
]