"""
Debug script to inspect Seek.com.au page structure
"""

from scrapling.fetchers import StealthyFetcher
import json

def debug_seek_page():
    """Debug Seek page structure"""

    url = "https://www.seek.com.au/ict-project-manager-jobs/in-sydney-nsw"
    print(f"Fetching: {url}")

    response = StealthyFetcher.fetch(
        url,
        headless=True,
        timeout=45000,
        hide_canvas=True,
        block_webrtc=True,
        wait_selector='[data-automation="searchResults"]',
        wait=2000
    )

    print(f"Status: {response.status}")

    if response.status == 200:
        # Try different selectors for job cards
        selectors = [
            '[data-automation="normalJob"]',
            'article[data-search-sol-meta]',
            '[data-automation="jobCard"]',
            '.job-card',
            'article',
            'div[data-automation*="job"]'
        ]

        for selector in selectors:
            elements = response.css(selector)
            print(f"Selector '{selector}': {len(elements)} elements")

            if len(elements) > 0:
                print(f"  First element HTML preview:")
                first_elem = elements[0]
                # Get a preview of the HTML
                html_preview = str(first_elem)[:500] + "..." if len(str(first_elem)) > 500 else str(first_elem)
                print(f"  {html_preview}")
                print()

        # Also check for search results container
        search_results = response.css('[data-automation="searchResults"]')
        print(f"Search results container: {len(search_results)}")

        if search_results:
            # Look inside search results
            all_articles = search_results[0].css('article')
            print(f"Articles inside search results: {len(all_articles)}")

            if all_articles:
                print("First article preview:")
                art_html = str(all_articles[0])[:500] + "..." if len(str(all_articles[0])) > 500 else str(all_articles[0])
                print(art_html)

    else:
        print(f"Failed to fetch page: {response.status}")

if __name__ == "__main__":
    debug_seek_page()