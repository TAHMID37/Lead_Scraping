"""
Indeed Australia Job Scraper using Scrapling
Scrapes job listings from QLD, NSW, WA, and SA
Filters for jobs posted within the last 24 hours
"""

from scrapling.fetchers import StealthyFetcher
from datetime import datetime
import json
import time


class IndeedScraper:
    """Scraper for Indeed Australia job listings"""
    
    # Australian states to scrape
    STATES = {
        'QLD': 'Queensland',
        'NSW': 'New South Wales',
        'WA': 'Western Australia',
        'SA': 'South Australia'
    }
    
    BASE_URL = 'https://au.indeed.com'
    
    def __init__(self, debug=False):
        """Initialize the scraper"""
        self.jobs = []
        self.debug = debug
        
    def build_search_url(self, state_code, page=0):
        """
        Build Indeed search URL with filters
        
        Args:
            state_code: State code (QLD, NSW, WA, SA)
            page: Page number for pagination
            
        Returns:
            Complete search URL with filters
        """
        # Indeed uses 'fromage=1' for last 24 hours
        # 'l=' for location
        # 'start=' for pagination (increments by 10)
        url = f"{self.BASE_URL}/jobs?q=&l={state_code}&fromage=1&start={page * 10}"
        return url
    
    def parse_posted_date(self, date_text):
        """
        Parse the posted date text from Indeed
        
        Args:
            date_text: Raw date text from Indeed (e.g., "Just posted", "1 day ago")
            
        Returns:
            Parsed date string
        """
        if not date_text:
            return "Unknown"
        
        date_text = date_text.strip().lower()
        
        # Handle different date formats
        if 'just posted' in date_text or 'today' in date_text:
            return "Today"
        elif '1 day' in date_text or 'yesterday' in date_text:
            return "Yesterday"
        else:
            return date_text.capitalize()
    
    def scrape_job_card(self, job_card, fetch_description=False, response=None):
        """
        Extract job details from a job card element
        
        Args:
            job_card: Scrapling element containing job card
            fetch_description: If True, clicks job to get full description
            response: The page response object (needed for clicking)
            
        Returns:
            Dictionary with job details or None if parsing fails
        """
        try:
            # Extract job title - get all spans and find the one with job title
            job_title = None
            all_spans = job_card.css('span')
            if all_spans and len(all_spans) >= 1:
                # First span is usually the job title
                job_title = all_spans[0].text.strip() if all_spans[0].text else None
            
            # Fallback title selectors
            if not job_title:
                title_elem = job_card.css_first('h2 span[title]')
                if not title_elem:
                    title_elem = job_card.css_first('h2 a span')
                if not title_elem:
                    title_elem = job_card.css_first('a[id*="job"] span')
                job_title = title_elem.text.strip() if title_elem and title_elem.text else None
            
            # Extract company name
            employer_name = None
            company_elem = job_card.css_first('span[data-testid="company-name"]')
            if not company_elem:
                company_elem = job_card.css_first('.companyName')
            if not company_elem:
                # Second span is often the company name
                if all_spans and len(all_spans) >= 2:
                    employer_name = all_spans[1].text.strip()
            if not employer_name and company_elem:
                employer_name = company_elem.text.strip() if company_elem.text else None
            
            # Extract job description
            # Indeed loads descriptions dynamically, so they're not in the initial card
            # We note this in the output
            job_description = "Description not loaded (Indeed loads this dynamically when clicking the job)"
            
            # If fetch_description is True and we have a browser session, click to get description
            # For now, we'll just note that descriptions aren't available without interaction
            if fetch_description and response:
                # This would require keeping browser session open and clicking each job
                # which is very slow. We'll document this limitation.
                pass
            
            # Extract location
            location_elem = job_card.css_first('div[data-testid="text-location"]')
            if not location_elem:
                location_elem = job_card.css_first('.companyLocation')
            if not location_elem:
                location_elem = job_card.css_first('div[class*="location"]')
            if not location_elem:
                # Try finding by class pattern
                location_divs = job_card.css('div[class*="css-"]')
                for div in location_divs:
                    text = div.text if div.text else ''
                    # Check if it looks like a location (contains state/postcode)
                    if any(state in text for state in ['NSW', 'QLD', 'VIC', 'SA', 'WA', 'NT', 'ACT', 'TAS']):
                        location_elem = div
                        break
            location = location_elem.text.strip() if location_elem and location_elem.text else None
            
            # Extract posted date - Indeed often doesn't show this in listing view
            posted_date = "Not available in listing view"
            # Try to find date info
            date_elem = job_card.css_first('span.date')
            if not date_elem:
                date_elem = job_card.css_first('span[data-testid="myJobsStateDate"]')
            if not date_elem:
                date_elem = job_card.css_first('time')
            if date_elem and date_elem.text:
                posted_date = self.parse_posted_date(date_elem.text)
            
            # Extract job URL
            job_link = job_card.css_first('a[id*="job"]')
            if not job_link:
                job_link = job_card.css_first('h2 a')
            if not job_link:
                job_link = job_card.css_first('a')
            
            job_url = None
            if job_link and hasattr(job_link, 'attrib'):
                href = job_link.attrib.get('href')
                if href:
                    if href.startswith('http'):
                        job_url = href
                    else:
                        job_url = f"{self.BASE_URL}{href}"
            
            # Only return if we have at least title and company
            if job_title and employer_name:
                return {
                    'job_title': job_title,
                    'employer_name': employer_name,
                    'job_description': job_description,
                    'posted_date': posted_date,
                    'location': location,
                    'job_url': job_url,
                    'scraped_at': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            if self.debug:
                print(f"  DEBUG - Error parsing job card: {e}")
            return None
            
            # Extract location for verification
            location_elem = job_card.css_first('div[data-testid="text-location"]')
            if not location_elem:
                location_elem = job_card.css_first('.companyLocation')
            location = location_elem.text.strip() if location_elem else None
            
            # Extract job URL
            job_link = job_card.css_first('h2.jobTitle a')
            job_url = f"{self.BASE_URL}{job_link.attrib.get('href')}" if job_link and job_link.attrib.get('href') else None
            
            # Only return if we have at least title and company
            if job_title and employer_name:
                return {
                    'job_title': job_title,
                    'employer_name': employer_name,
                    'job_description': job_description if job_description else "No description available",
                    'posted_date': posted_date,
                    'location': location,
                    'job_url': job_url,
                    'scraped_at': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"Error parsing job card: {e}")
            return None
    
    def scrape_state(self, state_code, max_pages=3, fetch_descriptions=False):
        """
        Scrape jobs from a specific Australian state
        
        Args:
            state_code: State code (QLD, NSW, WA, SA)
            max_pages: Maximum number of pages to scrape per state
            fetch_descriptions: If True, will click on each job to get full description (slower)
            
        Returns:
            List of job dictionaries
        """
        state_jobs = []
        state_name = self.STATES.get(state_code, state_code)
        
        print(f"\nScraping jobs from {state_name} ({state_code})...")
        if not fetch_descriptions:
            print(f"  Note: Descriptions require clicking each job (slow). Run with fetch_descriptions=True for full details.")
        
        for page in range(max_pages):
            try:
                url = self.build_search_url(state_code, page)
                print(f"  Fetching page {page + 1}: {url}")
                
                # Use StealthyFetcher to bypass anti-bot protection
                # headless=True for faster scraping, network_idle=True to wait for content
                response = StealthyFetcher.fetch(
                    url,
                    headless=True,
                    network_idle=True
                )
                
                if response.status != 200:
                    print(f"  Warning: Got status {response.status} for {url}")
                    continue
                
                # Find all job cards
                job_cards = response.css('div.job_seen_beacon')
                if not job_cards:
                    # Try alternative selector
                    job_cards = response.css('div.cardOutline')
                if not job_cards:
                    # Try another alternative
                    job_cards = response.css('div[class*="jobsearch"]')
                
                print(f"  Found {len(job_cards)} job cards on page {page + 1}")
                
                if len(job_cards) == 0:
                    print(f"  No more jobs found for {state_code}, stopping pagination")
                    break
                
                # Parse each job card
                page_jobs_count = 0
                for i, card in enumerate(job_cards, 1):
                    if self.debug and i == 1:
                        print(f"\n  DEBUG - First job card structure:")
                        print(f"  Card text preview: {card.text[:300]}")
                    
                    job_data = self.scrape_job_card(card, fetch_description=fetch_descriptions, response=response)
                    if job_data:
                        job_data['state'] = state_code
                        state_jobs.append(job_data)
                        page_jobs_count += 1
                
                print(f"  Successfully parsed {page_jobs_count} jobs from page {page + 1}")
                
                # Be respectful - add delay between pages
                time.sleep(2)
                
            except Exception as e:
                print(f"  Error scraping page {page + 1} for {state_code}: {e}")
                continue
        
        print(f"Total jobs scraped from {state_name}: {len(state_jobs)}")
        return state_jobs
    
    def scrape_all_states(self, max_pages_per_state=3):
        """
        Scrape jobs from all specified Australian states
        
        Args:
            max_pages_per_state: Maximum pages to scrape per state
            
        Returns:
            List of all jobs from all states
        """
        print("="*60)
        print("Indeed Australia Job Scraper")
        print("States: QLD, NSW, WA, SA")
        print("Filter: Last 24 hours only")
        print("="*60)
        
        all_jobs = []
        
        for state_code in self.STATES.keys():
            state_jobs = self.scrape_state(state_code, max_pages_per_state)
            all_jobs.extend(state_jobs)
            
            # Delay between states to be respectful
            time.sleep(3)
        
        self.jobs = all_jobs
        return all_jobs
    
    def save_to_json(self, filename='indeed_jobs.json'):
        """
        Save scraped jobs to JSON file
        
        Args:
            filename: Output filename
        """
        if not self.jobs:
            print("No jobs to save!")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"Saved {len(self.jobs)} jobs to {filename}")
        print(f"{'='*60}")
    
    def save_to_csv(self, filename='indeed_jobs.csv'):
        """
        Save scraped jobs to CSV file
        
        Args:
            filename: Output filename
        """
        if not self.jobs:
            print("No jobs to save!")
            return
        
        import csv
        
        # Define CSV columns
        fieldnames = ['job_title', 'employer_name', 'job_description', 
                     'posted_date', 'state', 'location', 'job_url', 'scraped_at']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for job in self.jobs:
                writer.writerow(job)
        
        print(f"Saved {len(self.jobs)} jobs to {filename}")
    
    def print_summary(self):
        """Print a summary of scraped jobs"""
        if not self.jobs:
            print("\nNo jobs scraped!")
            return
        
        print(f"\n{'='*60}")
        print(f"SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total jobs scraped: {len(self.jobs)}")
        
        # Jobs by state
        print("\nJobs by state:")
        for state in self.STATES.keys():
            state_count = len([j for j in self.jobs if j.get('state') == state])
            print(f"  {state}: {state_count}")
        
        # Sample jobs
        print(f"\nSample jobs (first 3):")
        for i, job in enumerate(self.jobs[:3], 1):
            print(f"\n{i}. {job['job_title']}")
            print(f"   Company: {job['employer_name']}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Posted: {job['posted_date']}")
            print(f"   State: {job['state']}")


def main():
    """Main function to run the scraper"""
    scraper = IndeedScraper()
    
    # Scrape jobs from all states (max 3 pages per state)
    # You can adjust max_pages_per_state as needed
    jobs = scraper.scrape_all_states(max_pages_per_state=3)
    
    # Print summary
    scraper.print_summary()
    
    # Save to both JSON and CSV
    scraper.save_to_json('indeed_jobs.json')
    scraper.save_to_csv('indeed_jobs.csv')
    
    print("\nScraping completed successfully!")


if __name__ == "__main__":
    main()
