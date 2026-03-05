"""
Seek Job Scraper — Spider.cloud + ANZSCO 482 Validation
Thin subclass of SpiderBaseScraper for seek.com.au
"""

from bs4 import BeautifulSoup
from datetime import datetime
from spider_base_scraper import SpiderBaseScraper


class SeekJobTitleScraper(SpiderBaseScraper):
    """Scrape Seek Australia via Spider.cloud API."""

    BASE_URL = "https://www.seek.com.au"

    def build_search_url(self, job_title, location, page):
        """Build Seek search URL.  Seek uses 1-indexed pages."""
        clean_title = job_title.replace(" ", "-").lower()
        clean_location = location.replace(" ", "-").lower()
        page_num = page + 1  # base class passes 0-indexed page
        if page_num == 1:
            return f"{self.BASE_URL}/{clean_title}-jobs/in-{clean_location}"
        return f"{self.BASE_URL}/{clean_title}-jobs/in-{clean_location}?page={page_num}"

    def parse_listing_html(self, html, job_title, location):
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        cards = soup.select('[data-automation="normalJob"]')
        if not cards:
            cards = soup.select("article[data-search-sol-meta]")

        for card in cards:
            # Title
            title = None
            title_el = card.select_one('[data-automation="jobTitle"]')
            if title_el:
                title = title_el.get_text(strip=True)
            if not title:
                h3 = card.select_one("h3")
                if h3:
                    title = h3.get_text(strip=True)

            # Company
            company = None
            co_el = card.select_one('[data-automation="jobCompany"]')
            if co_el:
                company = co_el.get_text(strip=True)
            if not company:
                co_span = card.select_one('span[class*="company"]')
                if co_span:
                    company = co_span.get_text(strip=True)

            # Location
            loc_text = location
            loc_el = card.select_one('[data-automation="jobLocation"]')
            if loc_el:
                loc_text = loc_el.get_text(strip=True)

            # URL
            job_url = None
            for sel in ['a[data-automation="jobTitle"]', 'h3 a', 'a[href*="/job/"]']:
                link = card.select_one(sel)
                if link and link.get("href"):
                    href = link["href"]
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
    scraper = SeekJobTitleScraper()
    jobs = scraper.scrape_multiple_titles(["Software Engineer"], "Sydney-NSW", max_pages=2)
    if jobs:
        validated = scraper.validate_jobs_with_anzsco(jobs)
        print(f"\nTotal: {len(validated)} jobs")
