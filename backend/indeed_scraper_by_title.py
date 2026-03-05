"""
Indeed Job Scraper — Spider.cloud + ANZSCO 482 Validation
Thin subclass of SpiderBaseScraper for au.indeed.com
"""

from bs4 import BeautifulSoup
from datetime import datetime
from spider_base_scraper import SpiderBaseScraper
import urllib.parse


class IndeedJobTitleScraper(SpiderBaseScraper):
    """Scrape Indeed Australia via Spider.cloud API."""

    BASE_URL = "https://au.indeed.com"

    def build_search_url(self, job_title, location, page):
        """Build Indeed search URL.  fromage=2 → last 48 hours."""
        q = urllib.parse.quote(job_title)
        loc = urllib.parse.quote(location)
        start = page * 10  # Indeed uses 0-indexed start offset
        return f"{self.BASE_URL}/jobs?q={q}&l={loc}&fromage=2&start={start}"

    def parse_listing_html(self, html, job_title, location):
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        for card in soup.select("div.job_seen_beacon"):
            # Title
            title = None
            title_el = card.select_one("h2 span[title]")
            if title_el:
                title = title_el.get("title", "").strip() or title_el.get_text(strip=True)
            if not title:
                title_el = card.select_one('h2 span[id^="jobTitle"]')
                if title_el:
                    title = title_el.get_text(strip=True)
            if not title:
                h2 = card.select_one("h2")
                if h2:
                    title = h2.get_text(strip=True)

            # Company — Spider returns server-rendered HTML without data-testid
            company = None
            co_el = card.select_one('[data-testid="company-name"]')
            if co_el:
                company = co_el.get_text(strip=True)
            if not company:
                # Raw HTML: company is in div.company_location > div > span
                co_el = card.select_one("div.company_location span")
                if co_el:
                    company = co_el.get_text(strip=True)

            # Location
            loc_text = location
            loc_el = card.select_one('[data-testid="text-location"]')
            if loc_el:
                loc_text = loc_el.get_text(strip=True)
            if loc_text == location:
                # Raw HTML: location is second div inside company_location
                loc_divs = card.select("div.company_location div > div")
                if len(loc_divs) >= 2:
                    loc_text = loc_divs[1].get_text(strip=True) or location

            # URL
            job_url = None
            for a in card.select("a"):
                href = a.get("href", "")
                if "jk=" in href:
                    job_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                    break

            if title and company and job_url:
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": loc_text,
                    "url": job_url,
                    "search_title": job_title,
                    "search_location": location,
                })

        return jobs

    def parse_job_detail(self, content, job_info):
        description = content.strip() if content else "Description not available"
        if len(description) < 50:
            description = "Description not available"

        return {
            "job_title": job_info["title"],
            "employer_name": job_info["company"],
            "location": job_info["location"],
            "job_description": description,
            "posted_date": "Unknown",
            "search_title": job_info["search_title"],
            "search_location": job_info["search_location"],
            "url": job_info["url"],
            "scraped_at": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    scraper = IndeedJobTitleScraper()
    jobs = scraper.scrape_multiple_titles(["ICT Project Manager"], "Sydney NSW", max_pages=2)
    if jobs:
        validated = scraper.validate_jobs_with_anzsco(jobs)
        print(f"\nTotal: {len(validated)} jobs")
