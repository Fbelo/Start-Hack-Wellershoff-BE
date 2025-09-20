"""
Base models for SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base, SCHEMA_NAME
from app.api.schemas.portfolio_asset import AssetType
from enum import Enum


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

class ImpactType(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    UNSURE = "unsure"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

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
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime, nullable=True)

    portfolio_assets = relationship("PortfolioAsset", back_populates="user")

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

    url = Column(String, nullable=False, unique=True)
    image_url = Column(String, nullable=True)

    impact_prediction = Column(SQLAEnum(ImpactType), nullable=True)
    impact_prediction_justification = Column(String, nullable=True)


    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with categories through association table
    categories = relationship("Category", secondary=news_categories, backref="news_articles")
    
    # Relationship with NewsUrl
    news_urls = relationship("NewsUrl", back_populates="news_rel")
    
    # Relationship with sources through NewsUrl
    sources = relationship("Source", secondary="news_url", viewonly=True)

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
    logo = Column(String, nullable=True)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    asset_type = Column(SQLAEnum(AssetType), nullable=False)
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

class Source(Base):
    """
    SQLAlchemy model for news sources table
    """
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    codename = Column(String, nullable=False)
    name = Column(String, nullable=False)
    website = Column(String, nullable=False)
    
    # Relationship with NewsUrl
    news_urls = relationship("NewsUrl", back_populates="source_rel")

class NewsUrl(Base):
    """
    SQLAlchemy model for news URLs linking sources to news articles
    """
    __tablename__ = "news_url"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    url = Column(String, nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)
    
    # Relationships
    source_rel = relationship("Source", back_populates="news_urls")
    news_rel = relationship("News", back_populates="news_urls")
    
    # Ensure each URL is unique per source and news combination
    __table_args__ = (
        # Composite unique constraint for source_id and url
        # This ensures a source cannot have duplicate URLs
        # And URL can only belong to one source
        # Same for news_id and url
        # This ensures a URL can only belong to one news article
        {'unique_constraint': ['source_id', 'url'], 'unique_constraint': ['news_id', 'url']}
    )