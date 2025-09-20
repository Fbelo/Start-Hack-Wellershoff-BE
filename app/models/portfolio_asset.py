from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class AssetType(str, Enum):
    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITY = "commodity"
    OTHER = "other"

class PortfolioAssetModel(BaseModel):
    """
    Model for financial assets in a user's portfolio
    """
    id: Optional[str] = None
    user_id: str
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
    metadata: Dict[str, str] = Field(default_factory=dict)  # Additional asset-specific data
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
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
    
    def to_dict(self):
        """Convert to dictionary for Firestore"""
        return {
            "user_id": self.user_id,
            "symbol": self.symbol,
            "name": self.name,
            "asset_type": self.asset_type,
            "quantity": self.quantity,
            "purchase_price": self.purchase_price,
            "current_price": self.current_price,
            "purchase_date": self.purchase_date,
            "sector": self.sector,
            "industry": self.industry,
            "country": self.country,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
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