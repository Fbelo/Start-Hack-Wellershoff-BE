from typing import List, Optional, Dict
from datetime import datetime
from app.db.firebase import get_firestore_db, COLLECTION_PORTFOLIO_ASSETS
from app.models.portfolio_asset import PortfolioAssetModel, AssetType
from google.cloud.firestore_v1.base_query import FieldFilter
import uuid

class PortfolioAssetService:
    """
    Service for handling portfolio asset operations
    """
    
    @staticmethod
    def get_all_by_user(user_id: str) -> List[PortfolioAssetModel]:
        """
        Get all portfolio assets for a user
        """
        db = get_firestore_db()
        query = db.collection(COLLECTION_PORTFOLIO_ASSETS).where(
            filter=FieldFilter("user_id", "==", user_id)
        )
        
        asset_docs = query.stream()
        
        result = []
        for doc in asset_docs:
            asset_data = doc.to_dict()
            asset_data["id"] = doc.id
            result.append(PortfolioAssetModel(**asset_data))
            
        return result
    
    @staticmethod
    def get_by_id(asset_id: str) -> Optional[PortfolioAssetModel]:
        """
        Get a portfolio asset by ID
        """
        db = get_firestore_db()
        asset_doc = db.collection(COLLECTION_PORTFOLIO_ASSETS).document(asset_id).get()
        
        if not asset_doc.exists:
            return None
            
        asset_data = asset_doc.to_dict()
        asset_data["id"] = asset_doc.id
        return PortfolioAssetModel(**asset_data)
    
    @staticmethod
    def create(asset: PortfolioAssetModel) -> PortfolioAssetModel:
        """
        Create a new portfolio asset
        """
        db = get_firestore_db()
        
        # Generate ID if not provided
        if not asset.id:
            asset.id = str(uuid.uuid4())
            
        # Set timestamps
        asset.created_at = datetime.now()
        asset.updated_at = datetime.now()
        
        # Save to Firestore
        asset_ref = db.collection(COLLECTION_PORTFOLIO_ASSETS).document(asset.id)
        asset_ref.set(asset.to_dict())
        
        return asset
    
    @staticmethod
    def update(asset_id: str, updates: dict) -> Optional[PortfolioAssetModel]:
        """
        Update a portfolio asset
        """
        db = get_firestore_db()
        asset_ref = db.collection(COLLECTION_PORTFOLIO_ASSETS).document(asset_id)
        asset_doc = asset_ref.get()
        
        if not asset_doc.exists:
            return None
            
        # Get current data and update
        asset_data = asset_doc.to_dict()
        asset_data.update(updates)
        asset_data["updated_at"] = datetime.now()
        
        # Save to Firestore
        asset_ref.update(asset_data)
        
        # Return updated asset
        asset_data["id"] = asset_id
        return PortfolioAssetModel(**asset_data)
    
    @staticmethod
    def delete(asset_id: str) -> bool:
        """
        Delete a portfolio asset
        """
        db = get_firestore_db()
        asset_ref = db.collection(COLLECTION_PORTFOLIO_ASSETS).document(asset_id)
        asset_doc = asset_ref.get()
        
        if not asset_doc.exists:
            return False
            
        asset_ref.delete()
        return True
    
    @staticmethod
    def get_by_symbol(user_id: str, symbol: str) -> Optional[PortfolioAssetModel]:
        """
        Get a portfolio asset by symbol for a specific user
        """
        db = get_firestore_db()
        query = db.collection(COLLECTION_PORTFOLIO_ASSETS).where(
            filter=FieldFilter("user_id", "==", user_id)
        ).where(
            filter=FieldFilter("symbol", "==", symbol)
        ).limit(1)
        
        assets = list(query.stream())
        if not assets:
            return None
            
        asset_doc = assets[0]
        asset_data = asset_doc.to_dict()
        asset_data["id"] = asset_doc.id
        return PortfolioAssetModel(**asset_data)
    
    @staticmethod
    def get_by_type(user_id: str, asset_type: AssetType) -> List[PortfolioAssetModel]:
        """
        Get portfolio assets by type for a specific user
        """
        db = get_firestore_db()
        query = db.collection(COLLECTION_PORTFOLIO_ASSETS).where(
            filter=FieldFilter("user_id", "==", user_id)
        ).where(
            filter=FieldFilter("asset_type", "==", asset_type)
        )
        
        asset_docs = query.stream()
        
        result = []
        for doc in asset_docs:
            asset_data = doc.to_dict()
            asset_data["id"] = doc.id
            result.append(PortfolioAssetModel(**asset_data))
            
        return result
    
    @staticmethod
    def create_demo_portfolio(user_id: str) -> List[PortfolioAssetModel]:
        """
        Create a demo portfolio for a user
        """
        demo_assets = [
            PortfolioAssetModel(
                user_id=user_id,
                symbol="AAPL",
                name="Apple Inc.",
                asset_type=AssetType.STOCK,
                quantity=10,
                purchase_price=150.75,
                current_price=175.50,
                purchase_date=datetime(2025, 5, 15),
                sector="Technology",
                industry="Consumer Electronics",
                country="USA",
                tags=["tech", "consumer", "dividend"]
            ),
            PortfolioAssetModel(
                user_id=user_id,
                symbol="MSFT",
                name="Microsoft Corporation",
                asset_type=AssetType.STOCK,
                quantity=5,
                purchase_price=300.25,
                current_price=325.10,
                purchase_date=datetime(2025, 6, 10),
                sector="Technology",
                industry="Software",
                country="USA",
                tags=["tech", "software", "cloud"]
            ),
            PortfolioAssetModel(
                user_id=user_id,
                symbol="AMZN",
                name="Amazon.com, Inc.",
                asset_type=AssetType.STOCK,
                quantity=3,
                purchase_price=3100.50,
                current_price=3250.75,
                purchase_date=datetime(2025, 4, 20),
                sector="Consumer Cyclical",
                industry="Internet Retail",
                country="USA",
                tags=["tech", "retail", "cloud"]
            ),
            PortfolioAssetModel(
                user_id=user_id,
                symbol="BTC",
                name="Bitcoin",
                asset_type=AssetType.CRYPTO,
                quantity=0.5,
                purchase_price=40000.00,
                current_price=45000.00,
                purchase_date=datetime(2025, 3, 5),
                sector=None,
                industry=None,
                country=None,
                tags=["crypto", "digital asset"]
            ),
            PortfolioAssetModel(
                user_id=user_id,
                symbol="VTI",
                name="Vanguard Total Stock Market ETF",
                asset_type=AssetType.ETF,
                quantity=15,
                purchase_price=200.00,
                current_price=210.50,
                purchase_date=datetime(2025, 1, 15),
                sector="N/A",
                industry="Fund",
                country="USA",
                tags=["etf", "index", "diversified"]
            )
        ]
        
        created_assets = []
        for asset in demo_assets:
            created_assets.append(PortfolioAssetService.create(asset))
            
        return created_assets