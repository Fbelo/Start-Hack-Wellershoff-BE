from fastapi import HTTPException, APIRouter, Depends, Body, Query, Path
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import PortfolioAsset, Tag
from app.api.schemas.portfolio import PortfolioAssetModel, PortfolioAssetCreate, PortfolioAssetUpdate, AssetType
from app.db.database import get_db

# Create portfolio router
portfolio_router = APIRouter(
    prefix="/api/v1/portfolio",
    tags=["portfolio"],
    responses={404: {"description": "Not found"}},
)

class PortfolioController:
    """
    Controller for handling portfolio asset operations
    """
    
    @staticmethod
    def get_all_by_user(db: Session, user_id: int) -> List[PortfolioAssetModel]:
        """
        Get all portfolio assets for a user
        """
        assets = db.query(PortfolioAsset).filter(PortfolioAsset.user_id == user_id).all()
        return [PortfolioAssetModel.model_validate(asset) for asset in assets]

    @staticmethod
    def create(db: Session, asset_data: PortfolioAssetCreate) -> PortfolioAssetModel:
        """
        Create a new portfolio asset
        """
        # Process tags
        tags = []
        for tag_name in asset_data.tags:
            # Find or create tag
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()  # Flush to get the ID
            tags.append(tag)
        
        # Create asset
        asset = PortfolioAsset(
            user_id=asset_data.user_id,
            symbol=asset_data.symbol,
            name=asset_data.name,
            asset_type=asset_data.asset_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=tags
        )
        
        try:
            db.add(asset)
            db.commit()
            db.refresh(asset)
            return PortfolioAssetModel.model_validate(asset)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Failed to create portfolio asset: {str(e)}")
    
    
    @staticmethod
    def delete(db: Session, asset_id: int) -> bool:
        """
        Delete a portfolio asset
        """
        asset = db.query(PortfolioAsset).filter(PortfolioAsset.id == asset_id).first()
        if not asset:
            return False
        
        try:
            db.delete(asset)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
    
    @staticmethod
    def get_by_tag(db: Session, tag: str, user_id: int) -> List[PortfolioAssetModel]:
        """
        Get portfolio assets by tag
        """
        # Find the tag
        tag_obj = db.query(Tag).filter(Tag.name == tag).first()
        if not tag_obj:
            return []
        
        # Get assets with this tag for the specified user
        assets = db.query(PortfolioAsset).filter(
            PortfolioAsset.user_id == user_id,
            PortfolioAsset.tags.any(id=tag_obj.id)
        ).all()
        
        return [PortfolioAssetModel.model_validate(asset) for asset in assets]
        
    @staticmethod
    def create_demo_portfolio(db: Session, user_id: int) -> List[PortfolioAssetModel]:
        """
        Create a demo portfolio for a user
        """
        demo_assets = [
            PortfolioAssetCreate(
                user_id=user_id,
                symbol="AAPL",
                name="Apple Inc.",
                asset_type=AssetType.STOCK,
                tags=["tech", "consumer", "dividend"]
            ),
            PortfolioAssetCreate(
                user_id=user_id,
                symbol="MSFT",
                name="Microsoft Corporation",
                asset_type=AssetType.STOCK,
                tags=["tech", "software", "dividend"]
            ),
            PortfolioAssetCreate(
                user_id=user_id,
                symbol="AMZN",
                name="Amazon.com Inc.",
                asset_type=AssetType.STOCK,
                tags=["tech", "retail", "growth"]
            ),
            PortfolioAssetCreate(
                user_id=user_id,
                symbol="BTC",
                name="Bitcoin",
                asset_type=AssetType.CRYPTO,
                tags=["crypto", "digital asset"]
            ),
            PortfolioAssetCreate(
                user_id=user_id,
                symbol="SPY",
                name="SPDR S&P 500 ETF Trust",
                asset_type=AssetType.ETF,
                tags=["index", "S&P 500", "diversified"]
            )
        ]
        
        created_assets = []
        for asset_data in demo_assets:
            try:
                # Check if asset already exists for this user
                existing = PortfolioController.get_by_symbol_and_user(db, asset_data.symbol, user_id)
                if existing:
                    created_assets.append(existing)
                    continue
                
                # Create new asset
                asset = PortfolioController.create(db, asset_data)
                created_assets.append(asset)
            except Exception as e:
                # Log error but continue with other assets
                print(f"Error creating demo asset {asset_data.symbol}: {str(e)}")
        
        return created_assets


# Define routes
@portfolio_router.get("/{user_id}", response_model=List[PortfolioAssetModel])
async def get_user_portfolio(user_id: int, db: Session = Depends(get_db)):
    """Get all portfolio assets for a user"""
    return PortfolioController.get_all_by_user(db=db, user_id=user_id)


@portfolio_router.get("/{user_id}/tag/{tag}", response_model=List[PortfolioAssetModel])
async def get_assets_by_tag(user_id: int, tag: str, db: Session = Depends(get_db)):
    """Get portfolio assets by tag for a user"""
    return PortfolioController.get_by_tag(db=db, tag=tag, user_id=user_id)

@portfolio_router.post("/", response_model=PortfolioAssetModel, status_code=201)
async def create_asset(asset: PortfolioAssetCreate, db: Session = Depends(get_db)):
    """Create a new portfolio asset"""
    try:
        return PortfolioController.create(db=db, asset_data=asset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@portfolio_router.put("/{asset_id}", response_model=PortfolioAssetModel)
async def update_asset(asset_id: int, asset: PortfolioAssetUpdate, db: Session = Depends(get_db)):
    """Update a portfolio asset"""
    updated_asset = PortfolioController.update(db=db, asset_id=asset_id, asset_data=asset)
    if not updated_asset:
        raise HTTPException(status_code=404, detail="Portfolio asset not found")
    return updated_asset

@portfolio_router.delete("/{asset_id}", response_model=bool)
async def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """Delete a portfolio asset"""
    result = PortfolioController.delete(db=db, asset_id=asset_id)
    if not result:
        raise HTTPException(status_code=404, detail="Portfolio asset not found")
    return True

@portfolio_router.post("/demo/{user_id}", response_model=List[PortfolioAssetModel], status_code=201)
async def create_demo_portfolio(user_id: int, db: Session = Depends(get_db)):
    """Create a demo portfolio for a user"""
    try:
        return PortfolioController.create_demo_portfolio(db=db, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))