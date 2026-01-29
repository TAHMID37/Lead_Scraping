"""Debug script to test Indeed scraper directly"""
import asyncio
from app.services.scrapers.indeed_scraper import IndeedScraper

async def test_indeed_scraper():
    scraper = IndeedScraper()
    
    jobs = await scraper.scrape_jobs(
        job_title="ICT Project Manager",
        location="Sydney-NSW",
        max_results=5
    )
    
    print(f"Jobs found: {len(jobs)}")
    for job in jobs:
        print(f"\n  Title: {job.title}")
        print(f"  Company: {job.company}")
        print(f"  Location: {job.location}")
        print(f"  URL: {job.url}")
        print(f"  Source: {job.source}")

if __name__ == "__main__":
    asyncio.run(test_indeed_scraper())
