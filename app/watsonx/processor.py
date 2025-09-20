"""
Watson News Processor

This module handles the processing of news data through the Watson agent.
It transforms the data between application models and Watson API formats.
"""
import logging
from typing import List, Dict
from app.watsonx.client import WatsonAgentClient
from app.watsonx.schemas import (
    NewsForAnalysis, 
    WatsonNewsAnalysisRequest,
    WatsonNewsAnalysisResponse, 
)
from app.api.schemas.news import NewsModel, NewsUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsProcessor:
    """
    Process news data through the Watson agent
    """
    def __init__(self):
        self.watson_client = WatsonAgentClient()
    
    def _prepare_news_for_analysis(self, news: NewsModel) -> NewsForAnalysis:
        """
        Transform a NewsModel into a format suitable for Watson analysis
        
        Args:
            news (NewsModel): The news article to prepare
            
        Returns:
            NewsForAnalysis: The prepared news data
        """
        # Extract URLs from news_urls relation
        urls = []
        for news_url in news.news_urls:
            urls.append(news_url.url)
        
        # Extract source name (using the first source if multiple exist)
        source = "Unknown"
        if news.sources and len(news.sources) > 0:
            source = news.sources[0].name
        
        return NewsForAnalysis(
            title=news.title,
            content=news.content,
            summary=news.summary,
            source=source,
            published_date=news.published_at,
            urls=urls
        )
    
    def _create_analysis_request(self, news_list: List[NewsModel]) -> WatsonNewsAnalysisRequest:
        """
        Create a Watson analysis request for a list of news items
        
        Args:
            news_list (List[NewsModel]): The list of news articles to analyze
            
        Returns:
            WatsonNewsAnalysisRequest: The prepared request
        """
        prepared_news = [self._prepare_news_for_analysis(news) for news in news_list]
        
        # Create context information
        # This could be extended to include market state, trends, etc.
        context = {
            "request_timestamp": None,  # Will be filled in by the API
            "analysis_type": "market_impact"
        }
        
        return WatsonNewsAnalysisRequest(
            news=prepared_news,
            context=context
        )
    
    def _map_response_to_updates(
        self, 
        response: WatsonNewsAnalysisResponse, 
        news_list: List[NewsModel]
    ) -> Dict[int, NewsUpdate]:
        """
        Map Watson analysis results to NewsUpdate objects
        
        Args:
            response (WatsonNewsAnalysisResponse): The Watson analysis response
            news_list (List[NewsModel]): The original news list sent for analysis
            
        Returns:
            Dict[int, NewsUpdate]: A dictionary mapping news IDs to update objects
        """
        updates = {}
        
        # Create a map from news index to news ID for easy lookup
        news_map = {i: news.id for i, news in enumerate(news_list) if news.id is not None}
        
        for result in response.results:
            # Extract the news index from the news_id (format: "news_{index}")
            try:
                if result.news_id.startswith("news_"):
                    index = int(result.news_id.split("_")[1])
                    if index in news_map:
                        news_id = news_map[index]
                        
                        # Create the update object
                        updates[news_id] = NewsUpdate(
                            impact_prediction=result.impact_prediction,
                            impact_prediction_justification=result.impact_prediction_justification
                        )
            except (ValueError, IndexError) as e:
                logger.error(f"Error mapping news ID {result.news_id}: {str(e)}")
        
        return updates
    
    async def process_news_batch(self, news_list: List[NewsModel]) -> Dict[int, NewsUpdate]:
        """
        Process a batch of news articles through the Watson agent
        
        Args:
            news_list (List[NewsModel]): The list of news articles to process
            
        Returns:
            Dict[int, NewsUpdate]: A dictionary mapping news IDs to update objects with the analysis results
        """
        try:
            # Skip processing if there are no news items
            if not news_list:
                logger.info("No news items to process")
                return {}
            
            # Prepare the request
            request = self._create_analysis_request(news_list)
            
            # Convert request to dictionary for API
            request_dict = request.dict()
            
            # Add unique IDs to news items for tracking
            for i, news_item in enumerate(request_dict["news"]):
                # Use news index as identifier (simple approach)
                news_item["id"] = f"news_{i}"
            
            # Send the request to Watson
            logger.info(f"Sending {len(news_list)} news items to Watson for analysis")
            response_dict = await self.watson_client.analyze_news(request_dict)
            
            # Check if we got a valid response
            if not response_dict:
                logger.error("Watson analysis failed - no response received")
                return {}
            
            # Parse the response
            try:
                response = WatsonNewsAnalysisResponse(**response_dict)
            except Exception as e:
                logger.error(f"Error parsing Watson response: {str(e)}")
                return {}
            
            # Map the results to news updates
            updates = self._map_response_to_updates(response, news_list)
            logger.info(f"Successfully processed {len(updates)} news items")
            
            return updates
            
        except Exception as e:
            logger.error(f"Error processing news batch: {str(e)}")
            return {}