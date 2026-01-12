"""
Indeed scraper using DynamicFetcher to properly load job descriptions
This should work much better for dynamic content!
"""

from scrapling.fetchers import StealthyFetcher
from datetime import datetime
from playwright.sync_api import Page
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
import random


class IndeedDynamicScraper:
    """Scraper using StealthyFetcher for better JavaScript handling"""
    
    def __init__(self, max_workers=3):
        self.jobs = []
        self.max_workers = max_workers
        self.STATES = {
            # 'QLD': 'Queensland',
            'NSW': 'New South Wales',
            # 'WA': 'Western Australia',
            # 'SA': 'South Australia'
        }
        self.BASE_URL = 'https://au.indeed.com'
        self.STATES = {
            # 'QLD': 'Queensland',
            'NSW': 'New South Wales',
            # 'WA': 'Western Australia',
            # 'SA': 'South Australia'
        }
        self.BASE_URL = 'https://au.indeed.com'
    
    def build_search_url(self, state_code, page=0):
        """Build Indeed search URL"""
        url = f"{self.BASE_URL}/jobs?q=&l={state_code}&fromage=1&start={page * 1}"
        return url
    
    def process_single_job(self, job_info):
        """Process a single job (for parallel execution)"""
        try:
            # Add small random delay to avoid hammering the server
            time.sleep(random.random() * 2)
            
            description, posted_date = self.fetch_job_with_description(job_info['url'])
            
            return {
                'job_title': job_info['title'],
                'employer_name': job_info['employer'],
                'location': job_info['location'],
                'job_description': description,
                'posted_date': posted_date,
                'state': job_info['state'],
                'url': job_info['url'],
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            return None
    
    def fetch_job_with_description(self, job_url):
        """
        Fetch job page and get description using StealthyFetcher
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Tuple of (description, posted_date)
        """
        try:
            # Define human-like page actions
            def human_behavior(page: Page):
                """Simulate human browsing behavior - faster version"""
                try:
                    # Quick mouse movement
                    page.mouse.move(100 + int(random.random() * 300), 100 + int(random.random() * 300))
                    page.wait_for_timeout(100)
                    
                    # Quick scroll down
                    for i in range(2):
                        page.evaluate('window.scrollBy(0, 300)')
                        page.wait_for_timeout(200)
                    
                    # Brief pause
                    page.wait_for_timeout(300)
                    
                    # Scroll back up
                    page.evaluate('window.scrollBy(0, -200)')
                except Exception:
                    pass  # Ignore errors in human behavior
            
            # Use StealthyFetcher with stealth options and human-like behavior
            response = StealthyFetcher.fetch(
                job_url,
                headless=True,
                hide_canvas=True,  # Add random noise to prevent fingerprinting
                block_webrtc=True,  # Prevent WebRTC leaks
                network_idle=False,  # Don't wait for network idle (can hang on some pages)
                load_dom=True,  # Wait for JavaScript to execute
                wait_selector='#jobDescriptionText',  # Wait for description element
                wait=1500,  # Wait 1.5 seconds after everything loads
                timeout=90000,  # 90 second timeout (some pages redirect multiple times)
                page_action=human_behavior  # Add human-like behavior
            )
            
            if response.status == 200:
                # Now extract description - content should be loaded
                description = None
                
                # Try to get all text from description container with proper structure
                desc_elem = response.css_first('#jobDescriptionText')
                if desc_elem:
                    # Get the FULL inner HTML to preserve all structure
                    description = desc_elem.get_all_text(separator='\n', strip=True)
                    
                    # If that didn't work, try getting the raw text
                    if not description or len(description) < 50:
                        description = desc_elem.text.strip() if desc_elem.text else None
                
                # Another fallback
                if not description or len(description) < 50:
                    all_desc_divs = response.css('div[id*="jobDescription"], div[class*="jobDescription"]')
                    for div in all_desc_divs:
                        text = div.get_all_text(separator='\n', strip=True)
                        if text and len(text.strip()) > 50:
                            description = text.strip()
                            break
                
                if not description or description == '':
                    description = "Description not available"
                
                # Extract posted date
                posted_date = "Unknown"
                # Look for date metadata
                date_elements = response.css('[class*="date"], [class*="Date"], time, span')
                for elem in date_elements:
                    text = elem.text if elem.text else ''
                    text_lower = text.lower()
                    if any(word in text_lower for word in ['posted', 'ago', 'day', 'hour', 'today', 'yesterday']):
                        if len(text) < 50:  # Make sure it's not a long paragraph
                            posted_date = text.strip()
                            break
                
                return description, posted_date  # Return full description without truncation
            
            return f"Failed to load page (status {response.status})", "Unknown"
            
        except Exception as e:
            return f"Error: {str(e)[:100]}", "Unknown"
    
    def scrape_state(self, state_code, max_pages=2):
        """Scrape jobs from a state"""
        state_jobs = []
        state_name = self.STATES.get(state_code, state_code)
        
        print(f"\nScraping jobs from {state_name} ({state_code}) with descriptions...")
        print(f"  Using StealthyFetcher with anti-bot protection.")
        
        for page in range(max_pages):
            try:
                url = self.build_search_url(state_code, page)
                print(f"\n  Fetching page {page + 1}: {url}")
                
                # Use StealthyFetcher for listing page with simpler settings
                response = StealthyFetcher.fetch(
                    url,
                    headless=True,
                    timeout=45000,  # 45 second timeout
                    hide_canvas=True,
                    block_webrtc=True
                )
                
                if response.status != 200:
                    print(f"  Warning: Got status {response.status}")
                    continue
                
                # Find job cards
                job_cards = response.css('div.job_seen_beacon')
                print(f"  Found {len(job_cards)} jobs on page {page + 1}")
                
                if len(job_cards) == 0:
                    break
                
                # Extract basic job info from all cards first
                job_infos = []
                for i, card in enumerate(job_cards, 1):
                    try:
                        # Extract basic info from listing
                        all_spans = card.css('span')
                        job_title = all_spans[0].text.strip() if len(all_spans) > 0 and all_spans[0].text else None
                        employer_name = all_spans[1].text.strip() if len(all_spans) > 1 and all_spans[1].text else None
                        
                        # Get location
                        location_divs = card.css('div')
                        location = None
                        for div in location_divs:
                            text = div.text if div.text else ''
                            if any(state in text for state in ['NSW', 'QLD', 'VIC', 'SA', 'WA', 'NT', 'ACT', 'TAS']):
                                location = text.strip()
                                break
                        
                        # Get job URL
                        job_link = card.css_first('a')
                        job_url = None
                        if job_link and hasattr(job_link, 'attrib'):
                            href = job_link.attrib.get('href')
                            if href:
                                job_url = f"{self.BASE_URL}{href}" if not href.startswith('http') else href
                        
                        if job_title and employer_name and job_url:
                            job_infos.append({
                                'index': i,
                                'title': job_title,
                                'employer': employer_name,
                                'location': location,
                                'url': job_url,
                                'state': state_code
                            })
                    except Exception as e:
                        print(f"    ✗ Error extracting job {i}: {e}")
                
                # Process jobs in parallel
                print(f"  Processing {len(job_infos)} jobs in parallel (max {self.max_workers} workers)...")
                
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    # Submit all jobs
                    future_to_job = {
                        executor.submit(self.process_single_job, job_info): job_info
                        for job_info in job_infos
                    }
                    
                    # Collect results as they complete
                    for future in as_completed(future_to_job):
                        job_info = future_to_job[future]
                        try:
                            job_data = future.result()
                            if job_data:
                                state_jobs.append(job_data)
                                desc_len = len(job_data['job_description'])
                                print(f"    ✓ [{job_info['index']}] {job_info['title'][:50]} - {desc_len} chars")
                        except Exception as e:
                            print(f"    ✗ [{job_info['index']}] {job_info['title'][:50]} - {str(e)[:60]}")
                
                # Random delay between pages (3-6 seconds)
                page_delay = 3 + random.random() * 3
                time.sleep(page_delay)
                
            except Exception as e:
                print(f"  ✗ Error on page {page + 1}: {e}")
                continue
        
        print(f"\nTotal jobs scraped from {state_name}: {len(state_jobs)}")
        return state_jobs
    
    def scrape_all_states(self, max_pages_per_state=1):
        """Scrape all states"""
        print("="*70)
        print("Indeed Australia Job Scraper - WITH DESCRIPTIONS")
        print("Using DynamicFetcher for better JavaScript content handling")
        print("States: QLD, NSW, WA, SA | Filter: Last 24 hours")
        print("="*70)
        
        all_jobs = []
        
        for state_code in self.STATES.keys():
            state_jobs = self.scrape_state(state_code, max_pages_per_state)
            all_jobs.extend(state_jobs)
            time.sleep(3)
        
        self.jobs = all_jobs
        return all_jobs
    
    def save_to_json(self, filename='indeed_jobs_dynamic.json'):
        """Save to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved {len(self.jobs)} jobs to {filename}")
    
    def save_to_csv(self, filename='indeed_jobs_dynamic.csv'):
        """Save to CSV"""
        import csv
        fieldnames = ['job_title', 'employer_name', 'job_description', 
                     'posted_date', 'state', 'location', 'url', 'scraped_at']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for job in self.jobs:
                writer.writerow(job)
        print(f"✓ Saved {len(self.jobs)} jobs to {filename}")
    
    def print_summary(self):
        """Print summary"""
        if not self.jobs:
            print("\n✗ No jobs scraped!")
            return
        
        print(f"\n{'='*70}")
        print(f"SCRAPING SUMMARY")
        print(f"{'='*70}")
        print(f"Total jobs: {len(self.jobs)}")
        
        # Count descriptions
        with_desc = sum(1 for j in self.jobs 
                       if j['job_description'] and 
                       'not available' not in j['job_description'].lower() and
                       'error' not in j['job_description'].lower())
        
        print(f"Jobs with descriptions: {with_desc}/{len(self.jobs)}")
        
        # By state
        print(f"\nJobs by state:")
        for state in self.STATES.keys():
            count = len([j for j in self.jobs if j['state'] == state])
            print(f"  {state}: {count}")
        
        # Sample
        if self.jobs:
            print(f"\nSample job:")
            job = self.jobs[0]
            print(f"  Title: {job['job_title']}")
            print(f"  Company: {job['employer_name']}")
            print(f"  Description: {job['job_description'][:150]}...")
            print(f"  Posted: {job['posted_date']}")


def main():
    """Run the scraper"""
    scraper = IndeedDynamicScraper()
    
    # Scrape 1 page per state (you can increase this)
    jobs = scraper.scrape_all_states(max_pages_per_state=1)
    
    # Print summary
    scraper.print_summary()
    
    # Save results
    scraper.save_to_json()
    scraper.save_to_csv()
    
    print("\n" + "="*70)
    print(f"✓ Scraping complete!")
    print("="*70)


if __name__ == "__main__":
    main()
