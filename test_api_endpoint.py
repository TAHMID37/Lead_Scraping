"""Test the API endpoint"""
import requests
import json
import time

# Wait for server to start
time.sleep(2)

url = "http://127.0.0.1:8888/api/v1/jobs/scrape"

payload = {
    "job_title": "ICT Project Manager",
    "location": "Sydney-NSW",
    "max_results": 5
}

print(f"Testing API endpoint: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}\n")

try:
    response = requests.post(url, json=payload, timeout=300)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
    
    result = response.json()
    print(f"Summary:")
    print(f"  Success: {result.get('success')}")
    print(f"  Total Found: {result.get('total_found')}")
    print(f"  Jobs Returned: {len(result.get('jobs', []))}")
    
    if result.get('jobs'):
        print(f"\nFirst 3 Jobs:")
        for i, job in enumerate(result.get('jobs')[:3]):
            print(f"\n  {i+1}. {job.get('title')}")
            print(f"     Company: {job.get('company')}")
            print(f"     Location: {job.get('location')}")
            print(f"     Source: {job.get('source')}")
    
except Exception as e:
    print(f"Error: {e}")
