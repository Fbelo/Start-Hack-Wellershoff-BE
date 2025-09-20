"""
Base models for SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from app.db.database import Base

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