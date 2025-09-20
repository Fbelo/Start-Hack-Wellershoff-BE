from fastapi import HTTPException, Query, APIRouter
from typing import List
from app.services.news import NewsService
from app.api.schemas.news import NewsModel, ImpactType

# Create news router
news_router = APIRouter(
    prefix="/api/v1/news",
    tags=["news"],
    responses={404: {"description": "Not found"}},
)

class NewsController:
    @staticmethod
    async def get_all_news(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
        """
        Get all news articles with pagination
        """
        return NewsService.get_all(limit=limit, offset=offset)

    @staticmethod
    async def get_news_by_id(news_id: str):
        """
        Get a specific news article by ID
        """
        news = NewsService.get_by_id(news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News article not found")
        return news

    @staticmethod
    async def search_news(query: str, limit: int = Query(20, ge=1, le=50)):
        """
        Search for news articles
        """
        return NewsService.search(query, limit=limit)

    @staticmethod
    async def get_news_by_impact(impact_type: ImpactType, limit: int = Query(20, ge=1, le=50)):
        """
        Get news articles by impact prediction
        """
        return NewsService.get_by_impact(impact_type, limit=limit)

    @staticmethod
    async def create_news(news: NewsModel):
        """
        Create a new news article
        """
        try:
            return NewsService.create(news)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def update_news(news_id: str, news: NewsModel):
        """
        Update a news article
        """
        updated_news = NewsService.update(news_id, news.dict(exclude={"id"}))
        if not updated_news:
            raise HTTPException(status_code=404, detail="News article not found")
        return updated_news

    @staticmethod
    async def delete_news(news_id: str):
        """
        Delete a news article
        """
        result = NewsService.delete(news_id)
        if not result:
            raise HTTPException(status_code=404, detail="News article not found")
        return True


# Define routes
@news_router.get("/", response_model=List[NewsModel])
async def get_all_news(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    return await NewsController.get_all_news(limit=limit, offset=offset)

@news_router.get("/{news_id}", response_model=NewsModel)
async def get_news_by_id(news_id: str):
    return await NewsController.get_news_by_id(news_id=news_id)

@news_router.get("/search/", response_model=List[NewsModel])
async def search_news(query: str, limit: int = Query(20, ge=1, le=50)):
    return await NewsController.search_news(query=query, limit=limit)

@news_router.get("/impact/{impact_type}", response_model=List[NewsModel])
async def get_news_by_impact(impact_type: ImpactType, limit: int = Query(20, ge=1, le=50)):
    return await NewsController.get_news_by_impact(impact_type=impact_type, limit=limit)

@news_router.post("/", response_model=NewsModel, status_code=201)
async def create_news(news: NewsModel):
    return await NewsController.create_news(news=news)

@news_router.put("/{news_id}", response_model=NewsModel)
async def update_news(news_id: str, news: NewsModel):
    return await NewsController.update_news(news_id=news_id, news=news)

@news_router.delete("/{news_id}", response_model=bool)
async def delete_news(news_id: str):
    return await NewsController.delete_news(news_id=news_id)