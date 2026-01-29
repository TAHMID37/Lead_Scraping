"""Debug script to inspect actual HTML structure of job cards"""
from scrapling.fetchers import StealthyFetcher
from bs4 import BeautifulSoup
import urllib.parse

def inspect_indeed_card():
    print("=" * 80)
    print("INSPECTING INDEED JOB CARD STRUCTURE")
    print("=" * 80)
    
    job_title = "ICT Project Manager"
    location = "Sydney-NSW"
    encoded_title = urllib.parse.quote(job_title)
    encoded_location = urllib.parse.quote(location)
    
    url = f"https://au.indeed.com/jobs?q={encoded_title}&l={encoded_location}&fromage=1&start=0"
    
    response = StealthyFetcher.fetch(
        url,
        headless=True,
        hide_canvas=True,
        block_webrtc=True,
        wait=2000,
        timeout=30000
    )
    
    soup = BeautifulSoup(response.html_content, 'html.parser')
    
    job_cards = soup.find_all('div', class_='job_seen_beacon')
    print(f"Found {len(job_cards)} job cards\n")
    
    if job_cards:
        card = job_cards[0]
        print("First job card HTML (first 2000 chars):")
        print(card.prettify()[:2000])
        print("\n" + "="*80)
        print("Checking for elements in first card:")
        
        # Check for title
        spans = card.find_all('span')
        print(f"  Number of spans: {len(spans)}")
        if spans:
            print(f"  First 3 spans text:")
            for i, span in enumerate(spans[:3]):
                text = span.get_text(strip=True)[:100]
                print(f"    {i}: {text}")
        
        # Check for links
        links = card.find_all('a')
        print(f"  Number of links: {len(links)}")
        if links:
            print(f"  First 3 links:")
            for i, link in enumerate(links[:3]):
                href = link.get('href', '')
                text = link.get_text(strip=True)[:50]
                print(f"    {i}: href={href[:100]}, text={text}")

def inspect_seek_card():
    print("\n" + "=" * 80)
    print("INSPECTING SEEK JOB CARD STRUCTURE")
    print("=" * 80)
    
    url = "https://www.seek.com.au/ict-project-manager-jobs/in-sydney-nsw"
    
    response = StealthyFetcher.fetch(
        url,
        headless=True,
        hide_canvas=True,
        block_webrtc=True,
        wait_selector='[data-automation="searchResults"]',
        wait=2000,
        timeout=45000
    )
    
    soup = BeautifulSoup(response.html_content, 'html.parser')
    
    job_cards = soup.find_all('article', attrs={'data-automation': 'normalJob'})
    print(f"Found {len(job_cards)} normalJob cards\n")
    
    if job_cards:
        card = job_cards[0]
        print("First job card HTML (first 2000 chars):")
        print(card.prettify()[:2000])
        print("\n" + "="*80)
        print("Checking for elements in first card:")
        
        # Check for data attributes
        print(f"  Card attributes: {card.attrs}")
        
        # Check for specific selectors from the scraper
        title_elem = card.find('a', attrs={'data-automation': 'jobTitle'})
        print(f"  jobTitle element found: {title_elem is not None}")
        if title_elem:
            print(f"    Text: {title_elem.get_text(strip=True)[:100]}")
        
        company_elem = card.find(attrs={'data-automation': 'jobCompany'})
        print(f"  jobCompany element found: {company_elem is not None}")
        if company_elem:
            print(f"    Text: {company_elem.get_text(strip=True)[:100]}")
        
        location_elem = card.find(attrs={'data-automation': 'jobLocation'})
        print(f"  jobLocation element found: {location_elem is not None}")
        if location_elem:
            print(f"    Text: {location_elem.get_text(strip=True)[:100]}")

def inspect_careerone_card():
    print("\n" + "=" * 80)
    print("INSPECTING CAREERONE JOB CARD STRUCTURE")
    print("=" * 80)
    
    url = "https://www.careerone.com.au/jobs/ict-project-manager/sydney"
    
    response = StealthyFetcher.fetch(
        url,
        headless=True,
        hide_canvas=True,
        block_webrtc=True,
        wait=2000,
        timeout=30000
    )
    
    soup = BeautifulSoup(response.html_content, 'html.parser')
    
    # Find divs with job-card class
    job_cards = soup.select('div[class*="job-card"]')
    print(f"Found {len(job_cards)} divs with 'job-card' in class\n")
    
    if job_cards:
        card = job_cards[0]
        print("First job card HTML (first 2000 chars):")
        print(card.prettify()[:2000])
        print("\n" + "="*80)
        print("Checking for elements in first card:")
        
        # Check for title
        title_elem = card.find(['h2', 'h3'])
        print(f"  h2/h3 element found: {title_elem is not None}")
        if title_elem:
            print(f"    HTML: {str(title_elem)[:200]}")
            print(f"    Text: {title_elem.get_text(strip=True)[:100]}")
        
        # Check for links
        links = card.find_all('a')
        print(f"  Number of links: {len(links)}")
        if links:
            print(f"  First link: href={links[0].get('href', '')[:100]}")

if __name__ == "__main__":
    inspect_indeed_card()
    inspect_seek_card()
    inspect_careerone_card()
