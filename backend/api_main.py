"""
Job Scraper API
FastAPI application for scraping jobs from Indeed, Seek, and CareerOne
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json
import os
import glob

# Import scrapers
from indeed_scraper_by_title import IndeedJobTitleScraper
from seek_scraper_by_title import SeekJobTitleScraper
from career_scraper_by_title import CareerOneJobTitleScraper

# Import company and HubSpot modules
from company_scraper import extract_companies_from_jobs, enrich_companies_with_details
from hubspot_integration import HubSpotIntegration

# Directory where scraped JSON files are stored
# Can be overridden via DATA_DIR env var (useful in Docker)
DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(DATA_DIR, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="Job Scraper API",
    description="API for scraping job listings from Indeed, Seek, and CareerOne with ANZSCO 482 validation",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ScrapeRequest(BaseModel):
    """Request model for job scraping"""
    job_titles: List[str] = Field(..., min_items=1, max_items=10, description="List of job titles to search")
    location: str = Field(..., min_length=1, description="Location to search (e.g., 'Sydney NSW', 'Melbourne VIC')")
    max_pages: Optional[int] = Field(3, ge=1, le=5, description="Maximum pages to scrape per job title")

    class Config:
        json_schema_extra = {
            "example": {
                "job_titles": ["Software Engineer", "Data Scientist"],
                "location": "Sydney NSW",
                "max_pages": 3
            }
        }


class ScrapeResponse(BaseModel):
    """Response model for job scraping"""
    success: bool
    platform: str
    total_jobs: int
    scraped_file: str
    validated_file: str
    timestamp: str
    message: str
    companies_synced: Optional[dict] = None  # HubSpot sync statistics


# Helper function to save with timestamp
def save_with_timestamp(jobs, base_filename, validated=False):
    """Save jobs to JSON file with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "_validated" if validated else "_scraped"
    filename = f"{base_filename}_{timestamp}{suffix}.json"
    filepath = os.path.join(DATA_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    return filepath


# Helper function to get latest file
def get_latest_file(platform, validated=True):
    """Get the latest JSON file for a platform"""
    suffix = "_validated" if validated else "_scraped"
    pattern = os.path.join(DATA_DIR, f"{platform}_jobs_*{suffix}.json")

    # Get all matching files
    files = glob.glob(pattern)

    if not files:
        return None

    # Sort by modification time (newest first)
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Job Scraper API",
        "version": "2.0.0",
        "platforms": ["indeed", "seek", "careerone"],
        "docs": "/docs",
        "endpoints": {
            "indeed": "/api/scrape/indeed",
            "seek": "/api/scrape/seek",
            "careerone": "/api/scrape/careerone",
            "latest": "/api/latest/{platform}"
        }
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Get latest data endpoint
@app.get("/api/latest/{platform}")
async def get_latest_data(platform: str):
    """
    Get the latest scraped and validated data for a platform

    - **platform**: Platform name (indeed, seek, or careerone)

    Returns the latest validated JSON data with timestamp.
    """
    if platform not in ["indeed", "seek", "careerone"]:
        raise HTTPException(status_code=400, detail="Invalid platform. Must be 'indeed', 'seek', or 'careerone'")

    # Get latest validated file
    latest_file = get_latest_file(platform, validated=True)

    if not latest_file:
        return {
            "platform": platform,
            "jobs": [],
            "timestamp": None,
            "message": "No data available"
        }

    try:
        # Read the file
        with open(latest_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)

        # Get file modification time
        file_time = datetime.fromtimestamp(os.path.getmtime(latest_file))

        return {
            "platform": platform,
            "jobs": jobs,
            "timestamp": file_time.isoformat(),
            "total_jobs": len(jobs),
            "filename": latest_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading data: {str(e)}")


# Get list of available files for a platform
@app.get("/api/files/{platform}")
async def get_available_files(platform: str):
    """
    Get list of all available validated data files for a platform

    - **platform**: Platform name (indeed, seek, or careerone)

    Returns list of files with timestamps.
    """
    if platform not in ["indeed", "seek", "careerone"]:
        raise HTTPException(status_code=400, detail="Invalid platform. Must be 'indeed', 'seek', or 'careerone'")

    try:
        # Get all validated files for this platform
        pattern = os.path.join(DATA_DIR, f"{platform}_jobs_*_validated.json")
        files = glob.glob(pattern)

        # Sort by modification time (newest first)
        files.sort(key=os.path.getmtime, reverse=True)

        # Create file info list
        file_list = []
        for file in files:
            file_time = datetime.fromtimestamp(os.path.getmtime(file))
            # Extract timestamp from filename (e.g., indeed_jobs_20260129_114555_validated.json)
            parts = file.split('_')
            if len(parts) >= 4:
                date_str = parts[2]  # 20260129
                time_str = parts[3]  # 114555
                display_name = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
            else:
                display_name = file_time.strftime("%Y-%m-%d %H:%M:%S")

            file_list.append({
                "filename": os.path.basename(file),
                "display_name": display_name,
                "timestamp": file_time.isoformat()
            })

        return {
            "platform": platform,
            "files": file_list,
            "total": len(file_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


# Get specific file data
@app.get("/api/file/{platform}/{filename}")
async def get_file_data(platform: str, filename: str):
    """
    Get data from a specific file

    - **platform**: Platform name (indeed, seek, or careerone)
    - **filename**: The filename to read

    Returns the JSON data from the specified file.
    """
    if platform not in ["indeed", "seek", "careerone"]:
        raise HTTPException(status_code=400, detail="Invalid platform. Must be 'indeed', 'seek', or 'careerone'")

    # Security: validate filename format
    if not filename.startswith(f"{platform}_jobs_") or not filename.endswith("_validated.json"):
        raise HTTPException(status_code=400, detail="Invalid filename format")

    filepath = os.path.join(DATA_DIR, filename)

    # Check if file exists
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            jobs = json.load(f)

        # Get file modification time
        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))

        return {
            "platform": platform,
            "jobs": jobs,
            "timestamp": file_time.isoformat(),
            "total_jobs": len(jobs),
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


def _run_scrape(platform, scraper_cls, request):
    """Shared scrape logic for all platforms."""
    try:
        print(f"\n{'='*60}")
        print(f"{platform.title()} API Request")
        print(f"Job Titles: {', '.join(request.job_titles)}")
        print(f"Location: {request.location}")
        print(f"{'='*60}")

        scraper = scraper_cls()
        jobs = scraper.scrape_multiple_titles(
            request.job_titles, request.location, max_pages=request.max_pages
        )

        if not jobs:
            return {
                "success": False,
                "platform": platform,
                "total_jobs": 0,
                "scraped_file": "",
                "validated_file": "",
                "timestamp": datetime.now().isoformat(),
                "message": "No jobs found",
                "companies_synced": None,
            }

        scraped_file = save_with_timestamp(jobs, f"{platform}_jobs", validated=False)
        validated_jobs = scraper.validate_jobs_with_anzsco(jobs)
        validated_file = save_with_timestamp(validated_jobs, f"{platform}_jobs", validated=True)

        # Company enrichment + HubSpot
        print(f"\n{'='*60}")
        print(f"Processing Company Information")
        print(f"{'='*60}")

        companies = extract_companies_from_jobs(validated_jobs, source=platform)
        print(f"Found {len(companies)} unique companies")
        enriched_companies = enrich_companies_with_details(companies, max_companies=10)

        hubspot = HubSpotIntegration()
        if hubspot.is_enabled():
            company_sync_stats = hubspot.batch_sync_companies(enriched_companies)
        else:
            print("\nHubSpot integration not enabled (missing API key)")
            company_sync_stats = {
                "total": len(enriched_companies),
                "created": 0,
                "updated": 0,
                "exists": 0,
                "skipped": len(enriched_companies),
                "failed": 0,
                "enabled": False,
            }

        return {
            "success": True,
            "platform": platform,
            "total_jobs": len(jobs),
            "scraped_file": scraped_file,
            "validated_file": validated_file,
            "timestamp": datetime.now().isoformat(),
            "message": f"Successfully scraped {len(jobs)} jobs from {platform.title()}",
            "companies_synced": company_sync_stats,
        }

    except Exception as e:
        return {
            "success": False,
            "platform": platform,
            "total_jobs": 0,
            "scraped_file": "",
            "validated_file": "",
            "timestamp": datetime.now().isoformat(),
            "message": f"{platform.title()} scraping failed: {str(e)}",
            "companies_synced": None,
        }


# Indeed API
@app.post("/api/scrape/indeed", response_model=ScrapeResponse)
async def scrape_indeed(request: ScrapeRequest):
    """
    Scrape jobs from Indeed.com.au

    - **job_titles**: List of job titles to search (1-10 titles)
    - **location**: Location (e.g., "Sydney NSW", "Melbourne VIC", "Brisbane QLD")
    - **max_pages**: Maximum pages per title (default: 3)

    Returns both scraped and validated JSON files with timestamps.
    """
    result = _run_scrape("indeed", IndeedJobTitleScraper, request)
    if not result["success"] and "failed" in result["message"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


# Seek API
@app.post("/api/scrape/seek", response_model=ScrapeResponse)
async def scrape_seek(request: ScrapeRequest):
    """
    Scrape jobs from Seek.com.au

    - **job_titles**: List of job titles to search (1-10 titles)
    - **location**: Location with hyphen (e.g., "Sydney-NSW", "Melbourne-VIC")
    - **max_pages**: Maximum pages per title (default: 3)

    Returns both scraped and validated JSON files with timestamps.
    """
    result = _run_scrape("seek", SeekJobTitleScraper, request)
    if not result["success"] and "failed" in result["message"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


# CareerOne API
@app.post("/api/scrape/careerone", response_model=ScrapeResponse)
async def scrape_careerone(request: ScrapeRequest):
    """
    Scrape jobs from CareerOne.com.au

    - **job_titles**: List of job titles to search (1-10 titles)
    - **location**: Location (e.g., "Sydney", "Melbourne", "Brisbane")
    - **max_pages**: Maximum pages per title (default: 3)

    Returns both scraped and validated JSON files with timestamps.
    Also extracts company information and syncs to HubSpot.
    """
    result = _run_scrape("careerone", CareerOneJobTitleScraper, request)
    if not result["success"] and "failed" in result["message"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_main:app", host="0.0.0.0", port=3001, reload=True)

# Serve React static files — must be mounted AFTER all API routes
_static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
if os.path.exists(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
