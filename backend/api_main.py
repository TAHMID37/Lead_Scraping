"""
Job Scraper API
FastAPI application for scraping jobs from Indeed, Seek, and CareerOne
"""

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
import json
import os
import glob
import threading

# Import scrapers
from indeed_scraper_by_title import IndeedJobTitleScraper
from seek_scraper_by_title import SeekJobTitleScraper
from career_scraper_by_title import CareerOneJobTitleScraper

# Import company and HubSpot modules
from company_scraper import extract_companies_from_jobs, enrich_companies_with_details
from hubspot_integration import HubSpotIntegration

# Import DB
from db.database import get_db, engine, Base
from db.models import ScrapeSession, Job, AnzscoAssessment, Company, SessionCompany

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
    allow_headers=["*", "X-Spider-Api-Key", "X-Gemini-Api-Key", "X-Hubspot-Api-Key"],
)


# API key extraction
class ApiKeys:
    def __init__(self, spider_api_key: str, gemini_api_key: str = "", hubspot_api_key: str = ""):
        self.spider_api_key = spider_api_key
        self.gemini_api_key = gemini_api_key
        self.hubspot_api_key = hubspot_api_key


def get_api_keys(
    x_spider_api_key: str = Header("", alias="X-Spider-Api-Key"),
    x_gemini_api_key: str = Header("", alias="X-Gemini-Api-Key"),
    x_hubspot_api_key: str = Header("", alias="X-Hubspot-Api-Key"),
) -> ApiKeys:
    return ApiKeys(x_spider_api_key, x_gemini_api_key, x_hubspot_api_key)


# Startup event to create tables
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


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
    session_id: Optional[str] = None  # DB session ID


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


# ------------------------------------------------------------------
# Serialization helpers
# ------------------------------------------------------------------

def _session_to_dict(s, include_jobs=False):
    d = {
        "id": str(s.id),
        "platform": s.platform,
        "job_titles": s.job_titles,
        "location": s.location,
        "max_pages": s.max_pages,
        "status": s.status,
        "total_jobs": s.total_jobs,
        "eligible_jobs": s.eligible_jobs,
        "error_message": s.error_message,
        "started_at": s.started_at.isoformat() if s.started_at else None,
        "completed_at": s.completed_at.isoformat() if s.completed_at else None,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }
    if include_jobs:
        d["jobs"] = [_job_to_dict(j) for j in s.jobs]
    return d


def _job_to_dict(j):
    d = {
        "id": str(j.id),
        "session_id": str(j.session_id),
        "platform": j.platform,
        "job_title": j.job_title,
        "employer_name": j.employer_name,
        "location": j.location,
        "job_description": j.job_description,
        "salary": j.salary,
        "posted_date": j.posted_date,
        "url": j.url,
        "search_title": j.search_title,
        "search_location": j.search_location,
        "scraped_at": j.scraped_at.isoformat() if j.scraped_at else None,
        "created_at": j.created_at.isoformat() if j.created_at else None,
    }
    if j.assessment:
        d["anzsco_assessment"] = {
            "id": str(j.assessment.id),
            "eligible": j.assessment.eligible,
            "occupation": j.assessment.occupation,
            "anzsco_code": j.assessment.anzsco_code,
            "confidence_score": j.assessment.confidence_score,
            "reason": j.assessment.reason,
            "assessed_at": j.assessment.assessed_at.isoformat() if j.assessment.assessed_at else None,
        }
    return d


