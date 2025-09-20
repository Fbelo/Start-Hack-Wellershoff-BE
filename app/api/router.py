from fastapi import APIRouter

# Import routers from controller modules
from app.api.controllers.user import user_router
from app.api.controllers.news import news_router
from app.api.controllers.portfolio import portfolio_router
from app.api.controllers.prediction import prediction_router

# Create a top-level router
router = APIRouter()

# Include all the specific routers
router.include_router(user_router)
router.include_router(news_router)
router.include_router(portfolio_router)
router.include_router(prediction_router)
