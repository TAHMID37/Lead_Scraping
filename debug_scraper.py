#!/usr/bin/env python3
"""
Debug script to test scraper functionality
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

def test_indeed_scraper():
    """Test Indeed scraper manually"""
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    url = "https://au.indeed.com/jobs?q=Software%20Engineer&l=Sydney&fromage=1&start=0"
    print(f"Testing URL: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Check if we got a proper page
            title = soup.title.text if soup.title else "No title"
            print(f"Page Title: {title}")

            # Look for job cards
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            print(f"Found {len(job_cards)} job cards with 'job_seen_beacon'")

            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all('div', attrs={'data-jk': True})
                print(f"Found {len(job_cards)} job cards with 'data-jk'")

            if not job_cards:
                # Look for any div with job-related classes
                all_divs = soup.find_all('div', class_=lambda x: x and 'job' in x.lower())
                print(f"Found {len(all_divs)} divs with 'job' in class")

            # Check for CAPTCHA or block page
            if "captcha" in response.text.lower():
                print("CAPTCHA detected!")
            elif "blocked" in response.text.lower() or "forbidden" in response.text.lower():
                print("Request blocked!")
            else:
                print("Page seems normal")

            # Show first 500 chars of response
            print(f"Response preview: {response.text[:500]}...")

        else:
            print(f"Failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_indeed_scraper()