def _company_to_dict(c):
    return {
        "id": str(c.id),
        "name": c.name,
        "description": c.description,
        "website": c.website,
        "industry": c.industry,
        "source": c.source,
        "source_url": c.source_url,
        "anzsco_eligible": c.anzsco_eligible,
        "job_count": c.job_count,
        "hubspot_id": c.hubspot_id,
        "hubspot_status": c.hubspot_status,
        "hubspot_synced_at": c.hubspot_synced_at.isoformat() if c.hubspot_synced_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


# ------------------------------------------------------------------
# Existing endpoints (unchanged)
# ------------------------------------------------------------------

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
            "latest": "/api/latest/{platform}",
            "sessions": "/api/sessions",
            "stats": "/api/stats",
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


# ------------------------------------------------------------------
# Scrape logic
# ------------------------------------------------------------------

def _create_session(platform, request, db: DBSession) -> str:
    """Create a DB session and return its ID. The actual scrape runs in background."""
    session = ScrapeSession(
        platform=platform,
        job_titles=request.job_titles,
        location=request.location,
        max_pages=request.max_pages,
        status="scraping",
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return str(session.id)


def _run_scrape_background(platform, scraper_cls, job_titles, location, max_pages, api_keys_dict, session_id):
    """Run scrape in a background thread with its own DB session."""
    from db.database import SessionLocal
    db = SessionLocal()
    try:
        session = db.query(ScrapeSession).filter(ScrapeSession.id == session_id).first()
        if not session:
            return

        print(f"\n{'='*60}")
        print(f"{platform.title()} Background Scrape Started")
        print(f"Session: {session_id}")
        print(f"Job Titles: {', '.join(job_titles)}")
        print(f"Location: {location}")
        print(f"{'='*60}")

        spider_key = api_keys_dict.get("spider_api_key") or None
        gemini_key = api_keys_dict.get("gemini_api_key") or None
        hubspot_key = api_keys_dict.get("hubspot_api_key") or None

        scraper = scraper_cls(
            spider_api_key=spider_key,
            gemini_api_key=gemini_key,
        )
        jobs = scraper.scrape_multiple_titles(
            job_titles, location, max_pages=max_pages
        )

        if not jobs:
            session.status = "completed"
            session.total_jobs = 0
            session.eligible_jobs = 0
            session.completed_at = datetime.now(timezone.utc)
            db.commit()
            return

        # Save scraped JSON (backward compat)
        save_with_timestamp(jobs, f"{platform}_jobs", validated=False)

        # Save scraped jobs to DB
        db_jobs = []
        for job_data in jobs:
            db_job = Job(
                session_id=session.id,
                platform=platform,
                job_title=job_data.get("job_title", ""),
                employer_name=job_data.get("employer_name", ""),
                location=job_data.get("location", ""),
                job_description=job_data.get("job_description", ""),
                salary=job_data.get("salary", ""),
                posted_date=job_data.get("posted_date", ""),
                url=job_data.get("url", ""),
                search_title=job_data.get("search_title", ""),
                search_location=job_data.get("search_location", ""),
            )
            db.add(db_job)
            db_jobs.append(db_job)
        db.commit()

        # ANZSCO validation
        session.status = "validating"
        db.commit()

        validated_jobs = scraper.validate_jobs_with_anzsco(jobs)
        save_with_timestamp(validated_jobs, f"{platform}_jobs", validated=True)

        # Save assessments to DB
        eligible_count = 0
        for db_job, validated_job in zip(db_jobs, validated_jobs):
            assessment_data = validated_job.get("anzsco_assessment", {})
            is_eligible = assessment_data.get("eligible", False)
            if is_eligible:
                eligible_count += 1

            assessment = AnzscoAssessment(
                job_id=db_job.id,
                eligible=is_eligible,
                occupation=assessment_data.get("occupation", ""),
                anzsco_code=assessment_data.get("anzsco_code", ""),
                confidence_score=assessment_data.get("confidence_score", 0.0),
                reason=assessment_data.get("reason", ""),
            )
            db.add(assessment)
        db.commit()

        # Company enrichment
        session.status = "enriching"
        db.commit()

        print(f"\n{'='*60}")
        print(f"Processing Company Information")
        print(f"{'='*60}")

        companies = extract_companies_from_jobs(validated_jobs, source=platform)
        print(f"Found {len(companies)} unique companies")
        enriched_companies = enrich_companies_with_details(
            companies, max_companies=10,
            spider_api_key=spider_key,
        )

        # Save companies to DB (upsert by name+source)
        for comp_data in enriched_companies:
            comp_name = comp_data.get("name", "")
            comp_source = comp_data.get("source", platform)
            if not comp_name or comp_name == "Not specified":
                continue

            existing = db.query(Company).filter(
                Company.name == comp_name,
                Company.source == comp_source,
            ).first()

            if existing:
                existing.description = comp_data.get("description", "") or existing.description
                existing.website = comp_data.get("website", "") or existing.website
                existing.industry = comp_data.get("industry", "") or existing.industry
                existing.source_url = comp_data.get("source_url", "") or existing.source_url
                existing.anzsco_eligible = comp_data.get("anzsco_eligible", False) or existing.anzsco_eligible
                existing.job_count = (existing.job_count or 0) + comp_data.get("job_count", 0)
                existing.updated_at = datetime.now(timezone.utc)
                db_company = existing
            else:
                db_company = Company(
                    name=comp_name,
                    description=comp_data.get("description", ""),
                    website=comp_data.get("website", ""),
                    industry=comp_data.get("industry", ""),
                    source=comp_source,
                    source_url=comp_data.get("source_url", ""),
                    anzsco_eligible=comp_data.get("anzsco_eligible", False),
                    job_count=comp_data.get("job_count", 0),
                )
                db.add(db_company)

            db.flush()

            link_exists = db.query(SessionCompany).filter(
                SessionCompany.session_id == session.id,
                SessionCompany.company_id == db_company.id,
            ).first()
            if not link_exists:
                db.execute(
                    SessionCompany.__table__.insert().values(
                        session_id=session.id,
                        company_id=db_company.id,
                    )
                )
        db.commit()

        # HubSpot sync
        hubspot = HubSpotIntegration(api_key=hubspot_key)
        if hubspot.is_enabled():
            hubspot.batch_sync_companies(enriched_companies)
            for comp_data in enriched_companies:
                comp_name = comp_data.get("name", "")
                comp_source = comp_data.get("source", platform)
                if not comp_name or comp_name == "Not specified":
                    continue
                db_comp = db.query(Company).filter(
                    Company.name == comp_name,
                    Company.source == comp_source,
                ).first()
                if db_comp:
                    db_comp.hubspot_status = "created"
                    db_comp.hubspot_synced_at = datetime.now(timezone.utc)
            db.commit()
        else:
            print("\nHubSpot integration not enabled (missing API key)")

        # Update session as completed
        session.status = "completed"
        session.total_jobs = len(jobs)
        session.eligible_jobs = eligible_count
        session.completed_at = datetime.now(timezone.utc)
        db.commit()

        print(f"\n{'='*60}")
        print(f"{platform.title()} Background Scrape Completed — {len(jobs)} jobs")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Background scrape error: {e}")
        try:
            session = db.query(ScrapeSession).filter(ScrapeSession.id == session_id).first()
            if session:
                session.status = "failed"
                session.error_message = str(e)
                session.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


# ------------------------------------------------------------------
# Scrape endpoints
# ------------------------------------------------------------------

def _start_scrape(platform, scraper_cls, request, api_keys: ApiKeys, db: DBSession):
    """Create session and launch background scrape thread. Returns session_id immediately."""
    session_id = _create_session(platform, request, db)

    # Capture API keys as plain dict for the background thread
    keys_dict = {
        "spider_api_key": api_keys.spider_api_key,
        "gemini_api_key": api_keys.gemini_api_key,
        "hubspot_api_key": api_keys.hubspot_api_key,
    }

    thread = threading.Thread(
        target=_run_scrape_background,
        args=(platform, scraper_cls, request.job_titles, request.location, request.max_pages, keys_dict, session_id),
        daemon=True,
    )
    thread.start()

    return {
        "success": True,
        "platform": platform,
        "total_jobs": 0,
        "scraped_file": "",
        "validated_file": "",
        "timestamp": datetime.now().isoformat(),
        "message": f"Scrape started in background for {platform.title()}",
        "companies_synced": None,
        "session_id": session_id,
    }


# Indeed API
@app.post("/api/scrape/indeed", response_model=ScrapeResponse)
async def scrape_indeed(
    request: ScrapeRequest,
    api_keys: ApiKeys = Depends(get_api_keys),
    db: DBSession = Depends(get_db),
):
    return _start_scrape("indeed", IndeedJobTitleScraper, request, api_keys, db)


# Seek API
@app.post("/api/scrape/seek", response_model=ScrapeResponse)
async def scrape_seek(
    request: ScrapeRequest,
    api_keys: ApiKeys = Depends(get_api_keys),
    db: DBSession = Depends(get_db),
):
    return _start_scrape("seek", SeekJobTitleScraper, request, api_keys, db)


# CareerOne API
@app.post("/api/scrape/careerone", response_model=ScrapeResponse)
async def scrape_careerone(
    request: ScrapeRequest,
    api_keys: ApiKeys = Depends(get_api_keys),
    db: DBSession = Depends(get_db),
):
    return _start_scrape("careerone", CareerOneJobTitleScraper, request, api_keys, db)


# ------------------------------------------------------------------
# CRUD endpoints
# ------------------------------------------------------------------

@app.get("/api/sessions")
def list_sessions(
    platform: str = None,
    limit: int = 20,
    offset: int = 0,
    db: DBSession = Depends(get_db),
):
    query = db.query(ScrapeSession).order_by(ScrapeSession.created_at.desc())
    if platform:
        query = query.filter(ScrapeSession.platform == platform)
    total = query.count()
    sessions = query.offset(offset).limit(limit).all()
    return {
        "sessions": [_session_to_dict(s) for s in sessions],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(ScrapeSession).filter(ScrapeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_to_dict(session, include_jobs=True)


@app.get("/api/sessions/{session_id}/jobs")
def get_session_jobs(session_id: str, db: DBSession = Depends(get_db)):
    jobs = db.query(Job).filter(Job.session_id == session_id).all()
    return {"jobs": [_job_to_dict(j) for j in jobs]}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str, db: DBSession = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_dict(job)


@app.get("/api/companies")
def list_companies(
    limit: int = 50,
    offset: int = 0,
    db: DBSession = Depends(get_db),
):
    query = db.query(Company).order_by(Company.job_count.desc())
    total = query.count()
    companies = query.offset(offset).limit(limit).all()
    return {
        "companies": [_company_to_dict(c) for c in companies],
        "total": total,
    }


@app.get("/api/stats")
def get_stats(db: DBSession = Depends(get_db)):
    total_sessions = db.query(func.count(ScrapeSession.id)).scalar()
    total_jobs = db.query(func.count(Job.id)).scalar()
    eligible_jobs = db.query(func.count(AnzscoAssessment.id)).filter(AnzscoAssessment.eligible == True).scalar()
    total_companies = db.query(func.count(Company.id)).scalar()

    platform_counts = (
        db.query(ScrapeSession.platform, func.count(ScrapeSession.id))
        .group_by(ScrapeSession.platform)
        .all()
    )

    return {
        "total_sessions": total_sessions or 0,
        "total_jobs": total_jobs or 0,
        "eligible_jobs": eligible_jobs or 0,
        "total_companies": total_companies or 0,
        "eligibility_rate": round((eligible_jobs or 0) / max(total_jobs or 1, 1) * 100, 1),
        "platforms": [{"platform": p, "count": c} for p, c in platform_counts],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_main:app", host="0.0.0.0", port=3001, reload=True)
