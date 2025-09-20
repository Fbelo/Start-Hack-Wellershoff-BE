import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from app.api.schemas.news import NewsModel
from dotenv import load_dotenv
import re
import time
import random

# Load environment variables
load_dotenv()

"""
Current scrapers
financial times - "https://www.ft.com/news-feed"
bloomberg - "https://www.bloomberg.com/latest"
yahoo finance - "https://finance.yahoo.com/topic/latest-news/"
reuters - "https://www.reuters.com/business/finance/"


"""

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraper:
    """
    Base class for news scrapers
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def get_html(self, url: str) -> Optional[str]:
        """
        Get HTML content from a URL
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse HTML content to extract news articles
        Should be implemented by subclasses
        """
        raise NotImplementedError
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace
        """
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()
    
    def get_news(self) -> List[NewsModel]:
        """
        Get news articles
        Should be implemented by subclasses
        """
        raise NotImplementedError


class FinancialTimesScraper(NewsScraper):
    """
    Scraper for Financial Times
    """
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.ft.com/news-feed"
        self.markets_url = "https://www.ft.com/markets"
        
    def parse_html(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse Financial Times HTML
        """
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Find article containers
        article_elements = soup.select('div.o-teaser')
        
        for article in article_elements[:10]:  # Limit to 10 articles
            try:
                # Extract title
                title_element = article.select_one('div.o-teaser__heading a')
                if not title_element:
                    continue
                    
                title = self.clean_text(title_element.text)
                
                # Extract URL
                url = title_element.get('href', '')
                if url and not url.startswith('http'):
                    url = self.base_url + url
                
                # Extract summary
                summary_element = article.select_one('div.o-teaser__standfirst')
                summary = self.clean_text(summary_element.text) if summary_element else ""
                
                # Extract image
                image_element = article.select_one('img')
                image_url = image_element.get('src') if image_element else None
                
                # Extract date (using current date as FT doesn't show publish date in list view)
                date = datetime.now()
                
                articles.append({
                    "title": title,
                    "url": url,
                    "summary": summary,
                    "content": "",  # Will be filled later if needed
                    "source": "Financial Times",
                    "published_at": date,
                    "image_url": image_url,
                    "categories": ["finance", "markets"]
                })
                
            except Exception as e:
                logger.error(f"Error parsing FT article: {e}")
                continue
                
        return articles
    
    def get_article_content(self, url: str) -> str:
        """
        Get the content of a specific article
        """
        html = self.get_html(url)
        if not html:
            return ""
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find article body
        article_body = soup.select_one('div.article__content-body')
        if not article_body:
            return ""
            
        # Get all paragraphs
        paragraphs = article_body.select('p')
        content = ' '.join([p.text for p in paragraphs])
        
        return self.clean_text(content)
    
    def get_news(self) -> List[NewsModel]:
        """
        Get news from Financial Times
        """
        html = self.get_html(self.markets_url)
        articles_data = self.parse_html(html)
        
        news_models = []
        for article in articles_data:
            # Get full content for each article
            if article["url"]:
                # In a real app, you might want to use async to speed this up
                # For the demo, we'll just sleep to avoid overloading the server
                time.sleep(random.uniform(0.5, 1.5))
                article["content"] = self.get_article_content(article["url"])
            
            # Create NewsModel
            news_models.append(NewsModel(**article))
            
        return news_models


class BloombergScraper(NewsScraper):
    """
    Scraper for Bloomberg
    """
    def __init__(self):
        super().__init__()
        self.markets_url = "https://www.bloomberg.com/markets"
        
    def parse_html(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse Bloomberg HTML
        """
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Find article containers
        article_elements = soup.select('article.story-package-module__story')
        
        for article in article_elements[:10]:  # Limit to 10 articles
            try:
                # Extract title
                title_element = article.select_one('h3.story-package-module__headline')
                if not title_element:
                    continue
                    
                title = self.clean_text(title_element.text)
                
                # Extract URL
                link_element = article.select_one('a.story-package-module__headline-link')
                url = link_element.get('href', '') if link_element else ''
                
                # Extract summary
                summary_element = article.select_one('div.story-package-module__summary')
                summary = self.clean_text(summary_element.text) if summary_element else ""
                
                # Extract date (using current date as Bloomberg doesn't show publish date in list view)
                date = datetime.now()
                
                articles.append({
                    "title": title,
                    "url": url,
                    "summary": summary,
                    "content": "",  # Will be filled later if needed
                    "source": "Bloomberg",
                    "published_at": date,
                    "image_url": None,
                    "categories": ["finance", "markets"]
                })
                
            except Exception as e:
                logger.error(f"Error parsing Bloomberg article: {e}")
                continue
                
        return articles
    
    def get_news(self) -> List[NewsModel]:
        """
        Get news from Bloomberg
        """
        html = self.get_html(self.markets_url)
        articles_data = self.parse_html(html)
        
        news_models = []
        for article in articles_data:
            # Create NewsModel (we'll skip getting full content as Bloomberg has a paywall)
            news_models.append(NewsModel(**article))
            
        return news_models


class YahooFinanceScraper(NewsScraper):
    """
    Scraper for Yahoo Finance
    """
    def __init__(self):
        super().__init__()
        self.base_url = "https://finance.yahoo.com"
        
    def parse_html(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse Yahoo Finance HTML
        """
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Find article containers
        article_elements = soup.select('li.js-stream-content')
        
        for article in article_elements[:10]:  # Limit to 10 articles
            try:
                # Extract title
                title_element = article.select_one('h3')
                if not title_element:
                    continue
                    
                title = self.clean_text(title_element.text)
                
                # Extract URL
                link_element = article.select_one('a')
                url = link_element.get('href', '') if link_element else ''
                if url and not url.startswith('http'):
                    url = self.base_url + url
                
                # Extract summary (Yahoo Finance doesn't typically have summaries in the list view)
                summary = ""
                
                # Extract image
                image_element = article.select_one('img')
                image_url = image_element.get('src') if image_element else None
                
                # Extract date (using current date as Yahoo doesn't show publish date in list view)
                date = datetime.now()
                
                articles.append({
                    "title": title,
                    "url": url,
                    "summary": summary,
                    "content": "",  # Will be filled later if needed
                    "source": "Yahoo Finance",
                    "published_at": date,
                    "image_url": image_url,
                    "categories": ["finance", "markets"]
                })
                
            except Exception as e:
                logger.error(f"Error parsing Yahoo Finance article: {e}")
                continue
                
        return articles
    
    def get_article_content(self, url: str) -> str:
        """
        Get the content of a specific article
        """
        html = self.get_html(url)
        if not html:
            return ""
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find article body
        article_body = soup.select_one('div.caas-body')
        if not article_body:
            return ""
            
        # Get all paragraphs
        paragraphs = article_body.select('p')
        content = ' '.join([p.text for p in paragraphs])
        
        return self.clean_text(content)
    
    def get_news(self) -> List[NewsModel]:
        """
        Get news from Yahoo Finance
        """
        html = self.get_html(self.base_url)
        articles_data = self.parse_html(html)
        
        news_models = []
        for article in articles_data:
            # Get full content for each article
            if article["url"]:
                # In a real app, you might want to use async to speed this up
                # For the demo, we'll just sleep to avoid overloading the server
                time.sleep(random.uniform(0.5, 1.5))
                article["content"] = self.get_article_content(article["url"])
            
            # Create NewsModel
            news_models.append(NewsModel(**article))
            
        return news_models


def scrape_all_news() -> List[NewsModel]:
    """
    Scrape news from all sources
    """
    scrapers = [
        FinancialTimesScraper(),
        BloombergScraper(),
        YahooFinanceScraper()
    ]
    
    all_news = []
    for scraper in scrapers:
        try:
            news = scraper.get_news()
            all_news.extend(news)
        except Exception as e:
            logger.error(f"Error with scraper {scraper.__class__.__name__}: {e}")
    
    return all_news