"""
Test the complete company extraction and HubSpot integration workflow
"""

from career_scraper_by_title import CareerOneJobTitleScraper
from company_scraper import extract_companies_from_jobs, enrich_companies_with_details
from hubspot_integration import HubSpotIntegration
import json

print("="*60)
print("Testing Company Extraction & HubSpot Integration")
print("="*60)

# Step 1: Scrape a few jobs
print("\n[Step 1] Scraping jobs from CareerOne...")
scraper = CareerOneJobTitleScraper()
jobs = scraper.scrape_multiple_titles(["Software Engineer"], "Sydney", max_pages=1)

if not jobs:
    print("❌ No jobs found. Cannot test company extraction.")
    exit(1)

print(f"✅ Found {len(jobs)} jobs")

# Step 2: Validate with ANZSCO
print("\n[Step 2] Validating jobs with ANZSCO...")
validated_jobs = scraper.validate_jobs_with_anzsco(jobs)
print(f"✅ Validated {len(validated_jobs)} jobs")

# Step 3: Extract companies
print("\n[Step 3] Extracting companies from jobs...")
companies = extract_companies_from_jobs(validated_jobs, source="careerone")
print(f"✅ Found {len(companies)} unique companies:")
for i, company in enumerate(companies, 1):
    print(f"  {i}. {company['name']} (Jobs: {company['job_count']}, ANZSCO Eligible: {company['anzsco_eligible']})")

# Step 4: Enrich companies
print("\n[Step 4] Enriching company details...")
enriched_companies = enrich_companies_with_details(companies, max_companies=3)
print(f"✅ Enriched {len(enriched_companies)} companies")

# Show enriched data
print("\nEnriched Company Data:")
for i, company in enumerate(enriched_companies[:3], 1):
    print(f"\n  {i}. {company['name']}")
    print(f"     Description: {company['description'][:100] if company['description'] else 'None'}...")
    print(f"     Website: {company['website'] or 'None'}")
    print(f"     Source URL: {company['source_url'][:60]}...")

# Step 5: Test HubSpot integration
print("\n[Step 5] Testing HubSpot integration...")
hubspot = HubSpotIntegration()

if hubspot.is_enabled():
    print("✅ HubSpot is enabled")
    
    # Sync companies
    sync_stats = hubspot.batch_sync_companies(enriched_companies)
    
    print("\n" + "="*60)
    print("Final Results")
    print("="*60)
    print(f"Jobs Scraped: {len(validated_jobs)}")
    print(f"Companies Found: {len(companies)}")
    print(f"Companies Enriched: {len(enriched_companies)}")
    print(f"\nHubSpot Sync:")
    print(f"  Created: {sync_stats['created']}")
    print(f"  Updated: {sync_stats['updated']}")
    print(f"  Already Exists: {sync_stats['exists']}")
    print(f"  Skipped: {sync_stats['skipped']}")
    print(f"  Failed: {sync_stats['failed']}")
    print("="*60)
    
    # Save test results
    test_results = {
        "jobs": validated_jobs,
        "companies": enriched_companies,
        "hubspot_sync": sync_stats
    }
    
    with open("integration_test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Test results saved to integration_test_results.json")
    
else:
    print("⚠️  HubSpot is NOT enabled (missing API key)")
    print("   To enable, add HUBSPOT_API_KEY to your .env file")
    print("   The system will work without HubSpot, but companies won't be synced.")

print("\n✅ Test completed successfully!")
