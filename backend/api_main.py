"""
Job Scraper API
FastAPI application for scraping jobs from Indeed, Seek, and CareerOne
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json
import os
import glob
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import scrapers
from indeed_scraper_by_title import IndeedJobTitleScraper
from seek_scraper_by_title import SeekJobTitleScraper
from career_scraper_by_title import CareerOneJobTitleScraper

# Create thread pool executor for running sync scrapers
executor = ThreadPoolExecutor(max_workers=3)

# Create FastAPI app
app = FastAPI(
    title="Job Scraper API",
    description="API for scraping job listings from Indeed, Seek, and CareerOne with ANZSCO 482 validation",
    version="1.0.0"
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
    max_workers: Optional[int] = Field(3, ge=1, le=10, description="Number of parallel workers (1-10)")
    max_pages: Optional[int] = Field(2, ge=1, le=5, description="Maximum pages to scrape per job title")

    class Config:
        json_schema_extra = {
            "example": {
                "job_titles": ["Software Engineer", "Data Scientist"],
                "location": "Sydney NSW",
                "max_workers": 3,
                "max_pages": 2
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


# Helper function to save with timestamp
def save_with_timestamp(jobs, base_filename, validated=False):
    """Save jobs to JSON file with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "_validated" if validated else "_scraped"
    filename = f"{base_filename}_{timestamp}{suffix}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    
    return filename


