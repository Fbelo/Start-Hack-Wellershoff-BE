from fastapi import HTTPException, Query, APIRouter, Depends, Body
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from app.db.models import News, Category
from app.api.schemas.news import NewsModel, NewsCreate, NewsUpdate, ImpactType
from app.db.database import get_db

# Create news router
news_router = APIRouter(
    prefix="/api/v1/news",
    tags=["news"],
    responses={404: {"description": "Not found"}},
)

class NewsController:
    """
    Controller for handling news operations
    """
    
    @staticmethod
    def get_all(db: Session, limit: int = 50, offset: int = 0) -> List[NewsModel]:
        """
        Get all news articles with pagination
        """
        news = db.query(News).order_by(desc(News.published_at)).offset(offset).limit(limit).all()
        return [NewsModel.model_validate(item) for item in news]
    
    @staticmethod
    def get_by_id(db: Session, news_id: int) -> Optional[NewsModel]:
        """
        Get a news article by ID
        """
        news = db.query(News).filter(News.id == news_id).first()
        if not news:
            return None
        return NewsModel.model_validate(news)
    
    @staticmethod
    def get_by_category(db: Session, category: str, limit: int = 50, offset: int = 0) -> List[NewsModel]:
        """
        Get news articles by category
        """
        # Find the category
        category_obj = db.query(Category).filter(Category.name == category).first()
        if not category_obj:
            return []
            
    @staticmethod
    def get_by_impact(db: Session, impact_type: ImpactType, limit: int = 100, offset: int = 0) -> List[NewsModel]:
        """
        Get news articles by impact prediction type
        """
        news = db.query(News).filter(News.impact_prediction == impact_type).order_by(desc(News.published_at)).offset(offset).limit(limit).all()
        return [NewsModel.model_validate(item) for item in news]
        
    
    @staticmethod
    def search(db: Session, query: str, limit: int = 50, offset: int = 0) -> List[NewsModel]:
        """
        Search news articles by title or content
        """
        search_term = f"%{query}%"
        news = db.query(News).filter(
            (News.title.ilike(search_term)) | (News.content.ilike(search_term))
        ).order_by(desc(News.published_at)).offset(offset).limit(limit).all()
        
        return [NewsModel.model_validate(item) for item in news]
    
    @staticmethod
    def create(db: Session, news_data: NewsCreate) -> NewsModel:
        """
        Create a new news article
        """
        # Process categories
        categories = []
        for category_name in news_data.category_names:
            # Find or create category
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                category = Category(name=category_name)
                db.add(category)
                db.flush()  # Flush to get the ID
            categories.append(category)
        
        # Create news article
        news = News(
            title=news_data.title,
            content=news_data.content,
            summary=news_data.summary,
            url=news_data.url,
            published_at=news_data.published_at,
            image_url=news_data.image_url,
            impact_prediction=news_data.impact_prediction,
            impact_prediction_justification=news_data.impact_prediction_justification,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            categories=categories
        )
        
        try:
            db.add(news)
            db.commit()
            db.refresh(news)
            return NewsModel.model_validate(news)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Failed to create news article: {str(e)}")
    
    @staticmethod
    def update(db: Session, news_id: int, news_data: NewsUpdate) -> Optional[NewsModel]:
        """
        Update a news article
        """
        news = db.query(News).filter(News.id == news_id).first()
        if not news:
            return None
        
        # Update fields if provided
        if news_data.title is not None:
            news.title = news_data.title
        if news_data.content is not None:
            news.content = news_data.content
        if news_data.summary is not None:
            news.summary = news_data.summary
        if news_data.image_url is not None:
            news.image_url = news_data.image_url
        if news_data.impact_prediction is not None:
            news.impact_prediction = news_data.impact_prediction
        if news_data.impact_prediction_justification is not None:
            news.impact_prediction_justification = news_data.impact_prediction_justification
        
        # Update categories if provided
        if news_data.category_names is not None:
            categories = []
            for category_name in news_data.category_names:
                # Find or create category
                category = db.query(Category).filter(Category.name == category_name).first()
                if not category:
                    category = Category(name=category_name)
                    db.add(category)
                    db.flush()  # Flush to get the ID
                categories.append(category)
            news.categories = categories
        
        news.updated_at = datetime.now()
        
        try:
            db.commit()
            db.refresh(news)
            return NewsModel.model_validate(news)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Failed to update news article: {str(e)}")
    
    @staticmethod
    def delete(db: Session, news_id: int) -> bool:
        """
        Delete a news article
        """
        news = db.query(News).filter(News.id == news_id).first()
        if not news:
            return False
        
        try:
            db.delete(news)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
    
    @staticmethod
    def get_latest(db: Session, limit: int = 10) -> List[NewsModel]:
        """
        Get latest news articles
        """
        news = db.query(News).order_by(desc(News.published_at)).limit(limit).all()
        return [NewsModel.model_validate(item) for item in news]
    
            
    # API Endpoint Methods
    @staticmethod
    async def api_get_all_news(
        limit: int = Query(50, ge=1, le=100), 
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db)
    ):
        """
        Get all news articles with pagination
        """
        return NewsController.get_all(db, limit=limit, offset=offset)

    @staticmethod
    async def api_get_news_by_id(
        news_id: int,
        db: Session = Depends(get_db)
    ):
        """
        Get a specific news article by ID
        """
        news = NewsController.get_by_id(db, news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News article not found")
        return news

    @staticmethod
    async def api_get_news_by_category(
        category: str,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db)
    ):
        """
        Get news articles by category
        """
        return NewsController.get_by_category(db, category, limit=limit, offset=offset)

    @staticmethod
    async def api_search_news(
        query: str,
        limit: int = Query(20, ge=1, le=50),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db)
    ):
        """
        Search for news articles
        """
        return NewsController.search(db, query, limit=limit, offset=offset)


    @staticmethod
    async def api_update_news(
        news_id: int,
        news: NewsUpdate,
        db: Session = Depends(get_db)
    ):
        """
        Update a news article
        """
        updated_news = NewsController.update(db, news_id, news)
        if not updated_news:
            raise HTTPException(status_code=404, detail="News article not found")
        return updated_news
        
    @staticmethod
    async def api_get_latest_news(
        limit: int = Query(10, ge=1, le=50),
        db: Session = Depends(get_db)
    ):
        """
        Get latest news articles
        """
        return NewsController.get_latest(db, limit=limit)



# Define routes
@news_router.get("/", response_model=List[NewsModel])
async def get_all_news(
    limit: int = Query(50, ge=1, le=100), 
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return await NewsController.api_get_all_news(limit=limit, offset=offset, db=db)

@news_router.get("/{news_id}", response_model=NewsModel)
async def get_news_by_id(news_id: int, db: Session = Depends(get_db)):
    return await NewsController.api_get_news_by_id(news_id=news_id, db=db)

@news_router.get("/category/{category}", response_model=List[NewsModel])
async def get_news_by_category(
    category: str, 
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return await NewsController.api_get_news_by_category(category=category, limit=limit, offset=offset, db=db)

@news_router.get("/search/", response_model=List[NewsModel])
async def search_news(
    query: str, 
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return await NewsController.api_search_news(query=query, limit=limit, offset=offset, db=db)

@news_router.get("/latest/", response_model=List[NewsModel])
async def get_latest_news(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    return await NewsController.api_get_latest_news(limit=limit, db=db)

@news_router.put("/{news_id}", response_model=NewsModel)
async def update_news(news_id: int, news: NewsUpdate, db: Session = Depends(get_db)):
    return await NewsController.api_update_news(news_id=news_id, news=news, db=db)
