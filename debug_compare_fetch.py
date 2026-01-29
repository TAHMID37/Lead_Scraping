"""Debug script to compare HTML returned by different fetch methods"""
import asyncio
from scrapling.fetchers import StealthyFetcher
from bs4 import BeautifulSoup
import urllib.parse

async def compare_fetch():
    url = "https://au.indeed.com/jobs?q=ICT%20Project%20Manager&l=Sydney-NSW&fromage=1&start=0"
    
    print("Method 1: Direct fetch with minimal params")
    print("=" * 80)
    response1 = StealthyFetcher.fetch(
        url,
        headless=True,
        hide_canvas=True,
        block_webrtc=True,
        network_idle=False,
        load_dom=True,
        wait=2000,
        timeout=30000
    )
    soup1 = BeautifulSoup(response1.text, 'html.parser')
    job_cards1 = soup1.find_all('div', class_='job_seen_beacon')
    print(f"Job cards found: {len(job_cards1)}")
    
    print("\nMethod 2: With html_content instead of text")
    print("=" * 80)
    response2 = StealthyFetcher.fetch(
        url,
        headless=True,
        hide_canvas=True,
        block_webrtc=True,
        network_idle=False,
        load_dom=True,
        wait=2000,
        timeout=30000
    )
    soup2 = BeautifulSoup(response2.html_content, 'html.parser')
    job_cards2 = soup2.find_all('div', class_='job_seen_beacon')
    print(f"Job cards found: {len(job_cards2)}")
    
    print("\nChecking if soup is None:")
    print(f"soup1 is None: {soup1 is None}")
    print(f"soup2 is None: {soup2 is None}")
    
    if job_cards1:
        print(f"\nFirst job card in soup1:")
        card = job_cards1[0]
        title_elem = card.find('h2', class_='jobTitle')
        print(f"  Has h2.jobTitle: {title_elem is not None}")

if __name__ == "__main__":
    asyncio.run(compare_fetch())
