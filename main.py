from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

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

# Import and include routers
from app.routers import (
    example_router,
    news, 
    portfolio,
    prediction,
    user
)

# Include all routers
app.include_router(example_router.router)
app.include_router(news.router)
app.include_router(user.router)
app.include_router(portfolio.router)
app.include_router(prediction.router)

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