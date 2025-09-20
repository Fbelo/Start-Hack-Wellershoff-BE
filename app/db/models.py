"""
Base models for SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table, Text, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from datetime import datetime
from app.db.database import Base, SCHEMA_NAME
from app.api.schemas.news import ImpactType
from app.api.schemas.portfolio_asset import AssetType

# Association table for many-to-many relationships
news_categories = Table(
    'news_categories',
    Base.metadata,
    Column('news_id', Integer, ForeignKey('news.id')),
    Column('category_name', String)
)

portfolio_asset_tags = Table(
    'portfolio_asset_tags',
    Base.metadata,
    Column('portfolio_asset_id', Integer, ForeignKey('portfolio_assets.id')),
    Column('tag_name', String)
)

# SQLAlchemy model for users
class User(Base):
    """
    SQLAlchemy model for users table
    """
    __tablename__ = "users"
    __table_args__ = {'schema': SCHEMA_NAME}  # Explicitly set the schema
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    profile_picture = Column(String, nullable=True)
    preferences = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime, nullable=True)

# SQLAlchemy model for news
class News(Base):
    """
    SQLAlchemy model for news table
    """
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String, nullable=True)
    source = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)
    image_url = Column(String, nullable=True)
    impact_prediction = Column(SQLAEnum(ImpactType), default=ImpactType.UNKNOWN)
    impact_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with categories through association table
    categories = relationship("Category", secondary=news_categories, backref="news_articles")

# Category model for the news categories
class Category(Base):
    """
    SQLAlchemy model for categories table
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

# SQLAlchemy model for portfolio assets
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

# Tag model for portfolio asset tags
class Tag(Base):
    """
    SQLAlchemy model for tags table
    """
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

# Set up the relationships
User.portfolio_assets = relationship("PortfolioAsset", back_populates="user")