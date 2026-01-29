"""Debug script to inspect HTML structure"""
from scrapling.fetchers import StealthyFetcher
from bs4 import BeautifulSoup
import urllib.parse

def inspect_indeed():
    print("=" * 80)
    print("INSPECTING INDEED")
    print("=" * 80)
    
    job_title = "ICT Project Manager"
    location = "Sydney-NSW"
    encoded_title = urllib.parse.quote(job_title)
    encoded_location = urllib.parse.quote(location)
    
    url = f"https://au.indeed.com/jobs?q={encoded_title}&l={encoded_location}&fromage=1&start=0"
    print(f"URL: {url}\n")
    
    response = StealthyFetcher.fetch(
        url,
        headless=True,
        hide_canvas=True,
        block_webrtc=True,
        wait=2000,
        timeout=30000
    )
    
    soup = BeautifulSoup(response.html_content, 'html.parser')
    
    # Find job containers
    print("Looking for job containers...")
    job_cards = soup.find_all('div', class_='job_seen_beacon')
    print(f"Found {len(job_cards)} job cards with 'job_seen_beacon' class\n")
    
    # Try alternative selectors
    print("Trying alternative selectors:")
    print(f"  div[data-testid='job-search-result']: {len(soup.find_all('div', attrs={'data-testid': 'job-search-result'}))}")
    print(f"  div[class*='jobsearch-ResultsList']: {len(soup.find_all('div', class_=lambda x: x and 'jobsearch-ResultsList' in x))}")
    print(f"  article[data-jobid]: {len(soup.find_all('article', attrs={'data-jobid': True}))}")
    print(f"  div[data-automation='jobs']: {len(soup.find_all('div', attrs={'data-automation': 'jobs'}))}")
    
    # Print the first few container classes
    print("\nFirst 10 div classes found:")
    divs = soup.find_all('div', limit=20)
    for i, div in enumerate(divs[:10]):
        classes = div.get('class', [])
        data_attrs = {k: v for k, v in div.attrs.items() if k.startswith('data-')}
        if classes or data_attrs:
            print(f"  {i}: class={classes}, data={data_attrs}")
    
    # Look for job-related text
    print("\nSearching for job title text in first 500 characters...")
    text = soup.get_text()
    if "Project Manager" in text or "ICT" in text:
        print("  ✓ Found 'Project Manager' or 'ICT' in page text")
    else:
        print("  ✗ NOT FOUND 'Project Manager' or 'ICT' in page text")

def inspect_seek():
    print("\n" + "=" * 80)
    print("INSPECTING SEEK")
    print("=" * 80)
    
    url = "https://www.seek.com.au/ict-project-manager-jobs/in-sydney-nsw"
    print(f"URL: {url}\n")
    
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
    
    print("Looking for job containers...")
    job_cards = soup.find_all('article', attrs={'data-automation': 'normalJob'})
    print(f"Found {len(job_cards)} job cards with data-automation='normalJob'\n")
    
    print("Trying alternative selectors:")
    print(f"  article[data-automation]: {len(soup.find_all('article', attrs={'data-automation': True}))}")
    print(f"  article[data-search-sol-meta]: {len(soup.find_all('article', attrs={'data-search-sol-meta': True}))}")
    print(f"  article[data-testid='job-card']: {len(soup.find_all('article', attrs={'data-testid': 'job-card'}))}")
    print(f"  article: {len(soup.find_all('article'))}")
    
    # Print first few articles
    print("\nFirst 5 articles found:")
    articles = soup.find_all('article', limit=5)
    for i, article in enumerate(articles):
        data_attrs = {k: v for k, v in article.attrs.items() if k.startswith('data-')}
        print(f"  {i}: data={data_attrs}")
    
    # Look for job-related text
    print("\nSearching for job title text...")
    text = soup.get_text()
    if "Project Manager" in text or "ICT" in text:
        print("  ✓ Found 'Project Manager' or 'ICT' in page text")
    else:
        print("  ✗ NOT FOUND in page text")

def inspect_careerone():
    print("\n" + "=" * 80)
    print("INSPECTING CAREERONE")
    print("=" * 80)
    
    url = "https://www.careerone.com.au/jobs/ict-project-manager/sydney"
    print(f"URL: {url}\n")
    
    response = StealthyFetcher.fetch(
        url,
        headless=True,
        hide_canvas=True,
        block_webrtc=True,
        wait=2000,
        timeout=30000
    )
    
    soup = BeautifulSoup(response.html_content, 'html.parser')
    
    print("Looking for job containers...")
    
    # Try all selectors from CareerOne scraper
    selectors = [
        '[data-automation="jobListing"]',
        '.job-card',
        '.job-item',
        'article[class*="job"]',
        'div[class*="job-card"]'
    ]
    
    for selector in selectors:
        count = len(soup.select(selector))
        print(f"  {selector}: {count}")
    
    # Try generic article/div
    print(f"  article: {len(soup.find_all('article'))}")
    print(f"  div[class*='job']: {len(soup.find_all('div', class_=lambda x: x and 'job' in ' '.join(x).lower()))}")
    
    # Print first few containers
    print("\nFirst 10 divs/articles with 'job' in class:")
    containers = soup.find_all(['div', 'article'], class_=lambda x: x and 'job' in ' '.join(x).lower(), limit=10)
    for i, container in enumerate(containers[:10]):
        tag = container.name
        classes = container.get('class', [])
        print(f"  {i}: <{tag}> class={classes}")

if __name__ == "__main__":
    inspect_indeed()
    inspect_seek()
    inspect_careerone()
