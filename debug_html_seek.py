"""
Save Seek HTML to file for inspection
"""

from scrapling.fetchers import StealthyFetcher

def save_seek_html():
    """Save Seek page HTML to file"""

    url = "https://www.seek.com.au/ict-project-manager-jobs/in-sydney-nsw"
    print(f"Fetching: {url}")

    response = StealthyFetcher.fetch(
        url,
        headless=True,
        timeout=45000,
        hide_canvas=True,
        block_webrtc=True,
        wait_selector='[data-automation="searchResults"]',
        wait=1000
    )

    print(f"Status: {response.status}")
    print(f"Response attributes: {dir(response)}")
    print(f"Text length: {len(response.text) if hasattr(response, 'text') else 'No text attr'}")
    print(f"Content length: {len(response.content) if hasattr(response, 'content') else 'No content attr'}")

    # Try different ways to get the HTML
    html_content = None
    if hasattr(response, 'html_content') and response.html_content:
        html_content = response.html_content
        print("Using response.html_content")
    elif hasattr(response, 'text') and response.text:
        html_content = response.text
        print("Using response.text")
    elif hasattr(response, 'content') and response.content:
        html_content = response.content.decode('utf-8') if isinstance(response.content, bytes) else str(response.content)
        print("Using response.content")
    elif hasattr(response, 'html') and response.html:
        html_content = response.html
        print("Using response.html")

    if html_content:
        with open('seek_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Saved HTML to seek_page.html ({len(html_content)} chars)")
    else:
        print("No HTML content found")

if __name__ == "__main__":
    save_seek_html()