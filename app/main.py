from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.jobs import router as jobs_router

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=settings.description,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    jobs_router,
    prefix="/api/v1/jobs",
    tags=["jobs"]
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Job Scraper API",
        "version": settings.version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )