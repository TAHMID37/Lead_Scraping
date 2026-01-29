#!/usr/bin/env python3
"""
Test script for the Job Scraper API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_platforms():
    """Test platforms endpoint"""
    print("\nTesting platforms endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/jobs/platforms")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scrape_all():
    """Test scraping from all platforms"""
    print("\nTesting scrape all platforms...")
    payload = {
        "job_title": "Software Engineer",
        "location": "Sydney",
        "max_results": 5
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/jobs/scrape",
            json=payload,
            timeout=60
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Total jobs found: {data['total_found']}")
            print(f"Jobs returned: {len(data['jobs'])}")
            if data['jobs']:
                print(f"Sample job: {data['jobs'][0]['title']} at {data['jobs'][0]['company']}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scrape_platform():
    """Test scraping from specific platform"""
    print("\nTesting scrape from Indeed...")
    payload = {
        "job_title": "Data Scientist",
        "location": "Melbourne",
        "max_results": 3
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/jobs/scrape/indeed",
            json=payload,
            timeout=60
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Total jobs found: {data['total_found']}")
            print(f"Jobs returned: {len(data['jobs'])}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scrape_seek():
    """Test scraping from Seek"""
    print("\nTesting scrape from Seek...")
    payload = {
        "job_title": "ICT Project Manager",
        "location": "Sydney-NSW",
        "max_results": 5
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/jobs/scrape/seek",
            json=payload,
            timeout=60
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Total jobs found: {data['total_found']}")
            print(f"Jobs returned: {len(data['jobs'])}")
            if data['jobs']:
                print(f"Sample job: {data['jobs'][0]['title']} at {data['jobs'][0]['company']}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Job Scraper API Test Suite")
    print("=" * 40)

    # Test health first
    if not test_health():
        print("Health check failed. Is the server running?")
        exit(1)

    # Test platforms
    test_platforms()

    # Test scraping (these might take time)
    print("\nNote: Scraping tests may take 30-60 seconds each...")

    test_scrape_all()
    time.sleep(2)  # Brief pause between tests
    test_scrape_platform()
    time.sleep(2)  # Brief pause between tests
    test_scrape_seek()

    print("\nTest suite completed!")