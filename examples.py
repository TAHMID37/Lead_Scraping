"""
Example script showing different ways to use the Indeed scraper
"""

from indeed_scraper import IndeedScraper


def example_1_basic_scraping():
    """Example 1: Basic scraping of all states"""
    print("\n" + "="*60)
    print("Example 1: Basic Scraping")
    print("="*60)
    
    scraper = IndeedScraper()
    jobs = scraper.scrape_all_states(max_pages_per_state=2)
    
    scraper.print_summary()
    scraper.save_to_json('example1_jobs.json')


def example_2_single_state():
    """Example 2: Scrape only one state"""
    print("\n" + "="*60)
    print("Example 2: Scraping NSW Only")
    print("="*60)
    
    scraper = IndeedScraper()
    nsw_jobs = scraper.scrape_state('NSW', max_pages=2)
    
    print(f"\nFound {len(nsw_jobs)} jobs in NSW")
    
    # Show first few jobs
    for i, job in enumerate(nsw_jobs[:3], 1):
        print(f"\n{i}. {job['job_title']}")
        print(f"   Company: {job['employer_name']}")
        print(f"   Posted: {job['posted_date']}")


def example_3_filter_results():
    """Example 3: Scrape and filter results"""
    print("\n" + "="*60)
    print("Example 3: Scraping and Filtering")
    print("="*60)
    
    scraper = IndeedScraper()
    all_jobs = scraper.scrape_all_states(max_pages_per_state=2)
    
    # Filter for jobs posted today
    today_jobs = [job for job in all_jobs if job['posted_date'].lower() == 'today']
    print(f"\nJobs posted today: {len(today_jobs)}")
    
    # Filter by keyword in title (case-insensitive)
    keyword = "engineer"
    keyword_jobs = [job for job in all_jobs 
                   if keyword.lower() in job['job_title'].lower()]
    print(f"Jobs with '{keyword}' in title: {len(keyword_jobs)}")
    
    # Group by state
    print("\nJobs by state:")
    for state in scraper.STATES.keys():
        state_jobs = [job for job in all_jobs if job['state'] == state]
        print(f"  {state}: {len(state_jobs)}")


def example_4_custom_processing():
    """Example 4: Custom data processing"""
    print("\n" + "="*60)
    print("Example 4: Custom Processing")
    print("="*60)
    
    scraper = IndeedScraper()
    jobs = scraper.scrape_all_states(max_pages_per_state=1)
    
    # Create a custom report
    report = {
        'total_jobs': len(jobs),
        'by_state': {},
        'companies': set(),
        'today_jobs': 0
    }
    
    for job in jobs:
        # Count by state
        state = job['state']
        report['by_state'][state] = report['by_state'].get(state, 0) + 1
        
        # Collect unique companies
        report['companies'].add(job['employer_name'])
        
        # Count today's jobs
        if job['posted_date'].lower() == 'today':
            report['today_jobs'] += 1
    
    print(f"\nCustom Report:")
    print(f"  Total jobs: {report['total_jobs']}")
    print(f"  Unique companies: {len(report['companies'])}")
    print(f"  Jobs posted today: {report['today_jobs']}")
    print(f"\n  Jobs by state:")
    for state, count in report['by_state'].items():
        print(f"    {state}: {count}")


if __name__ == "__main__":
    # Run the examples you want to test
    # Comment/uncomment as needed
    
    # Uncomment the example you want to run:
    
    example_1_basic_scraping()
    # example_2_single_state()
    # example_3_filter_results()
    # example_4_custom_processing()
