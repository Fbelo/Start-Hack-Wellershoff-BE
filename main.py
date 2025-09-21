from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
import os

from app.db.database import engine, Base, create_schema_if_not_exists
from app.common.security import verify_api_key

# Create schema if it doesn't exist
create_schema_if_not_exists()

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wellershoff & Partners API",
    description="Backend API for Wellershoff & Partners application",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API key middleware
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    await verify_api_key(request)
    response = await call_next(request)
    return response

# Import and include router
from app.api import get_router
router = get_router()

# Include the main router
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to Wellershoff & Partners API"}

# Import news scraper scheduler
from app.scrapers.scheduler import start_scheduler
from app.watsonx import watson_service

# Start background tasks
@app.on_event("startup")
async def startup_event():
    # Check for required WatsonX environment variables
    required_vars = ["WATSON_URL", "WATSON_API_KEY", "WATSON_PROJECT_ID"]
    missing_vars = [var for var in required_vars if os.getenv(var) is None]
    
    if missing_vars:
        logging.warning(f"Missing required WatsonX environment variables: {', '.join(missing_vars)}")
        logging.warning("WatsonX integration will not function correctly without these variables")
    
    # Start the news scraper scheduler in a background task
    asyncio.create_task(start_scheduler())
    logging.info("Started news scraper scheduler")
    
    # Start the Watson service in a background task
    asyncio.create_task(watson_service.start())
    logging.info("Started Watson service")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)