"""
Company Details Scraper
Extracts company information from company pages using Spider.cloud API
"""

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import Dict
import os
import requests
import time
import random

load_dotenv()

SPIDER_API_URL = "https://api.spider.cloud/v1/scrape"


def _spider_fetch(url: str) -> str:
    """Fetch a page via Spider.cloud API, returning raw HTML."""
    api_key = os.getenv("SPIDER_API_KEY")
    if not api_key:
        return ""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"url": url, "return_format": "raw", "request": "smart"}

    try:
        resp = requests.post(SPIDER_API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            return data[0].get("content", "")
        return data.get("content", "") if isinstance(data, dict) else ""
    except Exception as e:
        print(f"    Spider fetch error for {url}: {e}")
        return ""


class CompanyScraper:
    """Scrape company details from company pages"""

    def __init__(self):
        self.BASE_URL_CAREERONE = 'https://www.careerone.com.au'

    def scrape_careerone_company(self, company_url: str, company_name: str) -> Dict:
        """Scrape company information from CareerOne company page"""
        company_info = {
            'name': company_name,
            'description': '',
            'website': '',
            'industry': '',
            'source_url': company_url,
            'source': 'careerone'
        }

        if not company_url or '/jobs/br_' not in company_url:
            return company_info

        try:
            time.sleep(random.uniform(0.5, 1.5))
            html = _spider_fetch(company_url)
            if not html:
                return company_info

            soup = BeautifulSoup(html, "html.parser")

            # Description
            for selector in ['.company-description', '[class*="about"]', '[class*="description"]',
                             '.company-info', 'div.text-body-4', 'p']:
                for elem in soup.select(selector):
                    text = elem.get_text(separator=' ', strip=True)
                    if text and 100 < len(text) < 2000:
                        low = text.lower()
                        if not any(w in low for w in ['apply now', 'search jobs', 'back to', 'similar jobs']):
                            company_info['description'] = text[:1000]
                            break
                if company_info['description']:
                    break

            # Website
            for a in soup.select('a[href^="http"]'):
                href = a.get('href', '')
                if href and 'careerone.com.au' not in href:
                    link_text = (a.get_text(strip=True) or '').lower()
                    if 'website' in link_text or 'visit' in link_text or len(link_text) < 30:
                        company_info['website'] = href
                        break

            # Industry
            for selector in ['[class*="industry"]', '[class*="sector"]', '.company-category']:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if text and len(text) < 100:
                        company_info['industry'] = text
                        break

        except Exception as e:
            print(f"    Error scraping company page for {company_name}: {str(e)[:50]}")

        return company_info

    def enrich_company_info(self, company_name: str, company_url: str = "",
                           source: str = "careerone", existing_description: str = "",
                           job_titles: list = None) -> Dict:
        """Enrich company information based on source"""
        if not company_name or company_name == "Not specified":
            return {
                'name': company_name,
                'description': '',
                'website': '',
                'industry': '',
                'source_url': company_url,
                'source': source
            }

        if source == "careerone" and company_url and '/jobs/br_' in company_url:
            enriched = self.scrape_careerone_company(company_url, company_name)
            if not enriched.get('description') or len(enriched.get('description', '')) < 50:
                if existing_description:
                    enriched['description'] = existing_description
                elif job_titles:
                    enriched['description'] = f"{company_name} is hiring for positions including: {', '.join(job_titles[:3])}. Found via {source} job listings."
            return enriched

        description = existing_description
        if not description or len(description) < 100:
            if job_titles:
                titles_str = ', '.join(dict.fromkeys(job_titles[:5]))  # unique titles
                description = f"{company_name} is currently hiring for: {titles_str}. Company discovered through {source} job postings."
            else:
                description = f"{company_name} - Employer found on {source} job board."

        return {
            'name': company_name,
            'description': description,
            'website': '',
            'industry': '',
            'source_url': company_url,
            'source': source
        }


def _extract_description_from_markdown(job_desc: str) -> str:
    """Extract a meaningful description paragraph from markdown job content.

    Spider returns markdown that starts with page titles, nav links, etc.
    We skip those and look for real descriptive prose.
    """
    if not job_desc or len(job_desc) < 100:
        return ""

    skip_indicators = [
        'indeed.com', 'seek.com', 'careerone.com',  # page titles
        'apply now', 'sign in', 'find jobs', 'search',  # nav
        'responsibilities', 'requirements', 'skills', 'qualifications',  # section headers
        'cookie', 'privacy', 'terms of use',  # footers
    ]

    lines = job_desc.split('\n')
    paragraphs = []
    for line in lines:
        stripped = line.strip().lstrip('#').strip()
        if not stripped or len(stripped) < 60:
            continue
        # Skip markdown links, headers, nav-like lines
        if stripped.startswith('[') or stripped.startswith('|') or stripped.startswith('---'):
            continue
        low = stripped.lower()
        if any(s in low for s in skip_indicators):
            continue
        paragraphs.append(stripped)

    if paragraphs:
        # Join the first few meaningful paragraphs (up to 2000 chars)
        result = '\n'.join(paragraphs[:10])
        return result[:2000]

    # Fallback: return a chunk from the middle of the description (skip first 200 chars of headers)
    start = min(200, len(job_desc) // 4)
    return job_desc[start:start + 2000].strip()


def extract_companies_from_jobs(jobs: list, source: str = "careerone") -> list:
    """Extract unique companies from job listings"""
    companies = {}

    for job in jobs:
        company_name = job.get('employer_name', 'Not specified')

        if company_name and company_name != "Not specified":
            if company_name not in companies:
                anzsco_eligible = False
                if 'anzsco_assessment' in job:
                    anzsco_eligible = job['anzsco_assessment'].get('eligible', False)

                job_desc = job.get('job_description', '')
                company_desc = _extract_description_from_markdown(job_desc)

                companies[company_name] = {
                    'name': company_name,
                    'description': company_desc,
                    'website': '',
                    'industry': '',
                    'source_url': job.get('company_url', job.get('url', '')),
                    'source': source,
                    'anzsco_eligible': anzsco_eligible,
                    'job_count': 1,
                    'sample_job_title': job.get('job_title', ''),
                    'job_titles': [job.get('job_title', '')],
                    'job_descriptions': [job_desc] if job_desc else []
                }
            else:
                companies[company_name]['job_count'] += 1
                companies[company_name]['job_titles'].append(job.get('job_title', ''))
                if 'anzsco_assessment' in job and job['anzsco_assessment'].get('eligible', False):
                    companies[company_name]['anzsco_eligible'] = True
                job_desc = job.get('job_description', '')
                if job_desc:
                    companies[company_name]['job_descriptions'].append(job_desc)
                    # Update description if current one is short and new one is better
                    if len(companies[company_name]['description']) < 200:
                        better = _extract_description_from_markdown(job_desc)
                        if len(better) > len(companies[company_name]['description']):
                            companies[company_name]['description'] = better

    return list(companies.values())


def enrich_companies_with_details(companies: list, max_companies: int = 10) -> list:
    """Enrich company information by scraping company pages"""
    scraper = CompanyScraper()
    enriched = []

    print(f"\n{'='*60}")
    print(f"Enriching company details...")
    print(f"{'='*60}")

    sorted_companies = sorted(companies, key=lambda x: x.get('job_count', 0), reverse=True)

    for i, company in enumerate(sorted_companies[:max_companies], 1):
        print(f"\n[{i}/{min(len(sorted_companies), max_companies)}] Enriching: {company['name']}")

        job_titles = company.get('job_titles', [company.get('sample_job_title', '')])

        enriched_info = scraper.enrich_company_info(
            company['name'],
            company.get('source_url', ''),
            company.get('source', 'careerone'),
            company.get('description', ''),
            job_titles
        )

        enriched_company = {**company, **enriched_info}

        for key in ['job_descriptions', 'job_titles']:
            enriched_company.pop(key, None)

        enriched.append(enriched_company)

        if enriched_info.get('description'):
            print(f"  Description: {enriched_info['description'][:100]}...")
        else:
            print(f"  No description found")

    if len(sorted_companies) > max_companies:
        print(f"\n  Adding {len(sorted_companies) - max_companies} more companies without enrichment...")
        enriched.extend(sorted_companies[max_companies:])

    return enriched


if __name__ == "__main__":
    test_url = "https://www.careerone.com.au/jobs/br_department-of-foreign-affairs-and-trade"
    scraper = CompanyScraper()

    print("Testing company scraper...")
    result = scraper.scrape_careerone_company(test_url, "Department of Foreign Affairs and Trade")

    print("\nResult:")
    print(f"Name: {result['name']}")
    print(f"Description: {result['description'][:200] if result['description'] else 'None'}...")
    print(f"Website: {result['website']}")
    print(f"Industry: {result['industry']}")
