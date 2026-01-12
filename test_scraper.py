"""
Test script to debug Indeed scraper and check HTML structure
"""

from indeed_scraper import IndeedScraper

def test_single_page():
    """Test scraping a single page with debug output"""
    print("Testing Indeed scraper with debug mode...\n")
    
    scraper = IndeedScraper(debug=True)
    
    # Test with just NSW, 1 page
    jobs = scraper.scrape_state('NSW', max_pages=1)
    
    print(f"\n{'='*60}")
    print(f"Test Results:")
    print(f"{'='*60}")
    print(f"Total jobs found: {len(jobs)}")
    
    if jobs:
        print(f"\nFirst job details:")
        job = jobs[0]
        for key, value in job.items():
            print(f"  {key}: {value}")
        
        # Check what's missing
        print(f"\nData quality check:")
        desc_count = sum(1 for j in jobs if j['job_description'] and j['job_description'] != 'No description available')
        date_count = sum(1 for j in jobs if j['posted_date'] != 'Unknown')
        
        print(f"  Jobs with descriptions: {desc_count}/{len(jobs)}")
        print(f"  Jobs with dates: {date_count}/{len(jobs)}")
    else:
        print("No jobs found!")

if __name__ == "__main__":
    test_single_page()
