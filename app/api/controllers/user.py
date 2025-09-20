from fastapi import HTTPException, Query, Body, Depends, APIRouter
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import User
from app.api.schemas.user import UserModel, UserCreate, UserUpdate
from app.db.database import get_db

# Create user router
user_router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

class UserController:
    """
    Controller for handling user operations
    """
    
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
    async def api_get_user_by_id(
        user_id: int,
        db: Session = Depends(get_db)
    ):
        """
        Get a specific user by ID
        """
        user = UserController.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    async def api_get_user_by_email(
        email: str,
        db: Session = Depends(get_db)
    ):
        """
        Get a user by email
        """
        user = UserController.get_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    async def api_create_user(
        user: UserCreate,
        db: Session = Depends(get_db)
    ):
        """
        Create a new user
        """
        try:
            return UserController.create(db, user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def api_update_user(
        user_id: int,
        user: UserUpdate,
        db: Session = Depends(get_db)
    ):
        """
        Update a user
        """
        updated_user = UserController.update(db, user_id, user)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user

    @staticmethod
    async def api_delete_user(
        user_id: int,
        db: Session = Depends(get_db)
    ):
        """
        Delete a user
        """
        result = UserController.delete(db, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return True



@user_router.get("/{user_id}", response_model=UserModel)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return await UserController.api_get_user_by_id(user_id=user_id, db=db)

@user_router.get("/email/{email}", response_model=UserModel)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    return await UserController.api_get_user_by_email(email=email, db=db)

@user_router.post("/", response_model=UserModel, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return await UserController.api_create_user(user=user, db=db)

@user_router.put("/{user_id}", response_model=UserModel)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return await UserController.api_update_user(user_id=user_id, user=user, db=db)

@user_router.delete("/{user_id}", response_model=bool)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    return await UserController.api_delete_user(user_id=user_id, db=db)