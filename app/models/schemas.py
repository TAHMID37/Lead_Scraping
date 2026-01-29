from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class JobSearchRequest(BaseModel):
    """Request model for job search"""
    job_title: str = Field(..., min_length=1, max_length=100, description="Job title to search for")
    location: Optional[str] = Field("Australia", description="Location to search in")
    max_results: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results to return")


class JobResponse(BaseModel):
    """Response model for individual job"""
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: Optional[str] = None
    salary: Optional[str] = None
    source: str  # 'indeed', 'seek', 'careerone'


class ScraperResponse(BaseModel):
    """Response model for scraper results"""
    success: bool
    jobs: List[JobResponse]
    total_found: int
    search_title: str
    search_location: str
    scraped_at: datetime
    error_message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None