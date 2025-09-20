"""
Shared enum types for the application
"""
from enum import Enum

class AssetType(str, Enum):
    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITY = "commodity"
    OTHER = "other"

class ImpactType(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    UNSURE = "unsure"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"