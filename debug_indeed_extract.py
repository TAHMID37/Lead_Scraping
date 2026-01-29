"""Debug script to test the extraction_jobs_from_page method specifically"""
import asyncio
from scrapling.fetchers import StealthyFetcher
from bs4 import BeautifulSoup
from app.services.scrapers.indeed_scraper import IndeedScraper

async def debug_indeed():
    scraper = IndeedScraper()
    
    # Build URL
    url = scraper.build_search_url("ICT Project Manager", "Sydney-NSW")
    print(f"URL: {url}\n")
    
    # Fetch page
    soup = await scraper.make_request(url)
    if not soup:
        print("Failed to fetch page")
        return
    
    # Extract jobs from page
    print("Extracting jobs from page...")
    jobs = scraper.extract_jobs_from_page(soup, "ICT Project Manager", "Sydney-NSW")
    print(f"Found {len(jobs)} jobs:\n")
    
    for i, job in enumerate(jobs):
        print(f"Job {i+1}:")
        print(f"  Title: {job['title']}")
        print(f"  Company: {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  URL: {job['url'][:80]}")
        print()

if __name__ == "__main__":
    asyncio.run(debug_indeed())
