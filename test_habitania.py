"""Test getting full Habitania job description"""
from scrapling.fetchers import StealthyFetcher
from playwright.sync_api import Page
import random

def human_behavior(page: Page):
    """Simulate human browsing"""
    page.mouse.move(100 + int(random.random() * 300), 100 + int(random.random() * 300))
    page.wait_for_timeout(200)
    
    for i in range(3):
        page.evaluate('window.scrollBy(0, %d)' % (200 + int(random.random() * 200)))
        page.wait_for_timeout(500)
    
    page.wait_for_timeout(800)
    page.evaluate('window.scrollBy(0, -150)')
    page.wait_for_timeout(300)

# Habitania job URL
url = "https://au.indeed.com/viewjob?cmp=Habitania-Homewares&t=Retail+Sales+Associate&jk=c6efd3cbc08f0106"

print("Fetching Habitania job...")
response = StealthyFetcher.fetch(
    url,
    headless=True,
    hide_canvas=True,
    block_webrtc=True,
    network_idle=True,
    load_dom=True,
    wait_selector='#jobDescriptionText',
    wait=2000,
    timeout=60000,
    page_action=human_behavior
)

print(f"Status: {response.status}\n")

desc_elem = response.css_first('#jobDescriptionText')
if desc_elem:
    print("=== METHOD 1: get_all_text() ===")
    text1 = desc_elem.get_all_text(separator='\n', strip=True)
    print(f"Length: {len(text1)} chars")
    print(text1[:500])
    
    print("\n\n=== METHOD 2: Get HTML and check structure ===")
    # Try to see the actual HTML structure
    all_children = desc_elem.css('*')
    print(f"Total child elements: {len(all_children)}")
    
    # Show first 10 elements with their tags
    for i, child in enumerate(all_children[:15]):
        tag = child.tag if hasattr(child, 'tag') else 'unknown'
        text = (child.text or '')[:80]
        print(f"{i+1}. <{tag}> {text}")
else:
    print("❌ No #jobDescriptionText found!")
