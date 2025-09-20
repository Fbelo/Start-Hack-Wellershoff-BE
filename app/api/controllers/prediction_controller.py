from fastapi import HTTPException, BackgroundTasks, APIRouter
from typing import List, Dict
from app.services.news import NewsService
from app.services.portfolio_asset import PortfolioAssetService
from app.api.schemas.news import NewsModel, ImpactType
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create prediction router
prediction_router = APIRouter(
    prefix="/api/v1/predictions",
    tags=["predictions"],
    responses={404: {"description": "Not found"}},
)

class PredictionController:
    @staticmethod
    async def predict_news_impact_for_user(news_id: str, user_id: str):
        """
        Predict the impact of a specific news article on a user's portfolio
        """
        # Get the news
        news = NewsService.get_by_id(news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News article not found")
            
        # Get the user's portfolio
        portfolio = PortfolioAssetService.get_all_by_user(user_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="User has no portfolio assets")
            
        # Predict impact
        try:
            updated_news = ""
            # updated_news = predict_news_impact(news, portfolio)
            
            # Update the news in the database
            NewsService.update(news_id, {
                "impact_prediction": updated_news.impact_prediction,
                "impact_score": updated_news.impact_score
            })
            
            return updated_news
        except Exception as e:
            logger.error(f"Error predicting impact: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def process_all_news_for_user(user_id: str, background_tasks: BackgroundTasks):
        """
        Process all news and predict impact for a user's portfolio
        This is a background task as it may take some time
        """
        # Get the user's portfolio
        portfolio = PortfolioAssetService.get_all_by_user(user_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="User has no portfolio assets")
        
        # Start background task to process all news
        background_tasks.add_task(PredictionController._process_all_news_background, portfolio)
        
        return {"message": "Processing started in background", "status": "success"}

    @staticmethod
    async def _process_all_news_background(portfolio: List):
        """
        Background task to process all news
        """
        try:
            # Get all news
            news_list = NewsService.get_all(limit=100)
            
            # Process all news
            updated_news_list = []
            # updated_news_list = process_all_news(news_list, portfolio)
            
            # Update all news in the database
            for news in updated_news_list:
                NewsService.update(news.id, {
                    "impact_prediction": news.impact_prediction,
                    "impact_score": news.impact_score
                })
                
            logger.info(f"Processed {len(news_list)} news articles")
        except Exception as e:
            logger.error(f"Error processing news: {e}")

    @staticmethod
    async def get_portfolio_impact_summary(user_id: str):
        """
        Get a summary of news impact on a user's portfolio
        """
        # Get all news with impact predictions
        all_news = NewsService.get_all(limit=100)
        
        # Filter news with impact predictions
        positive_news = [n for n in all_news if n.impact_prediction == ImpactType.POSITIVE]
        negative_news = [n for n in all_news if n.impact_prediction == ImpactType.NEGATIVE]
        neutral_news = [n for n in all_news if n.impact_prediction == ImpactType.NEUTRAL]
        unknown_news = [n for n in all_news if n.impact_prediction == ImpactType.UNKNOWN]
        
        # Calculate average impact score
        if positive_news or negative_news:
            impact_scores = [n.impact_score for n in all_news if n.impact_prediction != ImpactType.UNKNOWN]
            avg_impact_score = sum(impact_scores) / len(impact_scores) if impact_scores else 0
        else:
            avg_impact_score = 0
        
        # Determine overall trend
        if avg_impact_score > 0.2:
            overall_trend = "positive"
        elif avg_impact_score < -0.2:
            overall_trend = "negative"
        else:
            overall_trend = "neutral"
        
        return {
            "overall_trend": overall_trend,
            "avg_impact_score": avg_impact_score,
            "positive_news_count": len(positive_news),
            "negative_news_count": len(negative_news),
            "neutral_news_count": len(neutral_news),
            "unknown_news_count": len(unknown_news),
            "total_news_count": len(all_news),
            "top_positive_news": positive_news[:3] if positive_news else [],
            "top_negative_news": negative_news[:3] if negative_news else []
        }


# Define routes
@prediction_router.get("/news/{news_id}/impact/{user_id}", response_model=NewsModel)
async def predict_news_impact_for_user(news_id: str, user_id: str):
    return await PredictionController.predict_news_impact_for_user(news_id=news_id, user_id=user_id)

@prediction_router.post("/process-all-news/{user_id}", response_model=Dict)
async def process_all_news_for_user(user_id: str, background_tasks: BackgroundTasks):
    return await PredictionController.process_all_news_for_user(user_id=user_id, background_tasks=background_tasks)

@prediction_router.get("/portfolio/{user_id}/impact", response_model=Dict)
async def get_portfolio_impact_summary(user_id: str):
    return await PredictionController.get_portfolio_impact_summary(user_id=user_id)