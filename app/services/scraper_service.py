from typing import List, Optional
from datetime import datetime
from app.models.schemas import JobSearchRequest, ScraperResponse, JobResponse
from app.services.scrapers.indeed_scraper import IndeedScraper
from app.services.scrapers.seek_scraper import SeekScraper
from app.services.scrapers.careerone_scraper import CareerOneScraper
import asyncio


class ScraperService:
    """Service to orchestrate job scraping across multiple platforms"""

    def __init__(self):
        self.scrapers = {
            'indeed': IndeedScraper(),
            'seek': SeekScraper(),
            'careerone': CareerOneScraper()
        }

    async def scrape_jobs(self, request: JobSearchRequest) -> ScraperResponse:
        """Scrape jobs from all platforms based on the request"""
        all_jobs = []

        try:
            # Scrape from each platform concurrently
            tasks = []
            for scraper_name, scraper in self.scrapers.items():
                task = self._scrape_from_platform(scraper_name, scraper, request)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    print(f"Error in scraping task: {result}")
                    continue
                if result:
                    all_jobs.extend(result)

            # Sort by some criteria if needed (e.g., by posted date)
            # For now, just return as collected

            return ScraperResponse(
                success=True,
                jobs=all_jobs,
                total_found=len(all_jobs),
                search_title=request.job_title,
                search_location=request.location,
                scraped_at=datetime.now()
            )

        except Exception as e:
            return ScraperResponse(
                success=False,
                jobs=[],
                total_found=0,
                search_title=request.job_title,
                search_location=request.location,
                scraped_at=datetime.now(),
                error_message=str(e)
            )

    async def scrape_from_platform(self, platform: str, request: JobSearchRequest) -> ScraperResponse:
        """Scrape jobs from a specific platform"""
        if platform not in self.scrapers:
            return ScraperResponse(
                success=False,
                jobs=[],
                total_found=0,
                search_title=request.job_title,
                search_location=request.location,
                scraped_at=datetime.now(),
                error_message=f"Platform '{platform}' not supported. Available: {', '.join(self.scrapers.keys())}"
            )

        try:
            scraper = self.scrapers[platform]
            jobs = await scraper.scrape_jobs(
                job_title=request.job_title,
                location=request.location,
                max_results=request.max_results
            )

            return ScraperResponse(
                success=True,
                jobs=jobs,
                total_found=len(jobs),
                search_title=request.job_title,
                search_location=request.location,
                scraped_at=datetime.now()
            )

        except Exception as e:
            return ScraperResponse(
                success=False,
                jobs=[],
                total_found=0,
                search_title=request.job_title,
                search_location=request.location,
                scraped_at=datetime.now(),
                error_message=str(e)
            )

    async def _scrape_from_platform(self, scraper_name: str, scraper, request: JobSearchRequest) -> List[JobResponse]:
        """Helper method to scrape from a single platform"""
        try:
            jobs = await scraper.scrape_jobs(
                job_title=request.job_title,
                location=request.location,
                max_results=request.max_results
            )
            return jobs
        except Exception as e:
            print(f"Error scraping {scraper_name}: {e}")
            return []