"""Check StealthyFetcher response object"""
from scrapling.fetchers import StealthyFetcher

response = StealthyFetcher.fetch(
    "https://au.indeed.com/jobs?q=ICT%20Project%20Manager&l=Sydney-NSW&fromage=1&start=0",
    headless=True,
    hide_canvas=True,
    block_webrtc=True,
    network_idle=False,
    load_dom=True,
    wait=2000,
    timeout=30000
)

print(f"Response type: {type(response)}")
print(f"Response attributes: {dir(response)}")
print(f"Has 'text': {hasattr(response, 'text')}")
print(f"Has 'html_content': {hasattr(response, 'html_content')}")
print(f"Has 'content': {hasattr(response, 'content')}")

if hasattr(response, 'text'):
    print(f"response.text length: {len(response.text)}")
if hasattr(response, 'html_content'):
    print(f"response.html_content length: {len(response.html_content)}")
