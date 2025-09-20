"""
Base models for SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base, SCHEMA_NAME
from app.common.enums import AssetType, ImpactType
from datetime import datetime, timezone

# SQLAlchemy model for users
class User(Base):
    """
    SQLAlchemy model for users table
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    profile_picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime, nullable=True)

    portfolio_assets = relationship("PortfolioAsset")
    news = relationship("News")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login,
            "portfolio_assets": [asset.id for asset in self.portfolio_assets],
            "news": [news.id for news in self.news],
        }

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

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    image_url = Column(String, nullable=True)

    impact_prediction = Column(SQLAEnum(ImpactType), nullable=True)
    impact_prediction_justification = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship with categories
    categories = relationship("Category")
    
    # Relationship with NewsUrl
    news_urls = relationship("NewsUrl")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "user_id": self.user_id,
            "url": self.url,
            "image_url": self.image_url,
            "impact_prediction": self.impact_prediction,
            "impact_prediction_justification": self.impact_prediction_justification,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "categories": [cat.id for cat in self.categories],
            "news_urls": [nu.id for nu in self.news_urls],
        }


# Category model for the news categories
class Category(Base):
    """
    SQLAlchemy model for categories table
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "news_id": self.news_id,
        }

# SQLAlchemy model for portfolio assets
class PortfolioAsset(Base):
    """
    SQLAlchemy model for portfolio assets table
    """
    __tablename__ = "portfolio_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tag = Column(Integer, ForeignKey("tags.id"), nullable=False)
    logo = Column(String, nullable=True)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    asset_type = Column(SQLAEnum(AssetType), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tag": self.tag,
            "logo": self.logo,
            "symbol": self.symbol,
            "name": self.name,
            "asset_type": self.asset_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
# Tag model for portfolio asset tags
class Tag(Base):
    """
    SQLAlchemy model for tags table
    """
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    # Relationship with tags through association table
    assets = relationship("PortfolioAsset")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "assets": [asset.id for asset in self.assets],
        }

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
    news_urls = relationship("NewsUrl")

    def to_dict(self):
        return {
            "id": self.id,
            "codename": self.codename,
            "name": self.name,
            "website": self.website,
            "news_urls": [nu.id for nu in self.news_urls],
        }

class NewsUrl(Base):
    """
    SQLAlchemy model for news URLs linking sources to news articles
    """
    __tablename__ = "news_url"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey(f"sources.id"), nullable=False)
    news_id = Column(Integer, ForeignKey(f"news.id"), nullable=False)
    url = Column(String, nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "news_id": self.news_id,
            "url": self.url,
            "published_at": self.published_at,
        }