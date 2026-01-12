"""
Test fetching a single job description to see the page structure
"""

from scrapling.fetchers import StealthyFetcher

def test_job_page():
    """Test fetching a job page"""
    # Use a real Indeed job URL
    job_url = "https://au.indeed.com/viewjob?jk=97993b025c805462&from=serp&vjs=3"
    
    print(f"Fetching job page: {job_url}\n")
    
    response = StealthyFetcher.fetch(job_url, headless=True, network_idle=True)
    
    print(f"Status: {response.status}\n")
    
    if response.status == 200:
        # Try different selectors for description
        selectors = [
            '#jobDescriptionText',
            '[id*="jobDescription"]',
            '.jobsearch-jobDescriptionText',
            'div[class*="jobDescription"]',
            'div[id*="job-description"]',
            'div.jobsearch-JobComponent-description',
        ]
        
        for selector in selectors:
            elements = response.css(selector)
            if elements:
                print(f"✓ Found {len(elements)} elements with: {selector}")
                elem = elements[0]
                text = elem.text if elem.text else 'no-text'
                print(f"  Text length: {len(text)}")
                print(f"  Preview: {text[:200]}\n")
            else:
                print(f"✗ No elements found with: {selector}")
        
        # Look for any divs that might contain description
        print("\nLooking for description-like divs:")
        all_divs = response.css('div')
        for div in all_divs[:50]:
            if hasattr(div, 'attrib'):
                div_id = div.attrib.get('id', '')
                div_class = div.attrib.get('class', '')
                
                if 'description' in div_id.lower() or 'description' in div_class.lower():
                    text = div.text[:100] if div.text else 'no-text'
                    print(f"  ID: {div_id}, Class: {div_class}")
                    print(f"    Text: {text}\n")

if __name__ == "__main__":
    test_job_page()
