from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from app.db.models import News, Category
from app.api.schemas.news import NewsModel, NewsCreate, NewsUpdate, ImpactType

class NewsService:
    """
    Service for handling news operations
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
        
        # Get news articles with this category
        news = db.query(News).filter(
            News.categories.any(id=category_obj.id)
        ).order_by(desc(News.published_at)).offset(offset).limit(limit).all()
        
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
        for category_name in news_data.categories:
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
            source=news_data.source,
            url=news_data.url,
            published_at=news_data.published_at,
            image_url=news_data.image_url,
            impact_prediction=news_data.impact_prediction,
            impact_score=news_data.impact_score,
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
        if news_data.source is not None:
            news.source = news_data.source
        if news_data.image_url is not None:
            news.image_url = news_data.image_url
        if news_data.impact_prediction is not None:
            news.impact_prediction = news_data.impact_prediction
        if news_data.impact_score is not None:
            news.impact_score = news_data.impact_score
        
        # Update categories if provided
        if news_data.categories is not None:
            categories = []
            for category_name in news_data.categories:
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
    
    @staticmethod
    def predict_impact(db: Session, news_id: int, impact_type: ImpactType, impact_score: float) -> Optional[NewsModel]:
        """
        Update the impact prediction for a news article
        """
        news = db.query(News).filter(News.id == news_id).first()
        if not news:
            return None
        
        news.impact_prediction = impact_type
        news.impact_score = impact_score
        news.updated_at = datetime.now()
        
        try:
            db.commit()
            db.refresh(news)
            return NewsModel.model_validate(news)
        except IntegrityError:
            db.rollback()
            return None