# Helper function to get latest file
def get_latest_file(platform, validated=True):
    """Get the latest JSON file for a platform"""
    suffix = "_validated" if validated else "_scraped"
    pattern = f"{platform}_jobs_*{suffix}.json"
    
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
        "version": "1.0.0",
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
        pattern = f"{platform}_jobs_*_validated.json"
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
                "filename": file,
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
    
    # Check if file exists
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Read the file
        with open(filename, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        
        # Get file modification time
        file_time = datetime.fromtimestamp(os.path.getmtime(filename))
        
        return {
            "platform": platform,
            "jobs": jobs,
            "timestamp": file_time.isoformat(),
            "total_jobs": len(jobs),
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


# Indeed API
@app.post("/api/scrape/indeed", response_model=ScrapeResponse)
async def scrape_indeed(request: ScrapeRequest):
    """
    Scrape jobs from Indeed.com.au
    
    - **job_titles**: List of job titles to search (1-10 titles)
    - **location**: Location (e.g., "Sydney NSW", "Melbourne VIC", "Brisbane QLD")
    - **max_workers**: Number of parallel workers (default: 3)
    - **max_pages**: Maximum pages per title (default: 2)
    
    Returns both scraped and validated JSON files with timestamps.
    """
    def run_scraper():
        try:
            print(f"\n{'='*60}")
            print(f"Indeed API Request")
            print(f"Job Titles: {', '.join(request.job_titles)}")
            print(f"Location: {request.location}")
            print(f"{'='*60}")
            
            # Initialize scraper
            scraper = IndeedJobTitleScraper(max_workers=request.max_workers)
            
            # Scrape jobs
            jobs = scraper.scrape_multiple_titles(request.job_titles, request.location, max_pages=request.max_pages)
            
            if not jobs:
                return {
                    "success": False,
                    "platform": "indeed",
                    "total_jobs": 0,
                    "scraped_file": "",
                    "validated_file": "",
                    "timestamp": datetime.now().isoformat(),
                    "message": "No jobs found"
                }
            
            # Save scraped jobs with timestamp
            scraped_file = save_with_timestamp(jobs, "indeed_jobs", validated=False)
            
            # Validate against ANZSCO 482
            validated_jobs = scraper.validate_jobs_with_anzsco(jobs)
            
            # Save validated jobs with timestamp
            validated_file = save_with_timestamp(validated_jobs, "indeed_jobs", validated=True)
            
            return {
                "success": True,
                "platform": "indeed",
                "total_jobs": len(jobs),
                "scraped_file": scraped_file,
                "validated_file": validated_file,
                "timestamp": datetime.now().isoformat(),
                "message": f"Successfully scraped {len(jobs)} jobs from Indeed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "platform": "indeed",
                "total_jobs": 0,
                "scraped_file": "",
                "validated_file": "",
                "timestamp": datetime.now().isoformat(),
                "message": f"Indeed scraping failed: {str(e)}"
            }
    
    # Run scraper in thread pool to avoid asyncio conflict
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_scraper)
    
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
    - **max_workers**: Number of parallel workers (default: 3)
    - **max_pages**: Maximum pages per title (default: 2)
    
    Returns both scraped and validated JSON files with timestamps.
    """
    def run_scraper():
        try:
            print(f"\n{'='*60}")
            print(f"Seek API Request")
            print(f"Job Titles: {', '.join(request.job_titles)}")
            print(f"Location: {request.location}")
            print(f"{'='*60}")
            
            # Initialize scraper
            scraper = SeekJobTitleScraper(max_workers=request.max_workers)
            
            # Scrape jobs
            jobs = scraper.scrape_multiple_titles(request.job_titles, request.location, max_pages=request.max_pages)
            
            if not jobs:
                return {
                    "success": False,
                    "platform": "seek",
                    "total_jobs": 0,
                    "scraped_file": "",
                    "validated_file": "",
                    "timestamp": datetime.now().isoformat(),
                    "message": "No jobs found"
                }
            
            # Save scraped jobs with timestamp
            scraped_file = save_with_timestamp(jobs, "seek_jobs", validated=False)
            
            # Validate against ANZSCO 482
            validated_jobs = scraper.validate_jobs_with_anzsco(jobs)
            
            # Save validated jobs with timestamp
            validated_file = save_with_timestamp(validated_jobs, "seek_jobs", validated=True)
            
            return {
                "success": True,
                "platform": "seek",
                "total_jobs": len(jobs),
                "scraped_file": scraped_file,
                "validated_file": validated_file,
                "timestamp": datetime.now().isoformat(),
                "message": f"Successfully scraped {len(jobs)} jobs from Seek"
            }
            
        except Exception as e:
            return {
                "success": False,
                "platform": "seek",
                "total_jobs": 0,
                "scraped_file": "",
                "validated_file": "",
                "timestamp": datetime.now().isoformat(),
                "message": f"Seek scraping failed: {str(e)}"
            }
    
    # Run scraper in thread pool to avoid asyncio conflict
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_scraper)
    
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
    - **max_workers**: Number of parallel workers (default: 3)
    - **max_pages**: Maximum pages per title (default: 2)
    
    Returns both scraped and validated JSON files with timestamps.
    """
    def run_scraper():
        try:
            print(f"\n{'='*60}")
            print(f"CareerOne API Request")
            print(f"Job Titles: {', '.join(request.job_titles)}")
            print(f"Location: {request.location}")
            print(f"{'='*60}")
            
            # Initialize scraper
            scraper = CareerOneJobTitleScraper(max_workers=request.max_workers)
            
            # Scrape jobs
            jobs = scraper.scrape_multiple_titles(request.job_titles, request.location, max_pages=request.max_pages)
            
            if not jobs:
                return {
                    "success": False,
                    "platform": "careerone",
                    "total_jobs": 0,
                    "scraped_file": "",
                    "validated_file": "",
                    "timestamp": datetime.now().isoformat(),
                    "message": "No jobs found"
                }
            
            # Save scraped jobs with timestamp
            scraped_file = save_with_timestamp(jobs, "careerone_jobs", validated=False)
            
            # Validate against ANZSCO 482
            validated_jobs = scraper.validate_jobs_with_anzsco(jobs)
            
            # Save validated jobs with timestamp
            validated_file = save_with_timestamp(validated_jobs, "careerone_jobs", validated=True)
            
            return {
                "success": True,
                "platform": "careerone",
                "total_jobs": len(jobs),
                "scraped_file": scraped_file,
                "validated_file": validated_file,
                "timestamp": datetime.now().isoformat(),
                "message": f"Successfully scraped {len(jobs)} jobs from CareerOne"
            }
            
        except Exception as e:
            return {
                "success": False,
                "platform": "careerone",
                "total_jobs": 0,
                "scraped_file": "",
                "validated_file": "",
                "timestamp": datetime.now().isoformat(),
                "message": f"CareerOne scraping failed: {str(e)}"
            }
    
    # Run scraper in thread pool to avoid asyncio conflict
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_scraper)
    
    if not result["success"] and "failed" in result["message"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
