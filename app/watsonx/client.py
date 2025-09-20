"""
IBM WatsonX API Client

This module provides a client for connecting to the IBM WatsonX AI service.
It handles API connections, authentication, and request/response formatting.
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional
import json
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.db.models import News

# Load environment variables
load_dotenv()

CURRENT_USER_ID = 1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WatsonAgentClient:
    """
    Client for interacting with the IBM WatsonX API
    """
    def __init__(self):
        """
        Initialize the IBM WatsonX client
        
        The following environment variables are expected:
        - WATSONX_API_KEY: The API key for authenticating with the WatsonX service
        - WATSONX_INSTANCE_ID: The instance ID for the WatsonX service
        - WATSONX_PROJECT_ID: The project ID for the WatsonX service
        - WATSONX_URL: The URL of the WatsonX service (optional, has default)
        """
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.instance_id = os.getenv("WATSONX_INSTANCE_ID")
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.api_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com/ml/v1-beta")
        
        # Check for required environment variables
        if not self.api_key:
            logger.warning("WATSONX_API_KEY not found in environment variables")
        
        if not self.instance_id:
            logger.warning("WATSONX_INSTANCE_ID not found in environment variables")
            
        if not self.project_id:
            logger.warning("WATSONX_PROJECT_ID not found in environment variables")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get the HTTP headers for API requests
        
        Returns:
            Dict[str, str]: The headers to use for API requests
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "IBM-Cloud-IAM-ApiKey": self.api_key,
            "X-Watson-Service-Instance-ID": self.instance_id,
            "X-Watson-User-Agent": "WellershoffBackend/1.0"
        }
    
    async def analyze_news(self, news_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send news data to WatsonX for analysis using WatsonX Foundation Models
        
        Args:
            news_data (Dict[str, Any]): The news data to analyze
            
        Returns:
            Optional[Dict[str, Any]]: The analysis results from WatsonX, or None if the request failed
        """
        try:
            # Define the endpoint for model inference
            endpoint = f"{self.api_url}/generation/text"
            
            # Prepare the prompt with the news data
            news_context = json.dumps(news_data["news"], indent=2)

            # get title of news created_at today
            # Assuming News is a model or class, replace with the correct method or attribute to fetch today's news titles
            db = Session()
            todays_news = db.query(News).filter(user_id=CURRENT_USER_ID)

            todays_news_titles = [i.title for i in todays_news]
            
            # Create the payload for WatsonX
            payload = {
                "model_id": "ibm/granite-13b-instruct-v2",  # Using Granite model
                "input": (
                    "I'm going to give you the html of an article.\n"
                    "Your objective is to give me either the title of a news that is similar to it from the ones I give you or a summary of the article, a title, and an impact on market. \n\n"
                    "Article:\n"
                    f"{news_context}\n\n"
                    "Titles from today's news:\n"
                    f"{todays_news_titles}"
                ),
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 1000,
                    "min_new_tokens": 100,
                    "stop_sequences": [],
                    "temperature": 0.7
                },
                "project_id": self.project_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=60.0  # Set a longer timeout for model inference
                )
                
                # Check if the request was successful
                response.raise_for_status()
                
                # Parse the response
                watsonx_response = response.json()
                
                # Transform the WatsonX response to our expected format
                return self._transform_watsonx_response(watsonx_response, news_data)
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during WatsonX API call: {e.response.status_code} - {e.response.text}")
            return None
        
        except httpx.RequestError as e:
            logger.error(f"Error sending request to WatsonX API: {str(e)}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error during WatsonX API call: {str(e)}")
            return None
    
    def _transform_watsonx_response(self, watsonx_response: Dict[str, Any], original_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform the WatsonX response to our expected format
        
        Args:
            watsonx_response (Dict[str, Any]): The raw response from WatsonX
            original_request (Dict[str, Any]): The original request sent to WatsonX
            
        Returns:
            Dict[str, Any]: The transformed response in our expected format
        """
        try:
            # Extract the generated text from WatsonX response
            generated_text = watsonx_response.get("results", [{}])[0].get("generated_text", "")
            
            # Parse the generated text to extract analysis for each news item
            # This is a simplified parsing logic and would need to be adapted based on the actual response format
            results = []
            
            # For each news item in the original request, try to extract its analysis from the generated text
            for i, news_item in enumerate(original_request.get("news", [])):
                # Create a unique ID for this news item
                news_id = f"news_{i}"
                
                # Extract impact prediction and justification from generated text
                # This is a simplified approach - in practice, you'd need more robust parsing
                impact_prediction = "unsure"  # Default
                justification = "No specific justification provided by the model."
                
                # Try to find analysis for this specific news item in the generated text
                news_title = news_item.get("title", "")
                if news_title in generated_text:
                    # Look for impact keywords after the title
                    text_after_title = generated_text[generated_text.find(news_title) + len(news_title):]
                    
                    # Check for impact predictions
                    if "very positive" in text_after_title.lower():
                        impact_prediction = "very_positive"
                    elif "positive" in text_after_title.lower():
                        impact_prediction = "positive"
                    elif "negative" in text_after_title.lower():
                        impact_prediction = "negative"
                    elif "very negative" in text_after_title.lower():
                        impact_prediction = "very_negative"
                    
                    # Extract justification (first 200 chars after title as a simple approach)
                    justification = text_after_title[:200].strip()
                
                # Create a result for this news item
                results.append({
                    "news_id": news_id,
                    "impact_prediction": impact_prediction,
                    "impact_prediction_justification": justification,
                    "confidence_score": 0.7,  # Default confidence
                    "related_assets": [],  # Would need more sophisticated parsing to extract these
                    "key_entities": []  # Would need more sophisticated parsing to extract these
                })
            
            # Create the final response
            return {
                "results": results,
                "request_id": watsonx_response.get("model_id", "unknown"),
                "timestamp": watsonx_response.get("created_at", "")
            }
            
        except Exception as e:
            logger.error(f"Error transforming WatsonX response: {str(e)}")
            return {
                "results": [],
                "request_id": "error",
                "timestamp": ""
            }
    
    async def health_check(self) -> bool:
        """
        Check if the WatsonX API is available and responding
        
        Returns:
            bool: True if the API is available, False otherwise
        """
        try:
            # WatsonX doesn't have a dedicated health endpoint, so we'll make a minimal model call
            endpoint = f"{self.api_url}/generation/text"
            
            # Create a minimal payload just to test connectivity
            payload = {
                "model_id": "ibm/granite-13b-instruct-v2",
                "input": "Hello",
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 5
                },
                "project_id": self.project_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=10.0  # Short timeout for health check
                )
                
                # Return True if the request was successful (status code 200)
                return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error during WatsonX API health check: {str(e)}")
            return False