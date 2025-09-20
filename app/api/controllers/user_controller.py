from fastapi import HTTPException, Query, Body, Depends, APIRouter
from typing import List, Dict
from sqlalchemy.orm import Session
from app.services.user import UserService
from app.api.schemas.user import UserModel, UserCreate, UserUpdate
from app.db.database import get_db

# Create user router
user_router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

class UserController:
    @staticmethod
    async def get_all_users(
        limit: int = Query(50, ge=1, le=100),
        db: Session = Depends(get_db)
    ):
        """
        Get all users
        """
        return UserService.get_all(db, limit=limit)

    @staticmethod
    async def get_user_by_id(
        user_id: int,
        db: Session = Depends(get_db)
    ):
        """
        Get a specific user by ID
        """
        user = UserService.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    async def get_user_by_email(
        email: str,
        db: Session = Depends(get_db)
    ):
        """
        Get a user by email
        """
        user = UserService.get_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    async def create_user(
        user: UserCreate,
        db: Session = Depends(get_db)
    ):
        """
        Create a new user
        """
        try:
            return UserService.create(db, user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_user(
        user_id: int,
        user: UserUpdate,
        db: Session = Depends(get_db)
    ):
        """
        Update a user
        """
        updated_user = UserService.update(db, user_id, user)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user

    @staticmethod
    async def delete_user(
        user_id: int,
        db: Session = Depends(get_db)
    ):
        """
        Delete a user
        """
        result = UserService.delete(db, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return True

    @staticmethod
    async def update_user_preferences(
        user_id: int,
        preferences: Dict[str, bool] = Body(...),
        db: Session = Depends(get_db)
    ):
        """
        Update a user's preferences
        """
        updated_user = UserService.update_preferences(db, user_id, preferences)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user


# Define routes
@user_router.get("/", response_model=List[UserModel])
async def get_all_users(limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    return await UserController.get_all_users(limit=limit, db=db)

@user_router.get("/{user_id}", response_model=UserModel)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return await UserController.get_user_by_id(user_id=user_id, db=db)

@user_router.get("/email/{email}", response_model=UserModel)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    return await UserController.get_user_by_email(email=email, db=db)

@user_router.post("/", response_model=UserModel, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return await UserController.create_user(user=user, db=db)

@user_router.put("/{user_id}", response_model=UserModel)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return await UserController.update_user(user_id=user_id, user=user, db=db)

@user_router.delete("/{user_id}", response_model=bool)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    return await UserController.delete_user(user_id=user_id, db=db)

@user_router.patch("/{user_id}/preferences", response_model=UserModel)
async def update_user_preferences(user_id: int, preferences: Dict[str, bool] = Body(...), db: Session = Depends(get_db)):
    return await UserController.update_user_preferences(user_id=user_id, preferences=preferences, db=db)