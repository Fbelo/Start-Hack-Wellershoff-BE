"""
Controllers for Source API
"""
from fastapi import HTTPException, APIRouter, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import Source, NewsUrl
from app.api.schemas.source import SourceModel, SourceCreate, SourceUpdate
from app.db.database import get_db

# Create source router
source_router = APIRouter(
    prefix="/api/v1/sources",
    tags=["sources"],
    responses={404: {"description": "Not found"}},
)

class SourceController:
    """
    Controller for handling source operations
    """
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[SourceModel]:
        """
        Get all news sources with pagination
        """
        sources = db.query(Source).offset(skip).limit(limit).all()
        return [SourceModel.model_validate(source) for source in sources]
    
    @staticmethod
    def get_by_id(db: Session, source_id: int) -> Optional[SourceModel]:
        """
        Get a news source by ID
        """
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source:
            return None
        return SourceModel.model_validate(source)
    
    @staticmethod
    def get_by_codename(db: Session, codename: str) -> Optional[SourceModel]:
        """
        Get a news source by codename
        """
        source = db.query(Source).filter(Source.codename == codename).first()
        if not source:
            return None
        return SourceModel.model_validate(source)
    
    @staticmethod
    def create(db: Session, source_data: SourceCreate) -> SourceModel:
        """
        Create a new news source
        """
        try:
            # Check if source with codename already exists
            existing_source = db.query(Source).filter(Source.codename == source_data.codename).first()
            if existing_source:
                raise HTTPException(status_code=400, detail=f"Source with codename '{source_data.codename}' already exists")
            
            # Create new source
            db_source = Source(
                codename=source_data.codename,
                name=source_data.name,
                website=source_data.website
            )
            db.add(db_source)
            db.commit()
            db.refresh(db_source)
            return SourceModel.model_validate(db_source)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Invalid source data")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    @staticmethod
    def update(db: Session, source_id: int, source_data: SourceUpdate) -> SourceModel:
        """
        Update an existing news source
        """
        # Get existing source
        db_source = db.query(Source).filter(Source.id == source_id).first()
        if not db_source:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
        
        try:
            # Update fields if provided
            if source_data.codename is not None:
                db_source.codename = source_data.codename
            if source_data.name is not None:
                db_source.name = source_data.name
            if source_data.website is not None:
                db_source.website = source_data.website
            
            db.commit()
            db.refresh(db_source)
            return SourceModel.model_validate(db_source)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Invalid source data")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    @staticmethod
    def delete(db: Session, source_id: int) -> bool:
        """
        Delete a news source by ID
        """
        # Get existing source
        db_source = db.query(Source).filter(Source.id == source_id).first()
        if not db_source:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
        
        try:
            # Check if source is referenced by any news URLs
            news_urls = db.query(NewsUrl).filter(NewsUrl.source_id == source_id).first()
            if news_urls:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot delete source: it is referenced by existing news articles"
                )
            
            # Delete the source
            db.delete(db_source)
            db.commit()
            return True
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# API Routes
@source_router.get("/", response_model=List[SourceModel])
def get_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all news sources with pagination
    """
    return SourceController.get_all(db, skip=skip, limit=limit)

@source_router.get("/{source_id}", response_model=SourceModel)
def get_source(source_id: int, db: Session = Depends(get_db)):
    """
    Get a source by ID
    """
    source = SourceController.get_by_id(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
    return source

@source_router.get("/codename/{codename}", response_model=SourceModel)
def get_source_by_codename(codename: str, db: Session = Depends(get_db)):
    """
    Get a source by codename
    """
    source = SourceController.get_by_codename(db, codename)
    if not source:
        raise HTTPException(status_code=404, detail=f"Source with codename '{codename}' not found")
    return source

@source_router.post("/", response_model=SourceModel)
def create_source(source_data: SourceCreate, db: Session = Depends(get_db)):
    """
    Create a new news source
    """
    return SourceController.create(db, source_data)

@source_router.put("/{source_id}", response_model=SourceModel)
def update_source(source_id: int, source_data: SourceUpdate, db: Session = Depends(get_db)):
    """
    Update an existing news source
    """
    return SourceController.update(db, source_id, source_data)

@source_router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    """
    Delete a news source by ID
    """
    success = SourceController.delete(db, source_id)
    if success:
        return {"message": f"Source with ID {source_id} has been deleted"}
    return {"message": f"Failed to delete source with ID {source_id}"}