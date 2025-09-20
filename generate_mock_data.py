"""
This script generates mock data for testing.
It creates a user, multiple news items with multiple URLs from different sources.
"""

import json
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Optional
from app.api.schemas.news import NewsModel, NewsUrlModel, SourceModel, CategoryModel
from app.api.schemas.user import UserModel

def generate_mock_data() -> Dict[str, Any]:
    """
    Generates mock data for testing purposes.
    Creates:
    - 1 user
    - Multiple news items from different sources
    - Each news item has multiple URLs pointing to different sources
    
    Returns a dictionary with the generated data.
    """
    # Generate mock user
    user = UserModel(
        id=1,
        name="Test User",
        email="testuser@example.com",
        profile_picture="https://randomuser.me/api/portraits/men/1.jpg",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        last_login=datetime.now()
    )
    
    # Define sources (from comment in news_scraper.py)
    sources = [
        SourceModel(
            id=1,
            codename="ft",
            name="Financial Times",
            website="https://www.ft.com"
        ),
        SourceModel(
            id=2,
            codename="bb",
            name="Bloomberg",
            website="https://www.bloomberg.com"
        ),
        SourceModel(
            id=3,
            codename="yf",
            name="Yahoo Finance",
            website="https://finance.yahoo.com"
        ),
        SourceModel(
            id=4,
            codename="rt",
            name="Reuters",
            website="https://www.reuters.com"
        )
    ]
    
    # Define categories
    categories = [
        CategoryModel(id=1, name="markets"),
        CategoryModel(id=2, name="finance"),
        CategoryModel(id=3, name="stocks"),
        CategoryModel(id=4, name="bonds"),
        CategoryModel(id=5, name="commodities"),
        CategoryModel(id=6, name="currencies"),
        CategoryModel(id=7, name="economy"),
        CategoryModel(id=8, name="central banks"),
        CategoryModel(id=9, name="technology"),
        CategoryModel(id=10, name="regulation")
    ]
    
    # Generate mock news
    news_items = []
    
    # News headlines and content
    news_data = [
        {
            "title": "Fed Raises Interest Rates by 0.25%",
            "content": "The Federal Reserve raised interest rates by 0.25% today, citing concerns about inflation. This marks the third rate hike this year as the central bank continues its fight against persistent inflation. Market reaction was mixed, with stocks initially dropping before recovering later in the session.",
            "summary": "Federal Reserve implements third rate hike of the year",
            "categories": ["central banks", "economy", "finance"],
            "impact_prediction": "negative",
            "impact_prediction_justification": "Rate hikes typically have a negative impact on stock markets in the short term.",
        },
        {
            "title": "ECB Holds Rates Steady Despite Inflation Concerns",
            "content": "The European Central Bank has decided to maintain current interest rates despite growing concerns about inflation across the eurozone. Officials cited the need to support economic recovery in the face of ongoing supply chain disruptions and energy price volatility.",
            "summary": "European Central Bank maintains current monetary policy",
            "categories": ["central banks", "economy", "finance", "currencies"],
            "impact_prediction": "unsure",
            "impact_prediction_justification": "While rate stability is generally positive, persistent inflation could erode market confidence.",
        },
        {
            "title": "Oil Prices Surge Amid Middle East Tensions",
            "content": "Oil prices surged today amid escalating tensions in the Middle East, with Brent crude rising above $95 per barrel. Analysts warn that continued geopolitical instability could push prices even higher, potentially impacting global economic recovery efforts.",
            "summary": "Geopolitical tensions drive oil prices to multi-month highs",
            "categories": ["commodities", "markets", "economy"],
            "impact_prediction": "negative",
            "impact_prediction_justification": "Higher oil prices typically lead to increased costs for businesses and reduced consumer spending power.",
        },
        {
            "title": "Tech Stocks Rally on Strong Earnings Reports",
            "content": "Technology stocks rallied today following better-than-expected earnings reports from several major companies. The surge was led by semiconductor manufacturers and software firms, many of which reported strong revenue growth and positive outlooks for the coming quarters.",
            "summary": "Tech sector leads market gains after positive earnings surprises",
            "categories": ["stocks", "markets", "technology"],
            "impact_prediction": "very_positive",
            "impact_prediction_justification": "Strong earnings reports typically drive investor confidence and market growth, especially in tech sector.",
        },
        {
            "title": "New Regulations Target Cryptocurrency Exchanges",
            "content": "Regulators announced new oversight measures for cryptocurrency exchanges today, aiming to improve transparency and protect investors. The regulations will require exchanges to implement enhanced KYC procedures and maintain larger capital reserves. Industry reaction has been mixed.",
            "summary": "Regulatory authorities introduce new compliance requirements for crypto platforms",
            "categories": ["regulation", "finance", "technology"],
            "impact_prediction": "negative",
            "impact_prediction_justification": "Increased regulatory oversight often creates short-term uncertainty and compliance costs in affected markets.",
        },
        {
            "title": "Global Supply Chain Issues Continue to Pressure Inflation",
            "content": "Global supply chain disruptions show little sign of abating, according to a new industry report. Shipping costs remain elevated, component shortages persist, and delivery times continue to extend, all contributing to ongoing inflationary pressures across multiple sectors.",
            "summary": "Persistent supply chain problems contribute to elevated inflation",
            "categories": ["economy", "markets", "commodities"],
            "impact_prediction": "very_negative",
            "impact_prediction_justification": "Persistent supply chain issues and inflation have broad negative impacts across most economic sectors.",
        }
    ]
    
    # Generate news items with URLs from different sources
    for i, news_data_item in enumerate(news_data):
        # Create news URLs for each source
        news_urls = []
        for source in sources:
            # Create a different URL for each source
            if source.codename == "ft":
                url = f"https://www.ft.com/content/news-{i+1}-{random.randint(10000, 99999)}"
            elif source.codename == "bb":
                url = f"https://www.bloomberg.com/news/articles/{datetime.now().strftime('%Y-%m-%d')}/news-{i+1}-{random.randint(10000, 99999)}"
            elif source.codename == "yf":
                url = f"https://finance.yahoo.com/news/article-{i+1}-{random.randint(10000, 99999)}.html"
            elif source.codename == "rt":
                url = f"https://www.reuters.com/business/finance/news-{i+1}-{random.randint(10000, 99999)}"
            
            news_urls.append(
                NewsUrlModel(
                    id=len(news_urls) + 1,
                    source_id=source.id,
                    news_id=i + 1,
                    url=url,
                    published_at=published_date,
                    source_rel=source
                )
            )
        
        # Create category models based on the categories in the news data
        news_categories = [
            next((cat for cat in categories if cat.name == cat_name), None)
            for cat_name in news_data_item["categories"]
        ]
        news_categories = [cat for cat in news_categories if cat is not None]
        
        # Create the news item
        published_date = datetime.now() - timedelta(days=random.randint(0, 5), 
                                                  hours=random.randint(0, 23), 
                                                  minutes=random.randint(0, 59))
        
        news_item = NewsModel(
            id=i + 1,
            title=news_data_item["title"],
            content=news_data_item["content"],
            summary=news_data_item["summary"],
            url=news_urls[0].url,  # Use the first URL as the primary one
            published_at=published_date,
            image_url=f"https://example.com/images/news-{i+1}.jpg",
            impact_prediction=news_data_item.get("impact_prediction", "unsure"),
            impact_prediction_justification=news_data_item.get("impact_prediction_justification", "No justification provided."),
            impact_score=news_data_item.get("impact_score", 0.0),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            categories=news_categories,
            news_urls=news_urls,
            sources=sources
        )
        
        news_items.append(news_item)
    
    # Create the final result dictionary
    result = {
        "user": user.dict(),
        "news": [news.dict() for news in news_items],
        "sources": [source.dict() for source in sources],
        "categories": [category.dict() for category in categories]
    }
    
    return result

