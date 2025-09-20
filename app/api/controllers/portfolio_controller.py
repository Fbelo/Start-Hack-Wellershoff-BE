from fastapi import HTTPException, APIRouter
from typing import List
from app.services.portfolio_asset import PortfolioAssetService
from app.api.schemas.portfolio_asset import PortfolioAssetModel, AssetType

# Create portfolio router
portfolio_router = APIRouter(
    prefix="/api/v1/portfolio",
    tags=["portfolio"],
    responses={404: {"description": "Not found"}},
)

class PortfolioController:
    @staticmethod
    async def get_user_portfolio(user_id: str):
        """
        Get all portfolio assets for a user
        """
        return PortfolioAssetService.get_all_by_user(user_id)

    @staticmethod
    async def get_asset_by_id(asset_id: str):
        """
        Get a specific portfolio asset by ID
        """
        asset = PortfolioAssetService.get_by_id(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Portfolio asset not found")
        return asset

    @staticmethod
    async def get_assets_by_type(user_id: str, asset_type: AssetType):
        """
        Get portfolio assets by type for a user
        """
        return PortfolioAssetService.get_by_type(user_id, asset_type)

    @staticmethod
    async def get_asset_by_symbol(user_id: str, symbol: str):
        """
        Get a portfolio asset by symbol for a user
        """
        asset = PortfolioAssetService.get_by_symbol(user_id, symbol)
        if not asset:
            raise HTTPException(status_code=404, detail="Portfolio asset not found")
        return asset

    @staticmethod
    async def create_asset(asset: PortfolioAssetModel):
        """
        Create a new portfolio asset
        """
        try:
            return PortfolioAssetService.create(asset)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def update_asset(asset_id: str, asset: PortfolioAssetModel):
        """
        Update a portfolio asset
        """
        updated_asset = PortfolioAssetService.update(asset_id, asset.dict(exclude={"id"}))
        if not updated_asset:
            raise HTTPException(status_code=404, detail="Portfolio asset not found")
        return updated_asset

    @staticmethod
    async def delete_asset(asset_id: str):
        """
        Delete a portfolio asset
        """
        result = PortfolioAssetService.delete(asset_id)
        if not result:
            raise HTTPException(status_code=404, detail="Portfolio asset not found")
        return True

    @staticmethod
    async def create_demo_portfolio(user_id: str):
        """
        Create a demo portfolio for a user
        """
        try:
            return PortfolioAssetService.create_demo_portfolio(user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


# Define routes
@portfolio_router.get("/{user_id}", response_model=List[PortfolioAssetModel])
async def get_user_portfolio(user_id: str):
    return await PortfolioController.get_user_portfolio(user_id=user_id)

@portfolio_router.get("/asset/{asset_id}", response_model=PortfolioAssetModel)
async def get_asset_by_id(asset_id: str):
    return await PortfolioController.get_asset_by_id(asset_id=asset_id)

@portfolio_router.get("/{user_id}/type/{asset_type}", response_model=List[PortfolioAssetModel])
async def get_assets_by_type(user_id: str, asset_type: AssetType):
    return await PortfolioController.get_assets_by_type(user_id=user_id, asset_type=asset_type)

@portfolio_router.get("/{user_id}/symbol/{symbol}", response_model=PortfolioAssetModel)
async def get_asset_by_symbol(user_id: str, symbol: str):
    return await PortfolioController.get_asset_by_symbol(user_id=user_id, symbol=symbol)

@portfolio_router.post("/", response_model=PortfolioAssetModel, status_code=201)
async def create_asset(asset: PortfolioAssetModel):
    return await PortfolioController.create_asset(asset=asset)

@portfolio_router.put("/{asset_id}", response_model=PortfolioAssetModel)
async def update_asset(asset_id: str, asset: PortfolioAssetModel):
    return await PortfolioController.update_asset(asset_id=asset_id, asset=asset)

@portfolio_router.delete("/{asset_id}", response_model=bool)
async def delete_asset(asset_id: str):
    return await PortfolioController.delete_asset(asset_id=asset_id)

@portfolio_router.post("/demo/{user_id}", response_model=List[PortfolioAssetModel], status_code=201)
async def create_demo_portfolio(user_id: str):
    return await PortfolioController.create_demo_portfolio(user_id=user_id)