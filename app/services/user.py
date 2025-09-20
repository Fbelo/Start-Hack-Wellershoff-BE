from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.models.user import User, UserModel, UserCreate, UserUpdate
from fastapi import Depends, HTTPException

class UserService:
    """
    Service for handling user operations
    """
    
    @staticmethod
    def get_all(db: Session, limit: int = 50) -> List[UserModel]:
        """
        Get all users
        """
        users = db.query(User).limit(limit).all()
        return [UserModel.model_validate(user) for user in users]
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[UserModel]:
        """
        Get a user by ID
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return UserModel.model_validate(user)
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[UserModel]:
        """
        Get a user by email
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        return UserModel.model_validate(user)
    
    @staticmethod
    def create(db: Session, user_data: UserCreate) -> UserModel:
        """
        Create a new user
        """
        # Check if user with email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")
        
        # Create new user
        user = User(
            name=user_data.name,
            email=user_data.email,
            profile_picture=user_data.profile_picture,
            preferences=user_data.preferences,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return UserModel.model_validate(user)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Failed to create user: {str(e)}")
    
    @staticmethod
    def update(db: Session, user_id: int, user_data: UserUpdate) -> Optional[UserModel]:
        """
        Update a user
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Update fields if provided
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.profile_picture is not None:
            user.profile_picture = user_data.profile_picture
        if user_data.preferences is not None:
            user.preferences = user_data.preferences
        if user_data.last_login is not None:
            user.last_login = user_data.last_login
        
        user.updated_at = datetime.now()
        
        try:
            db.commit()
            db.refresh(user)
            return UserModel.model_validate(user)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Failed to update user: {str(e)}")
    
    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """
        Delete a user
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        try:
            db.delete(user)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
    
    @staticmethod
    def update_preferences(db: Session, user_id: int, preferences: Dict[str, bool]) -> Optional[UserModel]:
        """
        Update a user's preferences
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Update preferences
        if not user.preferences:
            user.preferences = {}
        user.preferences.update(preferences)
        user.updated_at = datetime.now()
        
        try:
            db.commit()
            db.refresh(user)
            return UserModel.model_validate(user)
        except IntegrityError:
            db.rollback()
            return None
    
    @staticmethod
    def record_login(db: Session, user_id: int) -> Optional[UserModel]:
        """
        Record a user login
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        user.last_login = datetime.now()
        user.updated_at = datetime.now()
        
        try:
            db.commit()
            db.refresh(user)
            return UserModel.model_validate(user)
        except IntegrityError:
            db.rollback()
            return None
    
    @staticmethod
    def create_fake_user(db: Session) -> UserModel:
        """
        Create a fake user for demo purposes
        """
        fake_user_data = UserCreate(
            name="Demo User",
            email="demo@example.com",
            profile_picture="https://ui-avatars.com/api/?name=Demo+User&background=random",
            preferences={
                "daily_news_digest": True,
                "portfolio_alerts": True,
                "market_updates": True
            }
        )
        
        try:
            return UserService.create(db, fake_user_data)
        except ValueError:
            # If user already exists, get it
            return UserService.get_by_email(db, "demo@example.com")