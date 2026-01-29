import urllib.parse
from typing import List, Dict, Any
from scrapling.fetchers import StealthyFetcher
from playwright.sync_api import Page
from bs4 import BeautifulSoup
from app.services.scrapers.base_scraper import BaseScraper
import asyncio
import time
import random


class IndeedScraper(BaseScraper):
    """Scraper for Indeed Australia"""

    def __init__(self):
        super().__init__("indeed")
        self.BASE_URL = 'https://au.indeed.com'

    def build_search_url(self, job_title: str, location: str, page: int = 1) -> str:
        """Build Indeed search URL"""
        encoded_title = urllib.parse.quote(job_title)
        encoded_location = urllib.parse.quote(location)

        # Indeed uses 0-based pagination, 10 results per page
        start = (page - 1) * 10
        url = f"{self.BASE_URL}/jobs?q={encoded_title}&l={encoded_location}&fromage=1&start={start}"
        return url

    def extract_jobs_from_page(self, soup: BeautifulSoup, job_title: str, location: str) -> List[Dict[str, Any]]:
        """Extract job listings from Indeed search results page"""
        jobs = []

        # Indeed job cards - each card is wrapped in job_seen_beacon
        job_cards = soup.find_all('div', class_='job_seen_beacon')

        for card in job_cards:
            try:
                # Extract title from the h2 with class jobTitle
                title_elem = card.find('h2', class_='jobTitle')
                title = None
                if title_elem:
                    span = title_elem.find('span', attrs={'id': lambda x: x and 'jobTitle-' in x})
                    if span:
                        title = span.get_text(strip=True)

                if not title:
                    # Fallback: try to get from link text
                    link = card.find('a', class_='jcs-JobTitle')
                    if link:
                        span = link.find('span')
                        if span:
                            title = span.get_text(strip=True)

                # Extract company name from span with data-testid='company-name'
                company = "Not specified"
                company_elem = card.find('span', attrs={'data-testid': 'company-name'})
                if company_elem:
                    company = company_elem.get_text(strip=True)

                # Extract location from div with data-testid='text-location'
                job_location = location
                location_elem = card.find('div', attrs={'data-testid': 'text-location'})
                if location_elem:
                    job_location = location_elem.get_text(strip=True)

                # Extract job URL from the main link
                job_url = None
                link = card.find('a', class_='jcs-JobTitle')
                if link and 'href' in link.attrs:
                    href = link['href']
                    if href:
                        job_url = f"{self.BASE_URL}{href}" if not href.startswith('http') else href

                if title and job_url:
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'url': job_url
                    })

            except Exception as e:
                print(f"Error extracting Indeed job: {e}")
                continue

        return jobs

    async def extract_job_details(self, job_url: str) -> Dict[str, Any]:
        """Extract detailed job information from individual job page"""
        loop = asyncio.get_event_loop()
        try:
            # Run the sync extraction in a thread pool
            result = await loop.run_in_executor(None, self._sync_extract_job_details, job_url)
            return result
        except Exception as e:
            return {
                'description': f"Error: {str(e)}",
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
                    for i in range(2):
                        page.evaluate('window.scrollBy(0, 300)')
                        page.wait_for_timeout(200)

                    # Brief pause
                    page.wait_for_timeout(300)

                    # Scroll back up
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
                wait_selector='#jobDescriptionText',
                wait=1500,
                timeout=90000,
                page_action=human_behavior
            )

            if response.status == 200:
                # Extract description
                description = "Description not available"

                desc_elem = response.css_first('#jobDescriptionText')
                if desc_elem:
                    description = desc_elem.get_all_text(separator='\n', strip=True)

                    if not description or len(description) < 50:
                        description = desc_elem.text.strip() if desc_elem.text else "Description not available"

                # Extract posted date
                posted_date = "Unknown"
                date_elements = response.css('[class*="date"], [class*="Date"], time, span')
                for elem in date_elements:
                    text = elem.text if elem.text else ''
                    text_lower = text.lower()
                    if any(word in text_lower for word in ['posted', 'ago', 'day', 'hour', 'today', 'yesterday']):
                        if len(text) < 50:
                            posted_date = text.strip()
                            break

                return {
                    'description': description,
                    'posted_date': posted_date,
                    'salary': None  # Indeed doesn't always show salary
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