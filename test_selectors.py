"""
Test selectors on the saved Seek HTML
"""

from bs4 import BeautifulSoup

def test_selectors():
    """Test different selectors on the saved HTML"""

    with open('seek_page.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    print(f"HTML length: {len(html_content)}")
    print(f"Soup title: {soup.title.text if soup.title else 'No title'}")

    # Test different selectors
    selectors = [
        'article[data-automation="normalJob"]',
        'article[data-search-sol-meta]',
        'article[data-testid="job-card"]',
        'article',
        '[data-automation="normalJob"]',
        '[data-automation="searchResults"]',
        '.job-card'
    ]

    for selector in selectors:
        try:
            elements = soup.select(selector)
            print(f"Selector '{selector}': {len(elements)} elements")
            if len(elements) > 0:
                # Show first element preview
                first = elements[0]
                print(f"  First element classes: {first.get('class', [])}")
                print(f"  First element attrs: {dict(first.attrs)}")
                print(f"  Preview: {str(first)[:200]}...")
                print()
        except Exception as e:
            print(f"Error with selector '{selector}': {e}")

if __name__ == "__main__":
    test_selectors()