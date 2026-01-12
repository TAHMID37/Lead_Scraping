"""
Enhanced Indeed Australia Job Scraper with Configuration Support
Run this to use settings from config.py
"""

from indeed_scraper import IndeedScraper
import config


def main():
    """Main function using configuration from config.py"""
    
    print("="*60)
    print("Indeed Australia Job Scraper (Configured)")
    print("="*60)
    print(f"States: {', '.join(config.STATES_TO_SCRAPE)}")
    print(f"Time filter: Last {config.DAYS_POSTED} day(s)")
    print(f"Pages per state: {config.MAX_PAGES_PER_STATE}")
    if config.SEARCH_KEYWORD:
        print(f"Keyword: {config.SEARCH_KEYWORD}")
    print("="*60)
    
    # Create scraper instance
    scraper = IndeedScraper()
    
    # Override states if configured
    if config.STATES_TO_SCRAPE:
        # Filter STATES to only include configured ones
        scraper.STATES = {k: v for k, v in scraper.STATES.items() 
                         if k in config.STATES_TO_SCRAPE}
    
    # Scrape all configured states
    jobs = scraper.scrape_all_states(max_pages_per_state=config.MAX_PAGES_PER_STATE)
    
    # Print summary
    scraper.print_summary()
    
    # Save results with configured filenames
    scraper.save_to_json(config.JSON_OUTPUT)
    scraper.save_to_csv(config.CSV_OUTPUT)
    
    print("\n✅ Scraping completed successfully!")
    print(f"📁 Results saved to:")
    print(f"   - {config.JSON_OUTPUT}")
    print(f"   - {config.CSV_OUTPUT}")


if __name__ == "__main__":
    main()
