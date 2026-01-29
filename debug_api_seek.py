"""
Debug script to test the API seek scraper logic
"""

from bs4 import BeautifulSoup
import asyncio

async def test_seek_scraper():
    """Test the seek scraper directly"""
    from app.services.scrapers.seek_scraper import SeekScraper
    scraper = SeekScraper()

    print("Testing Seek scraper...")

    # Test URL building
    url = scraper.build_search_url("ICT Project Manager", "Sydney-NSW", 1)
    print(f"URL: {url}")

    # Test fetching directly with the sync method
    from app.services.scrapers.seek_scraper import SeekScraper
    test_scraper = SeekScraper()
    response = test_scraper._sync_fetch(url)

    print(f"Response status: {response.status}")
    print(f"Response text length: {len(response.text) if hasattr(response, 'text') else 'No text attr'}")

    if hasattr(response, 'text') and response.text:
        print(f"Response text preview: {response.text[:200]}...")
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Page fetched successfully")
    else:
        print("Response has no text content")
        return

    # Debug: Check what the soup contains
    print(f"Soup title: {soup.title.text if soup.title else 'No title'}")
    print(f"Soup length: {len(str(soup))}")

    # Check for any divs or main content
    body = soup.find('body')
    if body:
        print(f"Body length: {len(str(body))}")
        # Look for any elements with 'job' in class or id
        job_elements = body.find_all(attrs={'class': lambda x: x and 'job' in x.lower()})
        print(f"Elements with 'job' in class: {len(job_elements)}")

    # Debug: Check what articles exist
    all_articles = soup.find_all('article')
    print(f"Total articles found: {len(all_articles)}")

    # Check for data-automation attributes
    normal_jobs = soup.find_all('article', attrs={'data-automation': 'normalJob'})
    print(f"Articles with data-automation='normalJob': {len(normal_jobs)}")

    testid_jobs = soup.find_all('article', attrs={'data-testid': 'job-card'})
    print(f"Articles with data-testid='job-card': {len(testid_jobs)}")

    # Check for any articles with job-id
    job_id_articles = soup.find_all('article', attrs={'data-job-id': True})
    print(f"Articles with data-job-id: {len(job_id_articles)}")

    # Show a sample of article HTML
    if all_articles:
        print("Sample article HTML (first 500 chars):")
        print(str(all_articles[0])[:500])
        print("...")

    # Test job extraction
    jobs_data = scraper.extract_jobs_from_page(soup, "ICT Project Manager", "Sydney-NSW")
    print(f"Extracted {len(jobs_data)} job data entries")

    for i, job_data in enumerate(jobs_data, 1):
        print(f"{i}. {job_data.get('title', 'No title')} - {job_data.get('company', 'No company')}")

    # If we have job data, test full scraping
    if jobs_data:
        jobs = await scraper.scrape_jobs(
            job_title="ICT Project Manager",
            location="Sydney-NSW",
            max_results=5
        )

        print(f"Full scrape found {len(jobs)} jobs")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job.title} at {job.company} - {job.location}")
            print(f"   URL: {job.url}")

if __name__ == "__main__":
    asyncio.run(test_seek_scraper())