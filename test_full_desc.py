"""
Quick test of the fixed scraper - just 3 jobs from NSW
"""

from scrapling.fetchers import DynamicFetcher
from datetime import datetime
import json

def test_full_descriptions():
    """Test that we get full descriptions now"""
    
    print("Testing full description extraction...\n")
    
    url = "https://au.indeed.com/jobs?q=&l=NSW&fromage=1&start=0"
    
    # Fetch listing page
    response = DynamicFetcher.fetch(url, headless=True, network_idle=True, load_dom=True)
    
    if response.status != 200:
        print(f"Failed to fetch listing page: {response.status}")
        return
    
    # Get first 3 job cards
    job_cards = response.css('div.job_seen_beacon')[:3]
    print(f"Found {len(job_cards)} jobs\n")
    
    for i, card in enumerate(job_cards, 1):
        # Extract basic info
        all_spans = card.css('span')
        job_title = all_spans[0].text.strip() if len(all_spans) > 0 and all_spans[0].text else None
        employer_name = all_spans[1].text.strip() if len(all_spans) > 1 and all_spans[1].text else None
        
        # Get job URL
        job_link = card.css_first('a')
        job_url = None
        if job_link and hasattr(job_link, 'attrib'):
            href = job_link.attrib.get('href')
            if href:
                job_url = f"https://au.indeed.com{href}" if not href.startswith('http') else href
        
        if not job_url:
            continue
        
        print(f"{i}. {job_title}")
        print(f"   Company: {employer_name}")
        print(f"   Fetching description from: {job_url[:80]}...")
        
        # Fetch job page
        try:
            job_response = DynamicFetcher.fetch(
                job_url,
                headless=True,
                network_idle=True,
                load_dom=True,
                wait_selector='#jobDescriptionText',
                wait=2000,
                timeout=45000
            )
            
            if job_response.status == 200:
                # Extract full description
                desc_elem = job_response.css_first('#jobDescriptionText')
                if desc_elem:
                    content_parts = []
                    paras = desc_elem.css('p, div, li')
                    for elem in paras:
                        text = elem.text
                        if text and len(text.strip()) > 15:
                            content_parts.append(text.strip())
                    
                    if content_parts:
                        description = '\\n'.join(content_parts)
                    else:
                        description = desc_elem.text.strip() if desc_elem.text else "No description"
                    
                    print(f"   ✓ Description length: {len(description)} characters")
                    print(f"   Preview: {description[:200]}...")
                    print(f"   Full text has {len(content_parts)} parts")
                else:
                    print(f"   ✗ No description element found")
            else:
                print(f"   ✗ Failed to fetch job page: {job_response.status}")
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_full_descriptions()
