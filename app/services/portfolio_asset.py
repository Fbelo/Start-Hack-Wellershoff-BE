from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from app.db.postgres.database import get_db
from app.models.portfolio_asset import PortfolioAsset, PortfolioAssetModel, PortfolioAssetCreate, PortfolioAssetUpdate, Tag, AssetType
from fastapi import Depends, HTTPException

class PortfolioAssetService:
    """
    Service for handling portfolio asset operations
    """
    
    @staticmethod
    def get_all_by_user(db: Session, user_id: int) -> List[PortfolioAssetModel]:
        """
        Get all portfolio assets for a user
        """
        assets = db.query(PortfolioAsset).filter(PortfolioAsset.user_id == user_id).all()
        return [PortfolioAssetModel.from_orm(asset) for asset in assets]
    
    @staticmethod
    def get_by_id(db: Session, asset_id: int) -> Optional[PortfolioAssetModel]:
        """
        Get a portfolio asset by ID
        """
        asset = db.query(PortfolioAsset).filter(PortfolioAsset.id == asset_id).first()
        if not asset:
            return None
        return PortfolioAssetModel.from_orm(asset)
    
    @staticmethod
    def get_by_symbol_and_user(db: Session, symbol: str, user_id: int) -> Optional[PortfolioAssetModel]:
        """
        Get a portfolio asset by symbol and user ID
        """
        asset = db.query(PortfolioAsset).filter(
            PortfolioAsset.symbol == symbol,
            PortfolioAsset.user_id == user_id
        ).first()
        if not asset:
            return None
        return PortfolioAssetModel.from_orm(asset)
    
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
            quantity=asset_data.quantity,
            purchase_price=asset_data.purchase_price,
            current_price=asset_data.current_price,
            purchase_date=asset_data.purchase_date,
            sector=asset_data.sector,
            industry=asset_data.industry,
            country=asset_data.country,
            metadata=asset_data.metadata,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=tags
        )
        
        try:
            db.add(asset)
            db.commit()
            db.refresh(asset)
            return PortfolioAssetModel.from_orm(asset)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Failed to create portfolio asset: {str(e)}")
    
    @staticmethod
    def update(db: Session, asset_id: int, asset_data: PortfolioAssetUpdate) -> Optional[PortfolioAssetModel]:
        """
        Update a portfolio asset
        """
        asset = db.query(PortfolioAsset).filter(PortfolioAsset.id == asset_id).first()
        if not asset:
            return None
        
        # Update fields if provided
        if asset_data.symbol is not None:
            asset.symbol = asset_data.symbol
        if asset_data.name is not None:
            asset.name = asset_data.name
        if asset_data.asset_type is not None:
            asset.asset_type = asset_data.asset_type
        if asset_data.quantity is not None:
            asset.quantity = asset_data.quantity
        if asset_data.purchase_price is not None:
            asset.purchase_price = asset_data.purchase_price
        if asset_data.current_price is not None:
            asset.current_price = asset_data.current_price
        if asset_data.purchase_date is not None:
            asset.purchase_date = asset_data.purchase_date
        if asset_data.sector is not None:
            asset.sector = asset_data.sector
        if asset_data.industry is not None:
            asset.industry = asset_data.industry
        if asset_data.country is not None:
            asset.country = asset_data.country
        if asset_data.metadata is not None:
            asset.metadata = asset_data.metadata
        
        # Update tags if provided
        if asset_data.tags is not None:
            tags = []
            for tag_name in asset_data.tags:
                # Find or create tag
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.flush()  # Flush to get the ID
                tags.append(tag)
            asset.tags = tags
        
        asset.updated_at = datetime.now()
        
        try:
            db.commit()
            db.refresh(asset)
            return PortfolioAssetModel.from_orm(asset)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Failed to update portfolio asset: {str(e)}")
    
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
    def update_current_price(db: Session, asset_id: int, current_price: float) -> Optional[PortfolioAssetModel]:
        """
        Update the current price of a portfolio asset
        """
        asset = db.query(PortfolioAsset).filter(PortfolioAsset.id == asset_id).first()
        if not asset:
            return None
        
        asset.current_price = current_price
        asset.updated_at = datetime.now()
        
        try:
            db.commit()
            db.refresh(asset)
            return PortfolioAssetModel.from_orm(asset)
        except IntegrityError:
            db.rollback()
            return None
    
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
        
        return [PortfolioAssetModel.from_orm(asset) for asset in assets]