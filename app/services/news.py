from typing import List, Optional
from datetime import datetime
from app.db.firebase import get_firestore_db, COLLECTION_NEWS
from app.models.news import NewsModel, ImpactType
from google.cloud.firestore_v1.base_query import FieldFilter
import uuid

class NewsService:
    """
    Service for handling news operations
    """
    
    @staticmethod
    def get_all(limit: int = 50, offset: int = 0) -> List[NewsModel]:
        """
        Get all news articles with pagination
        """
        db = get_firestore_db()
        news_ref = db.collection(COLLECTION_NEWS)
        
        # Query with ordering and pagination
        query = news_ref.order_by("published_at", direction="DESCENDING").offset(offset).limit(limit)
        news_docs = query.stream()
        
        result = []
        for doc in news_docs:
            news_data = doc.to_dict()
            news_data["id"] = doc.id
            result.append(NewsModel(**news_data))
            
        return result
    
    @staticmethod
    def get_by_id(news_id: str) -> Optional[NewsModel]:
        """
        Get a news article by ID
        """
        db = get_firestore_db()
        news_doc = db.collection(COLLECTION_NEWS).document(news_id).get()
        
        if not news_doc.exists:
            return None
            
        news_data = news_doc.to_dict()
        news_data["id"] = news_doc.id
        return NewsModel(**news_data)
    
    @staticmethod
    def create(news: NewsModel) -> NewsModel:
        """
        Create a new news article
        """
        db = get_firestore_db()
        
        # Generate ID if not provided
        if not news.id:
            news.id = str(uuid.uuid4())
            
        # Set timestamps
        news.created_at = datetime.now()
        news.updated_at = datetime.now()
        
        # Save to Firestore
        news_ref = db.collection(COLLECTION_NEWS).document(news.id)
        news_ref.set(news.to_dict())
        
        return news
    
    @staticmethod
    def update(news_id: str, updates: dict) -> Optional[NewsModel]:
        """
        Update a news article
        """
        db = get_firestore_db()
        news_ref = db.collection(COLLECTION_NEWS).document(news_id)
        news_doc = news_ref.get()
        
        if not news_doc.exists:
            return None
            
        # Get current data and update
        news_data = news_doc.to_dict()
        news_data.update(updates)
        news_data["updated_at"] = datetime.now()
        
        # Save to Firestore
        news_ref.update(news_data)
        
        # Return updated news
        news_data["id"] = news_id
        return NewsModel(**news_data)
    
    @staticmethod
    def delete(news_id: str) -> bool:
        """
        Delete a news article
        """
        db = get_firestore_db()
        news_ref = db.collection(COLLECTION_NEWS).document(news_id)
        news_doc = news_ref.get()
        
        if not news_doc.exists:
            return False
            
        news_ref.delete()
        return True
    
    @staticmethod
    def search(query: str, limit: int = 20) -> List[NewsModel]:
        """
        Search for news articles by title or content
        Note: This is a simple implementation. For production, consider using Firebase's full-text search capabilities
        or integrating with a dedicated search service like Algolia.
        """
        db = get_firestore_db()
        
        # Search in title
        title_query = db.collection(COLLECTION_NEWS).where(
            filter=FieldFilter("title", ">=", query)
        ).where(
            filter=FieldFilter("title", "<=", query + "\uf8ff")
        ).limit(limit)
        
        # Get results
        results = []
        for doc in title_query.stream():
            news_data = doc.to_dict()
            news_data["id"] = doc.id
            results.append(NewsModel(**news_data))
            
        return results
    
    @staticmethod
    def get_by_impact(impact_type: ImpactType, limit: int = 20) -> List[NewsModel]:
        """
        Get news articles by impact prediction
        """
        db = get_firestore_db()
        
        query = db.collection(COLLECTION_NEWS).where(
            filter=FieldFilter("impact_prediction", "==", impact_type)
        ).order_by("published_at", direction="DESCENDING").limit(limit)
        
        results = []
        for doc in query.stream():
            news_data = doc.to_dict()
            news_data["id"] = doc.id
            results.append(NewsModel(**news_data))
            
        return results