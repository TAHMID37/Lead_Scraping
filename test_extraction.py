"""
Test the extraction logic on saved HTML
"""

from bs4 import BeautifulSoup
from app.services.scrapers.seek_scraper import SeekScraper

def test_extraction():
    """Test extraction on saved HTML"""

    # Load the saved HTML
    with open('seek_page.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Create scraper instance
    scraper = SeekScraper()

    # Test extraction
    jobs_data = scraper.extract_jobs_from_page(soup, "ICT Project Manager", "Sydney-NSW")

    print(f"Extracted {len(jobs_data)} jobs")

    for i, job in enumerate(jobs_data[:3], 1):  # Show first 3
        print(f"{i}. {job.get('title')} at {job.get('company')} - {job.get('url')}")

if __name__ == "__main__":
    test_extraction()