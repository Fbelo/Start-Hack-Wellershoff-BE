from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.db.models import portfolio_asset_tags

class AssetType(str, Enum):
    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITY = "commodity"
    OTHER = "other"

# SQLAlchemy model for database operations
class PortfolioAsset(Base):
    """
    SQLAlchemy model for portfolio assets table
    """
    __tablename__ = "portfolio_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    asset_type = Column(SQLAEnum(AssetType), nullable=False)
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    purchase_date = Column(DateTime, nullable=False)
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=True)
    asset_metadata = Column(JSONB, nullable=False, default={})  # Renamed from metadata to avoid conflict
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with user
    user = relationship("User", back_populates="portfolio_assets")
    
    # Relationship with tags through association table
    tags = relationship("Tag", secondary=portfolio_asset_tags, backref="portfolio_assets")

# User model relationship definition
from app.models.user import User
User.portfolio_assets = relationship("PortfolioAsset", back_populates="user")

# Tag model for portfolio asset tags
class Tag(Base):
    """
    SQLAlchemy model for tags table
    """
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

# Pydantic model for API requests/responses
class PortfolioAssetModel(BaseModel):
    """
    Pydantic model for financial assets in a user's portfolio
    """
    id: Optional[int] = None
    user_id: int
    symbol: str  # Ticker symbol (e.g., AAPL, BTC, EUR/USD)
    name: str  # Full name (e.g., Apple Inc., Bitcoin, Euro/US Dollar)
    asset_type: AssetType
    quantity: float
    purchase_price: float
    current_price: Optional[float] = None
    purchase_date: datetime
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    asset_metadata: Dict[str, str] = Field(default_factory=dict)  # Additional asset-specific data
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True  # Allows the model to be created from an ORM model
        schema_extra = {
            "example": {
                "user_id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "asset_type": "stock",
                "quantity": 10,
                "purchase_price": 150.75,
                "current_price": 175.50,
                "purchase_date": "2025-05-15T09:30:00Z",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "country": "USA",
                "tags": ["tech", "consumer", "dividend"]
            }
        }

# Create model for creating new portfolio assets
class PortfolioAssetCreate(BaseModel):
    user_id: int
    symbol: str
    name: str
    asset_type: AssetType
    quantity: float
    purchase_price: float
    current_price: Optional[float] = None
    purchase_date: datetime
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    asset_metadata: Dict[str, str] = Field(default_factory=dict)

# Update model for updating portfolio assets
class PortfolioAssetUpdate(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    asset_type: Optional[AssetType] = None
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None
    current_price: Optional[float] = None
    purchase_date: Optional[datetime] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    tags: Optional[List[str]] = None
    asset_metadata: Optional[Dict[str, str]] = None
    
class PortfolioAssetExtended(PortfolioAssetModel):
    """
    Extended Pydantic model with calculation methods
    """
    def calculate_current_value(self) -> float:
        """Calculate the current value of the asset"""
        if self.current_price is not None:
            return self.quantity * self.current_price
        return self.quantity * self.purchase_price
    
    def calculate_profit_loss(self) -> float:
        """Calculate the profit or loss of the asset"""
        if self.current_price is not None:
            return (self.current_price - self.purchase_price) * self.quantity
        return 0.0
    
    def calculate_profit_loss_percentage(self) -> float:
        """Calculate the profit or loss percentage of the asset"""
        if self.purchase_price > 0 and self.current_price is not None:
            return ((self.current_price - self.purchase_price) / self.purchase_price) * 100
        return 0.0