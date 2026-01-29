"""Debug script to test Indeed extraction"""
from scrapling.fetchers import StealthyFetcher
from bs4 import BeautifulSoup
import urllib.parse

def test_indeed_extraction():
    print("=" * 80)
    print("TESTING INDEED EXTRACTION")
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
    
    for i, card in enumerate(job_cards):
        print(f"\n--- Card {i+1} ---")
        
        # Try extracting title the new way
        title_elem = card.find('h2', class_='jobTitle')
        print(f"h2.jobTitle found: {title_elem is not None}")
        
        if title_elem:
            span = title_elem.find('span', attrs={'id': lambda x: x and 'jobTitle-' in x})
            if span:
                title = span.get_text(strip=True)
                print(f"  ✓ Title (from span): {title}")
            else:
                print(f"  ✗ Title span not found")
                print(f"    h2 content: {title_elem.get_text(strip=True)[:100]}")
        
        # Try company
        company_elem = card.find('span', attrs={'data-testid': 'company-name'})
        if company_elem:
            company = company_elem.get_text(strip=True)
            print(f"  ✓ Company: {company}")
        else:
            print(f"  ✗ Company not found")
        
        # Try location
        location_elem = card.find('div', attrs={'data-testid': 'text-location'})
        if location_elem:
            loc = location_elem.get_text(strip=True)
            print(f"  ✓ Location: {loc}")
        else:
            print(f"  ✗ Location not found")
        
        # Try URL
        link = card.find('a', class_='jcs-JobTitle')
        if link and 'href' in link.attrs:
            href = link['href']
            print(f"  ✓ URL found: {href[:80]}")
        else:
            print(f"  ✗ URL not found")

if __name__ == "__main__":
    test_indeed_extraction()
