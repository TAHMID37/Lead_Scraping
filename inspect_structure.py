"""
Advanced test to inspect Indeed's actual HTML structure
"""

from scrapling.fetchers import StealthyFetcher

def inspect_indeed_page():
    """Fetch a page and inspect the actual structure"""
    print("Fetching Indeed page to inspect structure...\n")
    
    url = "https://au.indeed.com/jobs?q=&l=NSW&fromage=1&start=0"
    
    response = StealthyFetcher.fetch(url, headless=True, network_idle=True)
    
    if response.status == 200:
        print(f"✓ Successfully fetched page (status: {response.status})")
        
        # Try to find job cards with different selectors
        selectors_to_try = [
            'div.job_seen_beacon',
            'div.cardOutline',
            'div[class*="jobsearch"]',
            'li[class*="job"]',
            'div[data-jk]',
            'td.resultContent'
        ]
        
        for selector in selectors_to_try:
            cards = response.css(selector)
            if cards:
                print(f"\n✓ Found {len(cards)} elements with selector: {selector}")
                
                # Inspect first card
                if cards:
                    card = cards[0]
                    print(f"\nFirst card attributes:")
                    if hasattr(card, 'attrib'):
                        for key, value in list(card.attrib.items())[:5]:
                            print(f"  {key}: {value[:100] if len(value) > 100 else value}")
                    
                    # Try to find elements within the card
                    print(f"\nLooking for elements within first card:")
                    
                    # Title
                    titles = card.css('h2, a[id*="job"], span[title]')
                    if titles:
                        print(f"  Titles found: {len(titles)}")
                        print(f"    First title text: {titles[0].text[:100]}")
                    
                    # Company
                    companies = card.css('[data-testid="company-name"], .companyName, span[class*="company"]')
                    if companies:
                        print(f"  Companies found: {len(companies)}")
                        print(f"    First company text: {companies[0].text[:100]}")
                    
                    # Description
                    descriptions = card.css('.job-snippet, div[class*="snippet"], li, p')
                    if descriptions:
                        print(f"  Description elements found: {len(descriptions)}")
                        if descriptions[0].text:
                            print(f"    First desc text: {descriptions[0].text[:100]}")
                    
                    # Date
                    dates = card.css('span.date, span[class*="date"], time')
                    if dates:
                        print(f"  Date elements found: {len(dates)}")
                        print(f"    First date text: {dates[0].text}")
                    
                    # All spans (to find date)
                    all_spans = card.css('span')
                    print(f"  Total spans in card: {len(all_spans)}")
                    if len(all_spans) <= 20:
                        for i, span in enumerate(all_spans):
                            text = span.text.strip()
                            if text and len(text) < 50:
                                print(f"    Span {i}: '{text}'")
                
                break
    else:
        print(f"✗ Failed to fetch page (status: {response.status})")

if __name__ == "__main__":
    inspect_indeed_page()
