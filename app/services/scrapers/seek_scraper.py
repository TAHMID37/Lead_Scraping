import urllib.parse
from typing import List, Dict, Any, Optional
from scrapling.fetchers import StealthyFetcher
from playwright.sync_api import Page
from bs4 import BeautifulSoup
from app.services.scrapers.base_scraper import BaseScraper
import asyncio
import time
import random


class SeekScraper(BaseScraper):
    """Scraper for Seek Australia"""

    def __init__(self):
        super().__init__("seek")
        self.BASE_URL = 'https://www.seek.com.au'

    async def make_request(self, url: str, retries: int = None) -> Optional[BeautifulSoup]:
        """Override make_request with Seek-specific fetch parameters"""
        from scrapling.fetchers import StealthyFetcher
        from bs4 import BeautifulSoup
        import asyncio

        if retries is None:
            retries = 3  # Use fewer retries for Seek

        loop = asyncio.get_event_loop()

        for attempt in range(retries):
            try:
                # Run sync fetch in thread pool to avoid Playwright sync API in asyncio loop error
                response = await loop.run_in_executor(None, self._sync_fetch_seek, url)

                if response and response.status == 200 and response.html_content:
                    return BeautifulSoup(response.html_content, 'html.parser')
                else:
                    print(f"Request failed with status {response.status if response else 'None'} for {url}")

            except Exception as e:
                if attempt == retries - 1:
                    print(f"Failed to fetch {url} after {retries} attempts: {e}")
                    return None
                # Exponential backoff
                delay = (2 ** attempt) + 0.5
                await asyncio.sleep(delay)


        return None

    def _sync_fetch_seek(self, url: str):
        """Synchronous fetch method for Seek with specific parameters"""
        return StealthyFetcher.fetch(
            url,
            headless=True,
            timeout=45000,
            hide_canvas=True,
            block_webrtc=True,
            wait_selector='[data-automation="searchResults"]',
            wait=1000
        )

    def build_search_url(self, job_title: str, location: str, page: int = 1) -> str:
        """Build Seek search URL"""
        clean_title = job_title.replace(' ', '-').lower()
        clean_location = location.replace(' ', '-').lower()

        if page == 1:
            url = f"{self.BASE_URL}/{clean_title}-jobs/in-{clean_location}"
        else:
            url = f"{self.BASE_URL}/{clean_title}-jobs/in-{clean_location}?page={page}"

        return url

    def extract_jobs_from_page(self, soup: BeautifulSoup, job_title: str, location: str) -> List[Dict[str, Any]]:
        """Extract job listings from Seek search results page - using exact logic from working standalone script"""
        jobs = []

        # Find job cards - use the same logic as the working standalone script
        job_cards = soup.find_all('article', attrs={'data-automation': 'normalJob'})

        if not job_cards:
            # Try alternative selector
            job_cards = soup.find_all('article', attrs={'data-search-sol-meta': True})

        if not job_cards:
            # Last resort - try data-testid
            job_cards = soup.find_all('article', attrs={'data-testid': 'job-card'})

        for card in job_cards:
            try:
                # Extract title
                title_elem = card.find('a', attrs={'data-automation': 'jobTitle'})
                if not title_elem:
                    title_elem = card.find('h3').find('a') if card.find('h3') else None

                title = title_elem.get_text(strip=True) if title_elem else job_title

                # Extract company
                company_elem = card.find(attrs={'data-automation': 'jobCompany'})
                company = company_elem.get_text(strip=True) if company_elem else "Not specified"

                # Extract location
                location_elem = card.find(attrs={'data-automation': 'jobLocation'})
                job_location = location_elem.get_text(strip=True) if location_elem else location

                # Extract job URL
                job_url = None
                if title_elem and 'href' in title_elem.attrs:
                    href = title_elem['href']
                    job_url = f"{self.BASE_URL}{href}" if not href.startswith('http') else href

                if title and company and job_url:
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'url': job_url
                    })

            except Exception as e:
                continue

        return jobs

    async def extract_job_details(self, job_url: str) -> Dict[str, Any]:
        """Extract detailed job information from individual job page"""
        # For now, return placeholder data to avoid blocking job listing
        # Individual job page scraping can be implemented later if needed
        return {
            'description': 'Job description available at the job posting URL',
            'posted_date': None,
            'salary': None
        }

    def _sync_extract_job_details(self, job_url: str) -> Dict[str, Any]:
        """Synchronous job details extraction"""
        try:
            # Define human-like page actions
            def human_behavior(page: Page):
                """Simulate human browsing behavior"""
                try:
                    # Quick mouse movement
                    page.mouse.move(100 + int(random.random() * 300), 100 + int(random.random() * 300))
                    page.wait_for_timeout(100)

                    # Quick scroll down
                    for i in range(3):
                        page.evaluate('window.scrollBy(0, 400)')
                        page.wait_for_timeout(200)

                    # Brief pause
                    page.wait_for_timeout(300)

                    # Scroll back up a bit
                    page.evaluate('window.scrollBy(0, -200)')
                except Exception:
                    pass  # Ignore errors in human behavior

            response = StealthyFetcher.fetch(
                job_url,
                headless=True,
                hide_canvas=True,
                block_webrtc=True,
                network_idle=False,
                load_dom=True,
                wait_selector='[data-automation="job-details"], .y735df0',
                wait=1500,
                timeout=60000,
                page_action=human_behavior
            )

            if response.status == 200:
                # Extract description
                description = "Description not available"

                desc_selectors = [
                    '[data-automation="jobAdDetails"]',
                    '[data-automation="job-details"]',
                    '.y735df0',
                    'article[data-automation="job-details"]'
                ]

                for selector in desc_selectors:
                    desc_elem = response.css_first(selector)
                    if desc_elem:
                        description = desc_elem.get_all_text(separator='\n', strip=True)
                        if len(description) > 50:
                            break

                # Extract posted date
                posted_date = "Unknown"
                date_selectors = [
                    '[data-automation="job-detail-date"]',
                    'span[data-automation="jobListingDate"]',
                    'dd[data-automation="job-detail-date"]'
                ]

                for selector in date_selectors:
                    date_elem = response.css_first(selector)
                    if date_elem:
                        date_text = date_elem.text.strip() if date_elem.text else ''
                        if date_text and len(date_text) < 50:
                            posted_date = date_text
                            break

                return {
                    'description': description,
                    'posted_date': posted_date,
                    'salary': None  # Seek doesn't always show salary
                }

            return {
                'description': f"Failed to load page (status {response.status})",
                'posted_date': None,
                'salary': None
            }

        except Exception as e:
            return {
                'description': f"Error: {str(e)}",
                'posted_date': None,
                'salary': None
            }