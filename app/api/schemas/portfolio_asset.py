"""
Pydantic schemas for Portfolio Assets API
"""
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
    Pydantic model for financial assets in a user's portfolio
    """
    id: Optional[int] = None
    user_id: int
    symbol: str  # Ticker symbol (e.g., AAPL, BTC, EUR/USD)
    name: str  # Full name (e.g., Apple Inc., Bitcoin, Euro/US Dollar)
    asset_type: AssetType
    tags: List[str] = Field(default_factory=list)
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
                "tags": ["tech", "consumer", "dividend"]
            }
        }

# Create model for creating new portfolio assets
class PortfolioAssetCreate(BaseModel):
    user_id: int
    symbol: str
    name: str
    asset_type: AssetType
    tags: List[str] = Field(default_factory=list)

# Update model for updating portfolio assets
class PortfolioAssetUpdate(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    
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