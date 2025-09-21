"""
Report Controller

Controller for handling report generation operations
"""
from fastapi import HTTPException, Query, APIRouter, Depends, Body
from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.schemas.report import WeeklyAIReport, WeeklyReportRequest
from app.watsonx import watson_service

# Create report router
report_router = APIRouter(
    prefix="/api/v1/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)

class ReportController:
    """
    Controller for handling report operations
    """
    
    @staticmethod
    async def generate_weekly_report(
        request: WeeklyReportRequest
    ) -> WeeklyAIReport:
        """
        Generate a weekly AI report
        """
        try:
            report = await watson_service.generate_weekly_report(request)
            return report
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate weekly report: {str(e)}")
    
    # API Endpoint Methods
    @staticmethod
    async def api_generate_weekly_report(
        request: WeeklyReportRequest = Body(...)
    ) -> WeeklyAIReport:
        """
        API endpoint to generate a weekly AI report
        """
        return await ReportController.generate_weekly_report(request)


# Define routes
@report_router.post("/weekly", response_model=WeeklyAIReport)
async def generate_weekly_report(request: WeeklyReportRequest = Body(...)):
    """
    Generate a weekly AI report based on news data
    
    - **start_date**: Optional start date for the report period (default: 7 days ago)
    - **end_date**: Optional end date for the report period (default: today)
    - **max_news_items**: Maximum number of news items to include (default: 10)
    - **categories_of_interest**: Optional list of categories to focus on
    """
    return await ReportController.api_generate_weekly_report(request=request)