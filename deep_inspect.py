"""
Deep inspection of Indeed job card structure to find description
"""

from scrapling.fetchers import StealthyFetcher

def deep_inspect():
    """Deep dive into job card structure"""
    print("Deep inspection of Indeed job cards...\n")
    
    url = "https://au.indeed.com/jobs?q=&l=NSW&fromage=1&start=0"
    response = StealthyFetcher.fetch(url, headless=True, network_idle=True)
    
    if response.status == 200:
        cards = response.css('div.job_seen_beacon')
        
        if cards:
            print(f"Found {len(cards)} job cards\n")
            print("="*80)
            print("INSPECTING FIRST JOB CARD IN DETAIL")
            print("="*80)
            
            card = cards[0]
            
            # Get all child elements
            print("\n1. ALL DIVS in card:")
            divs = card.css('div')
            for i, div in enumerate(divs[:10]):
                classes = div.attrib.get('class', 'no-class') if hasattr(div, 'attrib') else 'no-class'
                text = div.text[:100] if div.text else 'no-text'
                print(f"   Div {i}: class='{classes}' | text='{text}'")
            
            print(f"\n2. ALL UL/LI elements:")
            uls = card.css('ul')
            print(f"   Found {len(uls)} <ul> elements")
            for i, ul in enumerate(uls):
                lis = ul.css('li')
                print(f"   UL {i}: has {len(lis)} <li> items")
                for j, li in enumerate(lis[:3]):
                    print(f"      LI {j}: {li.text[:80]}")
            
            print(f"\n3. ALL TABLE elements:")
            tables = card.css('table')
            print(f"   Found {len(tables)} <table> elements")
            for i, table in enumerate(tables):
                tds = table.css('td')
                print(f"   Table {i}: has {len(tds)} <td> cells")
                for j, td in enumerate(tds[:5]):
                    classes = td.attrib.get('class', '') if hasattr(td, 'attrib') else ''
                    text = td.text[:100] if td.text else ''
                    print(f"      TD {j}: class='{classes}' | text='{text}'")
            
            print(f"\n4. Looking for 'snippet' in class names:")
            all_with_snippet = card.css('[class*="snippet"]')
            print(f"   Found {len(all_with_snippet)} elements with 'snippet' in class")
            for elem in all_with_snippet[:3]:
                classes = elem.attrib.get('class', '') if hasattr(elem, 'attrib') else ''
                text = elem.text[:150] if elem.text else 'no-text'
                print(f"   - class='{classes}'")
                print(f"     text='{text}'")
            
            print(f"\n5. ALL SPANS (to find job details):")
            spans = card.css('span')
            print(f"   Found {len(spans)} span elements")
            for i, span in enumerate(spans[:10]):
                text = span.text[:100] if span.text else ''
                classes = span.attrib.get('class', '') if hasattr(span, 'attrib') else ''
                if text:
                    print(f"   Span {i}: class='{classes}' | text='{text}'")
            
            print(f"\n6. Checking for metadata divs:")
            metadata = card.css('div[class*="metadata"], div[class*="heading"], div[class*="info"]')
            print(f"   Found {len(metadata)} metadata-like divs")
            for i, meta in enumerate(metadata[:5]):
                classes = meta.attrib.get('class', '') if hasattr(meta, 'attrib') else ''
                text = meta.text[:150] if meta.text else ''
                print(f"   Meta {i}: class='{classes}'")
                print(f"     text='{text}'")
            
            print(f"\n7. Raw text content of entire card (first 500 chars):")
            print(f"   {card.text[:500]}")
            
            print("\n" + "="*80)
            print("INSPECTING SECOND JOB CARD FOR COMPARISON")
            print("="*80)
            
            if len(cards) > 1:
                card2 = cards[1]
                print(f"\nCard 2 - All LI elements:")
                lis2 = card2.css('li')
                for i, li in enumerate(lis2[:5]):
                    print(f"   LI {i}: {li.text[:100]}")
                
                print(f"\nCard 2 - Snippet search:")
                snippets = card2.css('[class*="snippet"]')
                for snippet in snippets[:2]:
                    print(f"   Snippet text: {snippet.text[:150]}")
    
    else:
        print(f"Failed to fetch page: {response.status}")

if __name__ == "__main__":
    deep_inspect()
