from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict
from app.services.user import UserService
from app.models.user import UserModel

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[UserModel])
async def get_all_users(limit: int = Query(50, ge=1, le=100)):
    """
    Get all users
    """
    return UserService.get_all(limit=limit)

@router.get("/{user_id}", response_model=UserModel)
async def get_user_by_id(user_id: str):
    """
    Get a specific user by ID
    """
    user = UserService.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/email/{email}", response_model=UserModel)
async def get_user_by_email(email: str):
    """
    Get a user by email
    """
    user = UserService.get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserModel, status_code=201)
async def create_user(user: UserModel):
    """
    Create a new user
    """
    try:
        return UserService.create(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=UserModel)
async def update_user(user_id: str, user: UserModel):
    """
    Update a user
    """
    updated_user = UserService.update(user_id, user.dict(exclude={"id"}))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=bool)
async def delete_user(user_id: str):
    """
    Delete a user
    """
    result = UserService.delete(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return True

@router.patch("/{user_id}/preferences", response_model=UserModel)
async def update_user_preferences(user_id: str, preferences: Dict[str, bool] = Body(...)):
    """
    Update a user's preferences
    """
    updated_user = UserService.update_preferences(user_id, preferences)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.post("/login/{user_id}", response_model=UserModel)
async def login_user(user_id: str):
    """
    Record a user login
    """
    updated_user = UserService.record_login(user_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.post("/demo", response_model=UserModel, status_code=201)
async def create_demo_user():
    """
    Create a demo user for testing
    """
    try:
        return UserService.create_fake_user()
    except ValueError as e:
        # If demo user already exists, try to retrieve it
        user = UserService.get_by_email("demo@example.com")
        if user:
            return user
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))