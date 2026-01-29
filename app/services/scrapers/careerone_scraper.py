import urllib.parse
import re
from typing import List, Dict, Any
from scrapling.fetchers import StealthyFetcher
from playwright.sync_api import Page
from bs4 import BeautifulSoup
from app.services.scrapers.base_scraper import BaseScraper
import asyncio
import time
import random


class CareerOneScraper(BaseScraper):
    """Scraper for CareerOne Australia"""

    def __init__(self):
        super().__init__("careerone")
        self.BASE_URL = 'https://www.careerone.com.au'

    def build_search_url(self, job_title: str, location: str, page: int = 1) -> str:
        """Build CareerOne search URL"""
        clean_title = job_title.strip().lower().replace(' ', '-')
        clean_location = location.strip().lower().replace(' ', '-').replace(',', '')

        # Remove state abbreviations
        clean_location = re.sub(r'\b(nsw|vic|qld|sa|wa|tas|nt|act)\b', '', clean_location).strip('-')

        if page == 1:
            url = f"{self.BASE_URL}/jobs/{clean_title}/{clean_location}"
        else:
            url = f"{self.BASE_URL}/jobs/{clean_title}/{clean_location}?page={page}"

        return url

    def extract_jobs_from_page(self, soup: BeautifulSoup, job_title: str, location: str) -> List[Dict[str, Any]]:
        """Extract job listings from CareerOne search results page"""
        jobs = []

        # CareerOne job cards - use the selector that actually works
        job_cards = soup.select('div[class*="job-card"]')

        for card in job_cards[:20]:  # Limit to first 20
            try:
                # Extract title from h2 or h3 tag within the card
                title_elem = card.find(['h2', 'h3'])
                title = None
                if title_elem:
                    title_link = title_elem.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                    else:
                        title = title_elem.get_text(strip=True)

                if not title:
                    continue

                # Extract company - look for elements with 'recruiter' or 'employer' in class
                company = "Not specified"
                # Try to find company info in the card
                company_indicators = ['recruiter', 'company', 'employer']
                for indicator in company_indicators:
                    company_elem = card.find(attrs={'class': lambda x: x and indicator in ' '.join(x).lower()})
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                        break

                # Extract location
                job_location = location
                # Look for location in various ways
                location_elem = card.find(attrs={'class': lambda x: x and 'location' in ' '.join(x).lower()})
                if not location_elem:
                    # Try finding by text content
                    all_divs = card.find_all('div')
                    for div in all_divs:
                        text = div.get_text(strip=True)
                        if any(state in text for state in ['NSW', 'QLD', 'VIC', 'SA', 'WA', 'NT', 'ACT', 'TAS', 'Sydney', 'Melbourne', 'Brisbane', 'Perth']):
                            job_location = text
                            break
                elif location_elem:
                    job_location = location_elem.get_text(strip=True)

                # Extract job URL from the main link
                job_url = None
                link_elem = card.find('a', href=True)
                if link_elem and 'href' in link_elem.attrs:
                    href = link_elem['href']
                    if href:
                        if href.startswith('http'):
                            job_url = href
                        elif href.startswith('/'):
                            job_url = f"{self.BASE_URL}{href}"
                        else:
                            job_url = f"{self.BASE_URL}/{href}"

                if job_url and title:
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'url': job_url
                    })

            except Exception as e:
                print(f"Error extracting CareerOne job: {e}")
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

                    # Scroll to load content
                    for i in range(3):
                        page.evaluate('window.scrollBy(0, 400)')
                        page.wait_for_timeout(300)

                    # Brief pause
                    page.wait_for_timeout(500)

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
                wait_selector='.job-description, [class*="description"], .job-details',
                wait=1500,
                timeout=90000,
                page_action=human_behavior
            )

            if response.status == 200:
                # Extract description
                description = "Description not available"

                desc_selectors = [
                    '.job-description',
                    '.job-details',
                    '[class*="description"]',
                    '.description-content',
                    '.job-body',
                    '.job-content',
                    'div[data-automation="jobDescription"]',
                    '#jobDescription',
                    '.jobAdDetails'
                ]

                for selector in desc_selectors:
                    desc_elem = response.css_first(selector)
                    if desc_elem:
                        description = desc_elem.get_all_text(separator='\n', strip=True)
                        if len(description) > 100:
                            break

                # Extract posted date
                posted_date = "Unknown"
                date_selectors = [
                    '[class*="date"]',
                    '[class*="posted"]',
                    '[class*="time"]',
                    'time',
                    '.posted-date',
                    '.job-date'
                ]

                for selector in date_selectors:
                    elements = response.css(selector)
                    for elem in elements:
                        text = elem.text if elem.text else ''
                        if any(word in text.lower() for word in ['ago', 'day', 'hour', 'minute', 'just', 'recent', 'posted', 'advertised']):
                            if len(text) < 100:
                                posted_date = text.strip()
                                break
                    if posted_date != "Unknown":
                        break

                # Extract salary
                salary = "Not specified"
                salary_selectors = [
                    '[class*="salary"]',
                    '[class*="pay"]',
                    '[class*="wage"]',
                    '.salary',
                    '.job-salary',
                    '.remuneration'
                ]

                for selector in salary_selectors:
                    elem = response.css_first(selector)
                    if elem:
                        text = elem.text if elem.text else ''
                        if any(word in text.lower() for word in ['$', 'salary', 'pay', 'package', 'k', 'annum']):
                            salary = text.strip()
                            break

                return {
                    'description': description,
                    'posted_date': posted_date,
                    'salary': salary
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