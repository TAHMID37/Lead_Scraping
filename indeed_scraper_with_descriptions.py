"""
Enhanced Indeed scraper that fetches full job descriptions by visiting each job page
"""

from scrapling.fetchers import StealthyFetcher
from datetime import datetime
import json
import time


class IndeedScraperWithDescriptions:
    """Enhanced scraper that fetches full job descriptions"""
    
    STATES = {
        'QLD': 'Queensland',
        # 'NSW': 'New South Wales',
        # 'WA': 'Western Australia',
        # 'SA': 'South Australia'
    }
    
    BASE_URL = 'https://au.indeed.com'
    
    def __init__(self):
        self.jobs = []
    
    def build_search_url(self, state_code, page=0):
        """Build Indeed search URL"""
        url = f"{self.BASE_URL}/jobs?q=&l={state_code}&fromage=1&start={page * 1}"
        return url
    
    def fetch_job_description(self, job_url):
        """
        Fetch full job description from individual job page
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Tuple of (description, posted_date)
        """
        try:
            # Fetch with longer timeout and wait for content to load
            response = StealthyFetcher.fetch(
                job_url, 
                headless=True, 
                network_idle=True,
                wait_selector='#jobDescriptionText',  # Wait for description element
                timeout=45000  # 45 second timeout
            )
            
            if response.status == 200:
                # Wait a bit more for JS to populate content
                import time
                time.sleep(2)
                
                # Re-fetch to get updated content
                response = StealthyFetcher.fetch(
                    job_url, 
                    headless=True,
                    network_idle=True
                )
                
                # Extract description - try multiple approaches
                description = None
                
                # Try getting all paragraph text
                paragraphs = response.css('#jobDescriptionText p, #jobDescriptionText div, #jobDescriptionText li')
                if paragraphs:
                    desc_parts = []
                    for p in paragraphs:
                        if p.text and len(p.text.strip()) > 10:
                            desc_parts.append(p.text.strip())
                    if desc_parts:
                        description = ' '.join(desc_parts[:10])  # First 10 paragraphs
                
                # Fallback: get all text content
                if not description or description == '':
                    desc_container = response.css_first('#jobDescriptionText')
                    if desc_container:
                        # Get all text nodes
                        all_text = desc_container.text
                        if all_text and len(all_text.strip()) > 20:
                            description = all_text.strip()
                
                # Another fallback: look for any job description div
                if not description or description == '':
                    desc_divs = response.css('div[class*="description"], div[id*="description"]')
                    for div in desc_divs:
                        text = div.text
                        if text and len(text.strip()) > 50:
                            description = text.strip()
                            break
                
                if not description or description == '':
                    description = "Description could not be extracted (content may be dynamically loaded)"
                
                # Extract posted date
                posted_date = "Unknown"
                date_indicators = response.css('[class*="date"], [class*="Date"], time, [data-testid*="date"]')
                for elem in date_indicators:
                    text = elem.text if elem.text else ''
                    if any(word in text.lower() for word in ['posted', 'ago', 'day', 'hour', 'today']):
                        posted_date = text.strip()
                        break
                
                return description[:500] if len(description) > 500 else description, posted_date
            
            return "Failed to fetch description (non-200 status)", "Unknown"
            
        except Exception as e:
            print(f"    Error fetching job description: {e}")
            return f"Error: {str(e)[:100]}", "Unknown"
    
    def scrape_state(self, state_code, max_pages=2):
        """Scrape jobs from a state with full descriptions"""
        state_jobs = []
        state_name = self.STATES.get(state_code, state_code)
        
        print(f"\nScraping jobs from {state_name} ({state_code}) with full descriptions...")
        print(f"  This will be slower as each job page is visited individually.")
        
        for page in range(max_pages):
            try:
                url = self.build_search_url(state_code, page)
                print(f"\n  Fetching page {page + 1}: {url}")
                
                response = StealthyFetcher.fetch(url, headless=True, network_idle=True)
                
                if response.status != 200:
                    print(f"  Warning: Got status {response.status}")
                    continue
                
                # Find job cards
                job_cards = response.css('div.job_seen_beacon')
                print(f"  Found {len(job_cards)} jobs on page {page + 1}")
                
                if len(job_cards) == 0:
                    break
                
                # Process each job
                for i, card in enumerate(job_cards, 1):
                    try:
                        # Extract basic info
                        all_spans = card.css('span')
                        job_title = all_spans[0].text.strip() if len(all_spans) > 0 and all_spans[0].text else None
                        employer_name = all_spans[1].text.strip() if len(all_spans) > 1 and all_spans[1].text else None
                        
                        # Get location
                        location_divs = card.css('div[class*="css-"]')
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
                            print(f"    {i}. Fetching description for: {job_title[:50]}...")
                            
                            # Fetch full description
                            description, posted_date = self.fetch_job_description(job_url)
                            
                            job_data = {
                                'job_title': job_title,
                                'employer_name': employer_name,
                                'job_description': description[:500] if len(description) > 500 else description,  # Limit length
                                'posted_date': posted_date,
                                'location': location,
                                'job_url': job_url,
                                'state': state_code,
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            state_jobs.append(job_data)
                            
                            # Small delay between individual job fetches
                            time.sleep(1)
                    
                    except Exception as e:
                        print(f"    Error processing job {i}: {e}")
                        continue
                
                # Delay between pages
                time.sleep(2)
                
            except Exception as e:
                print(f"  Error on page {page + 1}: {e}")
                continue
        
        print(f"\nTotal jobs scraped from {state_name}: {len(state_jobs)}")
        return state_jobs
    
    def scrape_all_states(self, max_pages_per_state=2):
        """Scrape all states with full descriptions"""
        print("="*60)
        print("Indeed Australia Job Scraper (WITH DESCRIPTIONS)")
        print("States: QLD, NSW, WA, SA")
        print("Filter: Last 24 hours only")
        print("="*60)
        
        all_jobs = []
        
        for state_code in self.STATES.keys():
            state_jobs = self.scrape_state(state_code, max_pages_per_state)
            all_jobs.extend(state_jobs)
            time.sleep(3)
        
        self.jobs = all_jobs
        return all_jobs
    
    def save_to_json(self, filename='indeed_jobs_with_descriptions.json'):
        """Save to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(self.jobs)} jobs to {filename}")
    
    def save_to_csv(self, filename='indeed_jobs_with_descriptions.csv'):
        """Save to CSV"""
        import csv
        fieldnames = ['job_title', 'employer_name', 'job_description', 
                     'posted_date', 'state', 'location', 'job_url', 'scraped_at']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for job in self.jobs:
                writer.writerow(job)
        print(f"Saved {len(self.jobs)} jobs to {filename}")


def main():
    """Run the enhanced scraper"""
    scraper = IndeedScraperWithDescriptions()
    
    # Scrape 2 pages per state (slower but with full descriptions)
    jobs = scraper.scrape_all_states(max_pages_per_state=1)
    
    # Save results
    scraper.save_to_json()
    scraper.save_to_csv()
    
    print("\n" + "="*60)
    print(f"Scraping complete! Found {len(jobs)} jobs with descriptions.")
    print("="*60)


if __name__ == "__main__":
    main()
