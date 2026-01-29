from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from scrapling.fetchers import StealthyFetcher
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import asyncio
import time
import random
from app.core.config import settings
from app.models.schemas import JobResponse


class BaseScraper(ABC):
    """Base class for job scrapers"""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.ua = UserAgent() if settings.user_agent_rotate else None

    def get_random_user_agent(self) -> str:
        """Get a random user agent string"""
        if self.ua:
            return self.ua.random
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    async def make_request(self, url: str, retries: int = None) -> Optional[BeautifulSoup]:
        """Make HTTP request with retry logic and return parsed soup"""
        if retries is None:
            retries = settings.max_retries

        loop = asyncio.get_event_loop()

        for attempt in range(retries):
            try:
                # Run the sync fetch in a thread pool
                response = await loop.run_in_executor(None, self._sync_fetch, url)

                if response.status == 200:
                    # Use html_content instead of text
                    return BeautifulSoup(response.html_content, 'html.parser')
                else:
                    print(f"Request failed with status {response.status} for {url}")

            except Exception as e:
                if attempt == retries - 1:
                    print(f"Failed to fetch {url} after {retries} attempts: {e}")
                    return None
                # Exponential backoff
                delay = (2 ** attempt) + random.random()
                await asyncio.sleep(delay)

        return None

    def _sync_fetch(self, url: str):
        """Synchronous fetch method to run in thread pool"""
        return StealthyFetcher.fetch(
            url,
            headless=True,
            hide_canvas=True,
            block_webrtc=True,
            network_idle=False,
            load_dom=True,
            wait=2000,
            timeout=settings.request_timeout * 1000  # Convert to milliseconds
        )

    @abstractmethod
    def build_search_url(self, job_title: str, location: str, page: int = 1) -> str:
        """Build search URL for the specific job board"""
        pass

    @abstractmethod
    def extract_jobs_from_page(self, soup: BeautifulSoup, job_title: str, location: str) -> List[Dict[str, Any]]:
        """Extract job listings from parsed HTML"""
        pass

    @abstractmethod
    async def extract_job_details(self, job_url: str) -> Dict[str, Any]:
        """Extract detailed job information from individual job page"""
        pass

    async def scrape_jobs(self, job_title: str, location: str, max_results: int = 10) -> List[JobResponse]:
        """Main scraping method"""
        jobs = []
        page = 1

        while len(jobs) < max_results:
            url = self.build_search_url(job_title, location, page)
            soup = await self.make_request(url)

            if not soup:
                break

            page_jobs = self.extract_jobs_from_page(soup, job_title, location)

            if not page_jobs:
                break

            # Get detailed information for each job
            for job_data in page_jobs:
                if len(jobs) >= max_results:
                    break

                try:
                    details = await self.extract_job_details(job_data['url'])
                    job = JobResponse(
                        title=job_data.get('title', job_title),
                        company=job_data.get('company', 'Not specified'),
                        location=job_data.get('location', location),
                        description=details.get('description', 'No description available'),
                        url=job_data['url'],
                        posted_date=details.get('posted_date'),
                        salary=details.get('salary'),
                        source=self.source_name
                    )
                    jobs.append(job)
                except Exception as e:
                    print(f"Error extracting details for job: {e}")
                    continue

            page += 1

            # Rate limiting
            await asyncio.sleep(1)

        return jobs[:max_results]