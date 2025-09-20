import json
from datetime import datetime, timedelta
import random
from typing import Dict, Any
from app.api.schemas.news import NewsModel, NewsUrlModel, SourceModel, CategoryModel
from app.api.schemas.user import UserModel

# Database imports
from app.db.database import SessionLocal, create_schema_if_not_exists
from app.db.models import User, News, Category, Source, NewsUrl, PortfolioAsset


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
    user = User(
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
        Source(
            id=1,
            codename="ft",
            name="Financial Times",
            website="https://www.ft.com"
        ),
        Source(
            id=2,
            codename="bb",
            name="Bloomberg",
            website="https://www.bloomberg.com"
        ),
        Source(
            id=3,
            codename="yf",
            name="Yahoo Finance",
            website="https://finance.yahoo.com"
        ),
        Source(
            id=4,
            codename="rt",
            name="Reuters",
            website="https://www.reuters.com"
        )
    ]
    
    # Define categories
    categories = [
        Category(id=1, name="markets"),
        Category(id=2, name="finance"),
        Category(id=3, name="stocks"),
        Category(id=4, name="bonds"),
        Category(id=5, name="commodities"),
        Category(id=6, name="currencies"),
        Category(id=7, name="economy"),
        Category(id=8, name="central banks"),
        Category(id=9, name="technology"),
        Category(id=10, name="regulation")
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
        # ... (Include other mock news data here)
    ]
    
    # Generate news items with URLs from different sources
    for i, news_data_item in enumerate(news_data):
        # Create the publication date first
        published_date = datetime.now() - timedelta(days=random.randint(0, 5), 
                                                  hours=random.randint(0, 23), 
                                                  minutes=random.randint(0, 59))
        
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
                NewsUrl(
                    id=len(news_urls) + 1,
                    source_id=source.id,
                    news_id=i + 1,
                    url=url,
                    published_at=published_date
                )
            )
        
        # Create category models based on the categories in the news data
        news_categories = [
            next((cat for cat in categories if cat.name == cat_name), None)
            for cat_name in news_data_item["categories"]
        ]
        news_categories = [cat for cat in news_categories if cat is not None]
        
        news_item = News(
            id=i + 1,
            title=news_data_item["title"],
            content=news_data_item["content"],
            summary=news_data_item["summary"],
            url=news_urls[0].url,  # Use the first URL as the primary one
            published_at=published_date,
            image_url=f"https://example.com/images/news-{i+1}.jpg",
            impact_prediction=news_data_item.get("impact_prediction", "unsure"),
            impact_prediction_justification=news_data_item.get("impact_prediction_justification", "No justification provided."),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            categories=news_categories,
            news_urls=news_urls,
            sources=sources
        )
        
        news_items.append(news_item)
                
    # Create the final result dictionary
    user.news = [news.model_dump() for news in news_items]
    result = {
        "user": user.model_dump(),
        "news": [news.model_dump() for news in news_items],
        "sources": [source.model_dump() for source in sources],
        "categories": [category.model_dump() for category in categories]
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
        print(f"     - Impact: {news['impact_prediction']}")
        print()

def save_to_database(data: Dict[str, Any]) -> None:
    """
    Saves the generated mock data to the database.
    
    Args:
        data: The mock data dictionary
    """
    # Create a database session
    db = SessionLocal()
    
    try:
        print("\n=== SAVING TO DATABASE ===")
        
        # Ensure schema exists
        create_schema_if_not_exists()
        
        # 1. Save user
        user_data = data['user']
        db_user = User(
            name=user_data['name'],
            email=user_data['email'],
            profile_picture=user_data['profile_picture'],
            created_at=datetime.fromisoformat(user_data['created_at']) if isinstance(user_data['created_at'], str) else user_data['created_at'],
            updated_at=datetime.fromisoformat(user_data['updated_at']) if isinstance(user_data['updated_at'], str) else user_data['updated_at'],
            last_login=datetime.fromisoformat(user_data['last_login']) if isinstance(user_data['last_login'], str) else user_data['last_login']
        )
        db.add(db_user)
        db.flush()  # Flush to get the user ID
        print(f"Added user: {db_user.name}")
        
        # 2. Save categories
        categories_map = {}  # To store category_name -> db_category mapping
        for category_data in data['categories']:
            db_category = Category(
                id=category_data['id'],
                name=category_data['name']
            )
            db.add(db_category)
            categories_map[category_data['name']] = db_category
        db.flush()
        print(f"Added {len(categories_map)} categories")
        
        # 3. Save sources
        sources_map = {}  # To store source_id -> db_source mapping
        for source_data in data['sources']:
            db_source = Source(
                id=source_data['id'],
                codename=source_data['codename'],
                name=source_data['name'],
                website=source_data['website']
            )
            db.add(db_source)
            sources_map[source_data['id']] = db_source
        db.flush()
        print(f"Added {len(sources_map)} sources")
        
        # 4. Save news and related data
        for news_data in data['news']:
            # Create the news item
            db_news = News(
                id=news_data['id'],
                title=news_data['title'],
                content=news_data['content'],
                summary=news_data['summary'],
                url=news_data['url'],
                image_url=news_data['image_url'],
                impact_prediction=news_data['impact_prediction'],
                impact_prediction_justification=news_data['impact_prediction_justification'],
                created_at=datetime.fromisoformat(news_data['created_at']) if isinstance(news_data['created_at'], str) else news_data['created_at'],
                updated_at=datetime.fromisoformat(news_data['updated_at']) if isinstance(news_data['updated_at'], str) else news_data['updated_at']
            )
            
            db.add(db_news)
            db.flush()  # Flush to get the news ID
            
            # Add categories to news
            for category_data in news_data['categories']:
                # In the association table, we're linking to category_name directly
                # We need to add a raw SQL statement to insert into the association table
                stmt = news_categories.insert().values(
                    news_id=db_news.id,
                    category_name=category_data['name']
                )
                db.execute(stmt)
            
            # Create user-news relationship
            stmt = user_news.insert().values(
                user_id=db_user.id,
                news_id=db_news.id
            )
            db.execute(stmt)
            
            # Save news URLs
            for url_data in news_data['news_urls']:
                source_id = url_data['source_id']
                db_news_url = NewsUrl(
                    id=url_data['id'],
                    source_id=source_id,
                    news_id=db_news.id,
                    url=url_data['url'],
                    published_at=datetime.fromisoformat(url_data['published_at']) if isinstance(url_data['published_at'], str) else url_data['published_at']
                )
                db.add(db_news_url)
            
            print(f"Added news: {db_news.title} with {len(news_data['news_urls'])} URLs")
        
        # Commit the transaction
        db.commit()
        print("\n=== SAVED SUCCESSFULLY ===")
    
    except Exception as e:
        # If there's an error, rollback the transaction
        db.rollback()
        print(f"\n=== ERROR SAVING TO DATABASE ===")
        print(f"Error: {str(e)}")
        raise
    
    finally:
        # Close the session
        db.close()

if __name__ == "__main__":
    # Generate the mock data
    mock_data = generate_mock_data()
    
    # Print a summary
    print_mock_data_summary(mock_data)
    
    # Save to JSON file
    save_mock_data_to_json(mock_data)
    
    # Ask user if they want to save to database
    save_to_db = input("\nDo you want to save this data to the database? (y/n): ").lower().strip() == 'y'
    
    if save_to_db:
        save_to_database(mock_data)
    else:
        print("Data was not saved to the database.")