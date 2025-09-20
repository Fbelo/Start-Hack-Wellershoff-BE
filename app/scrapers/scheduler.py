import asyncio
import logging
from app.scrapers.news_scraper import scrape_all_news
from app.api.controllers.news import NewsController
from app.api.schemas.news import NewsModel, ImpactType, NewsCreate
from app.db.database import get_db, SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraperScheduler:
    """
    Scheduler for running news scrapers
    """
    def __init__(self, interval_minutes: int = 15):
        self.interval_minutes = interval_minutes
        self.is_running = False
    
    async def start(self):
        """
        Start the scheduler
        """
        self.is_running = True
        logger.info(f"Starting news scraper scheduler with interval {self.interval_minutes} minutes")
        
        while self.is_running:
            try:
                await self.run_scrapers()
            except Exception as e:
                logger.error(f"Error running scrapers: {e}")
            
            # Wait for next interval
            logger.info(f"Waiting {self.interval_minutes} minutes until next scrape")
            await asyncio.sleep(self.interval_minutes * 60)
    
    async def run_scrapers(self):
        """
        Run all scrapers and save results to database
        """
        logger.info("Starting news scraping process")
        
        # This is a blocking operation, in a real app you might want to run it in a ThreadPoolExecutor
        news_list = scrape_all_news()
        
        logger.info(f"Scraped {len(news_list)} news articles")
        
        # Save to database
        for news in news_list:
            try:
                # Check if news already exists by URL
                # In a real app, you might want to implement a more sophisticated deduplication logic
                existing_news = self._find_existing_news_by_title(news.title)
                
                if not existing_news:
                    # Set impact prediction to UNKNOWN, will be processed by the prediction service
                    news.impact_prediction = ImpactType.UNKNOWN
                    news.impact_score = 0.0
                    
                    # Create a NewsCreate model for the controller
                    news_create = NewsCreate(
                        title=news.title,
                        content=news.content,
                        summary=news.summary,
                        published_date=news.published_date,
                        source=news.source,
                        urls=news.urls,
                        impact_prediction=ImpactType.UNKNOWN,
                        impact_score=0.0,
                        impact_prediction_justification=""
                    )
                    
                    # Save to database
                    with SessionLocal() as db:
                        NewsController.create(db, news_create)
                    logger.info(f"Saved news: {news.title}")
                else:
                    logger.info(f"News already exists: {news.title}")
            except Exception as e:
                logger.error(f"Error saving news: {str(e)}")
    
    def _find_existing_news_by_title(self, title: str) -> NewsModel:
        """
        Find existing news by title
        This is a simple implementation, in a real app you might want to use a more sophisticated approach
        """
        try:
            # Get a database session
            with SessionLocal() as db:
                # Search for news with this title
                news_list = NewsController.get_all(db)
                
                # Check if any result has exactly the same title
                for news in news_list:
                    if news.title.lower() == title.lower():
                        return news
            
            return None
        except Exception as e:
            logger.error(f"Error finding existing news: {str(e)}")
            return None
    
    def stop(self):
        """
        Stop the scheduler
        """
        logger.info("Stopping news scraper scheduler")
        self.is_running = False

# Global scheduler instance
scheduler = NewsScraperScheduler()

async def start_scheduler():
    """
    Start the news scraper scheduler
    """
    await scheduler.start()

def get_scheduler() -> NewsScraperScheduler:
    """
    Get the scheduler instance
    """
    return scheduler