"""Debug script to test the API scrapers"""
import asyncio
from app.services.scraper_service import ScraperService
from app.models.schemas import JobSearchRequest


async def test_scraper():
    """Test the scraper service"""
    
    service = ScraperService()
    
    # Test request
    request = JobSearchRequest(
        job_title="ICT Project Manager",
        location="Sydney-NSW",
        max_results=5
    )
    
    print("Testing Scraper Service...")
    print(f"Searching for: {request.job_title} in {request.location}")
    print("-" * 80)
    
    # Test all platforms
    for platform in ['indeed', 'seek', 'careerone']:
        print(f"\nTesting {platform.upper()}...")
        result = await service.scrape_from_platform(platform, request)
        print(f"Success: {result.success}")
        print(f"Jobs found: {result.total_found}")
        if result.error_message:
            print(f"Error: {result.error_message}")
        
        # Print first job if available
        if result.jobs:
            print(f"First job: {result.jobs[0].title}")
        else:
            print("No jobs found")
    
    print("\n" + "-" * 80)
    print("Testing combined scrape...")
    result = await service.scrape_jobs(request)
    print(f"Success: {result.success}")
    print(f"Total jobs found: {result.total_found}")
    print(f"Error: {result.error_message}")
    
    if result.jobs:
        for job in result.jobs[:3]:
            print(f"  - {job.title} ({job.source})")


if __name__ == "__main__":
    asyncio.run(test_scraper())