def save_mock_data_to_json(data: Dict[str, Any], filepath: str = "mock_data.json") -> None:
    """
    Saves the mock data to a JSON file.
    
    Args:
        data: The mock data dictionary
        filepath: Path to save the JSON file
    """
    # Convert datetime objects to strings
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    with open(filepath, "w") as f:
        json.dump(data, f, default=serialize_datetime, indent=2)
    
    print(f"Mock data saved to {filepath}")

def print_mock_data_summary(data: Dict[str, Any]) -> None:
    """
    Prints a summary of the generated mock data.
    
    Args:
        data: The mock data dictionary
    """
    print("\n=== MOCK DATA SUMMARY ===")
    print(f"User: {data['user']['name']} ({data['user']['email']})")
    print(f"News items: {len(data['news'])}")
    print(f"Sources: {len(data['sources'])}")
    print(f"Categories: {len(data['categories'])}")
    
    print("\nNews Items:")
    for i, news in enumerate(data['news']):
        print(f"  {i+1}. {news['title']}")
        print(f"     - Published: {news['published_at']}")
        print(f"     - Categories: {', '.join(cat['name'] for cat in news['categories'])}")
        print(f"     - URLs: {len(news['news_urls'])}")
        print(f"     - Impact: {news['impact_prediction']} ({news['impact_score']})")
        print()

if __name__ == "__main__":
    # Generate the mock data
    mock_data = generate_mock_data()
    
    # Print a summary
    print_mock_data_summary(mock_data)
    
    # Save to JSON file
    save_mock_data_to_json(mock_data)