from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

from app.db.database import engine, Base, create_schema_if_not_exists

# Create schema if it doesn't exist
create_schema_if_not_exists()

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wellershoff API",
    description="Backend API for Wellershoff application",
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

# Import and include router
from app.api.router import router

# Include the main router
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to Wellershoff API"}

# Import news scraper scheduler
from app.scrapers.scheduler import start_scheduler

# Start background tasks
@app.on_event("startup")
async def startup_event():
    # Start the news scraper scheduler in a background task
    asyncio.create_task(start_scheduler())
    logging.info("Started news scraper scheduler")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)