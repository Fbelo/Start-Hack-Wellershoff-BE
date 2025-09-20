from typing import List, Optional, Dict
from datetime import datetime
from app.db.firebase import get_firestore_db, COLLECTION_USERS
from app.models.user import UserModel
from google.cloud.firestore_v1.base_query import FieldFilter
import uuid

class UserService:
    """
    Service for handling user operations
    """
    
    @staticmethod
    def get_all(limit: int = 50) -> List[UserModel]:
        """
        Get all users
        """
        db = get_firestore_db()
        users_ref = db.collection(COLLECTION_USERS)
        
        query = users_ref.limit(limit)
        user_docs = query.stream()
        
        result = []
        for doc in user_docs:
            user_data = doc.to_dict()
            user_data["id"] = doc.id
            result.append(UserModel(**user_data))
            
        return result
    
    @staticmethod
    def get_by_id(user_id: str) -> Optional[UserModel]:
        """
        Get a user by ID
        """
        db = get_firestore_db()
        user_doc = db.collection(COLLECTION_USERS).document(user_id).get()
        
        if not user_doc.exists:
            return None
            
        user_data = user_doc.to_dict()
        user_data["id"] = user_doc.id
        return UserModel(**user_data)
    
    @staticmethod
    def get_by_email(email: str) -> Optional[UserModel]:
        """
        Get a user by email
        """
        db = get_firestore_db()
        query = db.collection(COLLECTION_USERS).where(
            filter=FieldFilter("email", "==", email)
        ).limit(1)
        
        users = list(query.stream())
        if not users:
            return None
            
        user_doc = users[0]
        user_data = user_doc.to_dict()
        user_data["id"] = user_doc.id
        return UserModel(**user_data)
    
    @staticmethod
    def create(user: UserModel) -> UserModel:
        """
        Create a new user
        """
        db = get_firestore_db()
        
        # Check if user with email already exists
        existing_user = UserService.get_by_email(user.email)
        if existing_user:
            raise ValueError(f"User with email {user.email} already exists")
        
        # Generate ID if not provided
        if not user.id:
            user.id = str(uuid.uuid4())
            
        # Set timestamps
        user.created_at = datetime.now()
        user.updated_at = datetime.now()
        
        # Save to Firestore
        user_ref = db.collection(COLLECTION_USERS).document(user.id)
        user_ref.set(user.to_dict())
        
        return user
    
    @staticmethod
    def update(user_id: str, updates: dict) -> Optional[UserModel]:
        """
        Update a user
        """
        db = get_firestore_db()
        user_ref = db.collection(COLLECTION_USERS).document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return None
            
        # Get current data and update
        user_data = user_doc.to_dict()
        user_data.update(updates)
        user_data["updated_at"] = datetime.now()
        
        # Save to Firestore
        user_ref.update(user_data)
        
        # Return updated user
        user_data["id"] = user_id
        return UserModel(**user_data)
    
    @staticmethod
    def delete(user_id: str) -> bool:
        """
        Delete a user
        """
        db = get_firestore_db()
        user_ref = db.collection(COLLECTION_USERS).document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return False
            
        user_ref.delete()
        return True
    
    @staticmethod
    def update_preferences(user_id: str, preferences: Dict[str, bool]) -> Optional[UserModel]:
        """
        Update a user's preferences
        """
        db = get_firestore_db()
        user_ref = db.collection(COLLECTION_USERS).document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return None
            
        # Get current data
        user_data = user_doc.to_dict()
        
        # Update preferences
        if "preferences" not in user_data:
            user_data["preferences"] = {}
        user_data["preferences"].update(preferences)
        user_data["updated_at"] = datetime.now()
        
        # Save to Firestore
        user_ref.update({
            "preferences": user_data["preferences"],
            "updated_at": user_data["updated_at"]
        })
        
        # Return updated user
        user_data["id"] = user_id
        return UserModel(**user_data)
    
    @staticmethod
    def record_login(user_id: str) -> Optional[UserModel]:
        """
        Record a user login
        """
        return UserService.update(user_id, {"last_login": datetime.now()})
    
    @staticmethod
    def create_fake_user() -> UserModel:
        """
        Create a fake user for demo purposes
        """
        fake_user = UserModel(
            name="Demo User",
            email="demo@example.com",
            profile_picture="https://ui-avatars.com/api/?name=Demo+User&background=random",
            preferences={
                "daily_news_digest": True,
                "portfolio_alerts": True,
                "market_updates": True
            }
        )
        return UserService.create(fake_user)