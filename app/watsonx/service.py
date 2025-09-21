"""
Watson Service

This module provides a service for integrating the Watson agent with the rest of the application.
It coordinates processing of scraped data through the Watson agent.
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from app.watsonx.processor import NewsProcessor
from app.watsonx.report_generator import ReportGenerator
from app.api.schemas.news import NewsModel, NewsUpdate
from app.api.schemas.report import WeeklyAIReport, WeeklyReportRequest
from app.api.controllers.news import NewsController
from app.db.database import SessionLocal
from app.common.enums import ImpactType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WatsonService:
    """
    Service for integrating Watson AI with the application
    """
    def __init__(self):
        self.processor = NewsProcessor()
        self.report_generator = ReportGenerator()
        self.processing_interval_minutes = 30  # Process news every 30 minutes
        self.max_batch_size = 20  # Process up to 20 news items at once
        self.is_running = False
    
    async def start(self):
        """
        Start the Watson service processing loop
        """
        self.is_running = True
        logger.info(f"Starting Watson service with interval {self.processing_interval_minutes} minutes")
        
        while self.is_running:
            try:
                await self.process_pending_news()
            except Exception as e:
                logger.error(f"Error in Watson service processing loop: {str(e)}")
            
            # Wait for next interval
            logger.info(f"Waiting {self.processing_interval_minutes} minutes until next processing")
            await asyncio.sleep(self.processing_interval_minutes * 60)
    
    def stop(self):
        """
        Stop the Watson service processing loop
        """
        self.is_running = False
        logger.info("Stopping Watson service")
    
    async def process_pending_news(self):
        """
        Process all pending news articles (those with UNKNOWN impact_prediction)
        """
        logger.info("Processing pending news articles")
        
        try:
            # Get all news with UNKNOWN impact_prediction
            with SessionLocal() as db:
                pending_news = NewsController.get_by_impact(db, ImpactType.UNKNOWN)
            
            logger.info(f"Found {len(pending_news)} pending news articles")
            
            # Process in batches to avoid overwhelming the Watson API
            for i in range(0, len(pending_news), self.max_batch_size):
                batch = pending_news[i:i+self.max_batch_size]
                
                # Process the batch
                updates = await self.processor.process_news_batch(batch)
                
                # Apply updates to the database
                with SessionLocal() as db:
                    for news_id, update in updates.items():
                        try:
                            NewsController.update(db, news_id, update)
                            logger.info(f"Updated news ID {news_id} with Watson analysis")
                        except Exception as e:
                            logger.error(f"Error updating news ID {news_id}: {str(e)}")
                
                # If there are more batches, wait a bit before processing the next one
                if i + self.max_batch_size < len(pending_news):
                    await asyncio.sleep(5)  # 5-second pause between batches
            
            logger.info("Finished processing pending news articles")
            
        except Exception as e:
            logger.error(f"Error processing pending news: {str(e)}")
    
    async def process_single_news(self, news: NewsModel) -> Optional[NewsUpdate]:
        """
        Process a single news article through the Watson agent
        
        Args:
            news (NewsModel): The news article to process
            
        Returns:
            Optional[NewsUpdate]: The update with analysis results, or None if processing failed
        """
        try:
            # Process the news article
            updates = await self.processor.process_news_batch([news])
            
            # Return the update for this news article, if it exists
            if news.id is not None and news.id in updates:
                return updates[news.id]
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing single news article: {str(e)}")
            return None
    
    async def health_check(self) -> bool:
        """
        Check if the Watson service is healthy
        
        Returns:
            bool: True if the service is healthy, False otherwise
        """
        # Check if the Watson API is responsive
        return await self.processor.watson_client.health_check()
        
    async def generate_weekly_report(self, report_request: WeeklyReportRequest) -> WeeklyAIReport:
        """
        Generate a weekly AI report based on news data
        
        Args:
            report_request (WeeklyReportRequest): The report request parameters
            
        Returns:
            WeeklyAIReport: The generated report
        """
        logger.info("Generating weekly AI report")
        
        # Determine date range
        end_date = report_request.end_date or datetime.now().date()
        start_date = report_request.start_date or (end_date - timedelta(days=7))
        
        # Get news for the specified period
        with SessionLocal() as db:
            # Convert dates to datetime for database query
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Get all news within the date range
            all_news = NewsController.get_all(db, limit=500)  # Get a larger set to filter
            
            # Filter by date
            news_in_range = [
                news for news in all_news 
                if start_datetime <= news.published_at <= end_datetime
            ]
            
            logger.info(f"Found {len(news_in_range)} news items in date range")
        
        # Generate the report
        report = await self.report_generator.generate_weekly_report(
            news_items=news_in_range,
            start_date=start_date,
            end_date=end_date,
            max_news_items=report_request.max_news_items or 10,
            categories_of_interest=report_request.categories_of_interest
        )
        
        return report