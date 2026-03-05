"""
CareerOne Job Scraper — Spider.cloud + ANZSCO 482 Validation
Thin subclass of SpiderBaseScraper for careerone.com.au
"""

from bs4 import BeautifulSoup
from datetime import datetime
from spider_base_scraper import SpiderBaseScraper
import re


class CareerOneJobTitleScraper(SpiderBaseScraper):
    """Scrape CareerOne Australia via Spider.cloud API."""

    BASE_URL = "https://www.careerone.com.au"
    LISTING_REQUEST_MODE = "chrome"  # CareerOne is a JS SPA, needs headless browser

    def build_search_url(self, job_title, location, page):
        """Build CareerOne search URL.  1-indexed pages."""
        clean_title = job_title.strip().lower().replace(" ", "-")
        clean_location = location.strip().lower().replace(" ", "-").replace(",", "")
        clean_location = re.sub(r"\b(nsw|vic|qld|sa|wa|tas|nt|act)\b", "", clean_location).strip("-")
        page_num = page + 1
        if page_num == 1:
            return f"{self.BASE_URL}/jobs/{clean_title}/{clean_location}"
        return f"{self.BASE_URL}/jobs/{clean_title}/{clean_location}?page={page_num}"

    def parse_listing_html(self, html, job_title, location):
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        for card in soup.select("div.job-card-detailed"):
            # Title
            title_el = card.select_one("h2 a.d-block") or card.select_one("h2 a")
            title = title_el.get_text(strip=True) if title_el else None
            if not title:
                continue

            # Company
            company = "Not specified"
            company_url = ""
            co_el = (
                card.select_one("h3 a.text-title-3")
                or card.select_one("h3 a.link-hover-default")
                or card.select_one("h3 a")
            )
            if co_el:
                text = co_el.get_text(strip=True)
                if text and 2 < len(text) < 150:
                    company = text
                href = co_el.get("href", "")
                if href:
                    company_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

            # Location
            job_location = location
            loc_links = card.select('a[href*="/jobs/in-"]')
            for ll in loc_links:
                lt = ll.get_text(strip=True)
                if lt and len(lt) < 50:
                    job_location = lt
                    break

            # URL
            job_url = None
            if title_el:
                href = title_el.get("href", "")
                if href:
                    job_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

            # Brief description
            brief = ""
            points = card.select("ul li.text-body-4")
            if points:
                brief = " ".join(p.get_text(strip=True) for p in points[:2])

            if job_url and title:
                jobs.append({
                    "title": title,
                    "company": company,
                    "company_url": company_url,
                    "location": job_location,
                    "url": job_url,
                    "brief_description": brief,
                    "search_title": job_title,
                    "search_location": location,
                })

        return jobs

    def parse_job_detail(self, content, job_info):
        description = content.strip() if content else "Description not available"
        if len(description) < 50:
            description = "Description not available"

        # Try to find salary in the markdown content
        salary = "Not specified"
        if content:
            for line in content.split("\n"):
                low = line.lower()
                if any(kw in low for kw in ["$", "salary", "package", "annum", "per year"]):
                    if len(line) < 200:
                        salary = line.strip()
                        break

        return {
            "job_title": job_info["title"],
            "employer_name": job_info["company"],
            "company_url": job_info.get("company_url", ""),
            "location": job_info["location"],
            "job_description": description,
            "brief_description": job_info.get("brief_description", ""),
            "posted_date": "Unknown",
            "salary": salary,
            "search_title": job_info["search_title"],
            "search_location": job_info["search_location"],
            "url": job_info["url"],
            "scraped_at": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    scraper = CareerOneJobTitleScraper()
    jobs = scraper.scrape_multiple_titles(["Software Engineer"], "Sydney", max_pages=2)
    if jobs:
        validated = scraper.validate_jobs_with_anzsco(jobs)
        print(f"\nTotal: {len(validated)} jobs")
