from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.models.schemas import JobSearchRequest, ScraperResponse, ErrorResponse
from app.services.scraper_service import ScraperService
from app.core.config import settings

router = APIRouter()


async def get_scraper_service() -> ScraperService:
    """Dependency to get scraper service instance"""
    return ScraperService()


@router.post("/scrape", response_model=ScraperResponse, summary="Scrape jobs from all platforms")
async def scrape_jobs(
    request: JobSearchRequest,
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """
    Scrape job listings from Indeed, Seek, and CareerOne based on job title and location.

    - **job_title**: Job title to search for (required)
    - **location**: Location to search in (optional, defaults to "Australia")
    - **max_results**: Maximum number of results to return (optional, defaults to 10, max 50)
    """
    try:
        result = await scraper_service.scrape_jobs(request)
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error_message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.post("/scrape/{platform}", response_model=ScraperResponse, summary="Scrape jobs from specific platform")
async def scrape_jobs_platform(
    platform: str,
    request: JobSearchRequest,
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """
    Scrape job listings from a specific platform.

    Supported platforms: indeed, seek, careerone

    - **platform**: Platform to scrape from (indeed, seek, careerone)
    - **job_title**: Job title to search for (required)
    - **location**: Location to search in (optional, defaults to "Australia")
    - **max_results**: Maximum number of results to return (optional, defaults to 10, max 50)
    """
    try:
        result = await scraper_service.scrape_from_platform(platform, request)
        if not result.success:
            raise HTTPException(status_code=400 if "not supported" in result.error_message else 500,
                              detail=result.error_message)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.get("/platforms", summary="Get available scraping platforms")
async def get_platforms():
    """Get list of available scraping platforms"""
    return {
        "platforms": ["indeed", "seek", "careerone"],
        "description": "Available job scraping platforms"
    }