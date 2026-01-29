#!/usr/bin/env python3
"""
Debug script to check HTML structure
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

def check_indeed_html():
    """Check Indeed HTML structure"""
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    url = "https://au.indeed.com/jobs?q=Software+Engineer&l=Sydney&fromage=1&start=0"
    print(f"Checking Indeed URL: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Check for job cards
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            print(f"Found {len(job_cards)} job_seen_beacon divs")

            # Try other selectors
            mosaic = soup.find_all('div', {'class': lambda x: x and 'mosaic' in x.lower()})
            print(f"Found {len(mosaic)} mosaic divs")

            # Look for any job-related content
            job_related = soup.find_all(['div', 'li'], {'class': lambda x: x and ('job' in x.lower() or 'card' in x.lower())})
            print(f"Found {len(job_related)} job/card related elements")

            # Check if it's a CAPTCHA page
            if "captcha" in response.text.lower():
                print("CAPTCHA detected!")
                return

            # Show a sample of the HTML
            print("\nFirst 1000 chars of HTML:")
            print(response.text[:1000])

        else:
            print(f"Failed with status {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_indeed_html()