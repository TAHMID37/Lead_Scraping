"""
Indeed Job Scraper by Job Title with ANZSCO 482 Validation
Searches for specific job titles, scrapes in parallel (5 workers), and validates eligibility
"""

from scrapling.fetchers import StealthyFetcher
from datetime import datetime
from playwright.sync_api import Page
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import google.generativeai as genai
import json
import time
import random
import os
import urllib.parse

# Load environment variables
load_dotenv()

SYSTEM_PROMPT = """
You are an ANZSCO Subclass 482 occupation assessor.

Your task is to determine whether a given job is eligible for Subclass 482 sponsorship by matching it ONLY against the ANZSCO 482 Eligible Occupation List provided below.

STRICT RULES:
1. Assess eligibility based on actual job duties, responsibilities, authority, and skill level — NOT job title alone.
2. You may ONLY select an occupation from the ANZSCO 482 Eligible Occupation List below.
3. If the role does not clearly and convincingly match an occupation’s core ANZSCO duties and required skill level, mark it as NOT eligible.
4. Operational, support, assistant, coordinator, technician, or execution-only roles are NOT eligible unless they clearly meet ANZSCO professional or managerial standards.
5. If there is ambiguity, insufficient evidence, or partial alignment, default to NOT eligible.
6. Do NOT invent occupations, ANZSCO codes, or eligibility rules.
7. Do NOT apply any visa logic beyond occupation matching.

ASSESSMENT METHOD:
- Identify the closest matching occupation from the list below.
- Verify that at least 60–70% of the role’s primary duties align with the ANZSCO occupation.
- Confirm the role meets the expected ANZSCO skill level.
- If all conditions are met, eligible = true. Otherwise, eligible = false.

ANZSCO 482 ELIGIBLE OCCUPATIONS:
ANZSCO 482 Eligible Occupations:
Chief Executive or Managing Director (111111)
Corporate General Manager (111211)
Aquaculture Farmer (121111)
Apiarist (121311)
Dairy Cattle Farmer (121313)
Goat Farmer (121315)
Pig Farmer (121318)
Poultry Farmer (121321)
Flower Grower (121611)
Sales and Marketing Manager (131112)
Advertising Manager (131113)
Corporate Services Manager (132111)
Finance Manager (132211)
Human Resource Manager (132311)
Policy and Planning Manager (132411)
Research and Development Manager (132511)
Construction Project Manager (133111)
Project Builder (133112)
Engineering Manager (133211)
Production Manager (Forestry) (133511)
Production Manager (Manufacturing) (133512)
Supply and Distribution Manager (133611)
Procurement Manager (133612)
Medical Administrator/ Medical Superintendent (134211)
Nursing Clinical Director (134212)
Primary Health Organisation Manager (134213)
School Principal (134311)
Faculty Head (134411)
Education Managers nec (134499)
Chief Information Officer (135111)
ICT Project Manager (135112)
ICT Managers nec (135199)
Arts Administrator or Manager (139911)
Environmental Manager (139912)
Laboratory Manager (139913)
Quality Assurance Manager (139916)
Regulatory Affairs Manager (139917)
Hotel or Motel Manager (141311)
Licensed Club Manager (141411)
Accommodation and Hospitality Managers nec (141999)
Retail Manager (General) (142111)
Travel Agency Manager (142116)
Fleet Manager (149411)
Boarding Kennel or Cattery Operator (149911)
Cinema or Theatre Manager (149912)
Equipment Hire Manager (149915)
Hospitality, Retail and Service Managers nec (149999)
Music Director (211212)
Artistic Director (212111)
Program Director (Television or Radio) (212315)
Stage Manager (212316)
Technical Director (212317)
Video Producer (212318)
Print Journalist (212413)
Radio Journalist (212414)
Technical Writer (212415)
Television Journalist (212416)
Journalists and Other Writers nec (212499)
Accountant (General) (221111)
Management Accountant (221112)
Taxation Accountant (221113)
Company Secretary (221211)
External Auditor (221213)
Internal Auditor (221214)
Finance Broker (222112)
Insurance Broker (222113)
Financial Investment Adviser (222311)
Human Resource Adviser (223111)
Recruitment Consultant (223112)
Workplace Relations Adviser (223113)
Actuary (224111)
Mathematician (224112)
Data Analyst (224114)
Data Scientist (224115)
Statistician (224116)
Land Economist (224511)
Valuer (224512)
Organisation and Methods Analyst (224712)
Management Consultant (224713)
Supply Chain Analyst (224714)
Patents Examiner (224914)
Information and Organisation Professionals nec (224999)
Advertising Specialist (225111)
Marketing Specialist (225113)
Content Creator (Marketing) (225114)
ICT Account Manager (225211)
ICT Business Development Manager (225212)
ICT Sales Representative (225213)
Public Relations Professional (225311)
Sales Representative (Industrial Products) (225411)
Sales Representative (Medical and Pharmaceutical Products) (225412)
Technical Sales Representatives nec (225499)
Aeroplane Pilot (231111)
Flying Instructor (231113)
Helicopter Pilot (231114)
Air Transport Professionals nec (231199)
Ship's Engineer (231212)
Architect (232111)
Landscape Architect (232112)
Surveyor (232212)
Cartographer (232213)
Other Spatial Scientist (232214)
Jewellery Designer (232313)
Illustrator (232412)
Multimedia Designer (232413)
Web Designer (232414)
Interior Designer (232511)
Urban and Regional Planner (232611)
Chemical Engineer (233111)
Materials Engineer (233112)
Civil Engineer (233211)
Geotechnical Engineer (233212)
Quantity Surveyor (233213)
Structural Engineer (233214)
Transport Engineer (233215)
Electrical Engineer (233311)
Electronics Engineer (233411)
Industrial Engineer (233511)
Mechanical Engineer (233512)
Production or Plant Engineer (233513)
Mining Engineer (excluding Petroleum) (233611)
Petroleum Engineer (233612)
Aeronautical Engineer (233911)
Agricultural Engineer (233912)
Biomedical Engineer (233913)
Engineering Technologist (233914)
Environmental Engineer (233915)
Naval Architect/ Marine Designer (233916)
Engineering Professionals nec (233999)
Agricultural Consultant (234111)
Agricultural Research Scientist (234114)
Agronomist (234115)
Aquaculture or Fisheries Scientist (234116)
Chemist (234211)
Food Technologist (234212)
Wine Maker (234213)
Environmental Consultant (234312)
Environmental Scientists nec (234399)
Geologist (234411)
Geophysicist (234412)
Hydrogeologist (234413)
Life Scientist (General) (234511)
Biochemist (234513)
Botanist (234515)
Marine Biologist (234516)
Entomologist (234521)
Zoologist (234522)
Life Scientists nec (234599)
Respiratory Scientist (234612)
Veterinarian (234711)
Conservator (234911)
Metallurgist (234912)
Meteorologist (234913)
Physicist (234914)
Natural and Physical Science Professionals nec (234999)
Early Childhood (Pre-primary School) Teacher (241111)
Primary School Teacher (241213)
Middle School Teacher/ Intermediate School Teacher (241311)
Secondary School Teacher (241411)
Special Needs Teacher (241511)
Teacher of the Hearing Impaired (241512)
Teacher of the Sight Impaired (241513)
Special Education Teachers nec (241599)
University Lecturer (242111)
Vocational Education Teacher/ Polytechnic Teacher (242211)
Education Reviewer (249112)
Music Teacher (Private Tuition) (249214)
Private Tutors and Teachers nec (249299)
Dietitian (251111)
Medical Diagnostic Radiographer (251211)
Medical Radiation Therapist (251212)
Nuclear Medicine Technologist (251213)
Sonographer (251214)
Occupational Health and Safety Adviser (251312)
Optometrist (251411)
Orthoptist (251412)
Hospital Pharmacist (251511)
Industrial Pharmacist (251512)
Retail Pharmacist (251513)
Orthotist or Prosthetist (251912)
Health Diagnostic and Promotion Professionals nec (251999)
Traditional Chinese Medicine Practitioner (252214)
Complementary Health Therapists nec (252299)
Dental Specialist (252311)
Dentist (252312)
Occupational Therapist (252411)
Physiotherapist (252511)
Podiatrist (252611)
Audiologist (252711)
Speech Pathologist/ Speech Language Therapist (252712)
General Practitioner (253111)
Resident Medical Officer (253112)
Anaesthetist (253211)
Specialist Physician (General Medicine) (253311)
Cardiologist (253312)
Clinical Haematologist (253313)
Medical Oncologist (253314)
Endocrinologist (253315)
Gastroenterologist (253316)
Intensive Care Specialist (253317)
Neurologist (253318)
Paediatrician (253321)
Renal Medicine Specialist (253322)
Rheumatologist (253323)
Thoracic Medicine Specialist (253324)
Specialist Physicians nec (253399)
Psychiatrist (253411)
Surgeon (General) (253511)
Cardiothoracic Surgeon (253512)
Neurosurgeon (253513)
Orthopaedic Surgeon (253514)
Otorhinolaryngologist (253515)
Paediatric Surgeon (253516)
Plastic and Reconstructive Surgeon (253517)
Urologist (253518)
Vascular Surgeon (253521)
Dermatologist (253911)
Emergency Medicine Specialist (253912)
Obstetrician and Gynaecologist (253913)
Ophthalmologist (253914)
Pathologist (253915)
Diagnostic and Interventional Radiologist (253917)
Radiation Oncologist (253918)
Medical Practitioners nec (253999)
Midwife (254111)
Nurse Educator (254211)
Nurse Researcher (254212)
Nurse Practitioner (254411)
Registered Nurse (Aged Care) (254412)
Registered Nurse (Child and Family Health) (254413)
Registered Nurse (Community Health) (254414)
Registered Nurse (Critical Care and Emergency) (254415)
Registered Nurse (Developmental Disability) (254416)
Registered Nurse (Disability and Rehabilitation) (254417)
Registered Nurse (Medical) (254418)
Registered Nurse (Medical Practice) (254421)
Registered Nurse (Mental Health) (254422)
Registered Nurse (Perioperative) (254423)
Registered Nurse (Surgical) (254424)
Registered Nurse (Paediatrics) (254425)
Registered Nurses nec (254499)


OUTPUT REQUIREMENTS:
- Return ONLY valid JSON.
- Do NOT include any text outside the JSON.

{
  "eligible": true | false,
  "occupation": "",
  "anzsco_code": "",
  "confidence_score": 0.0,
  "reason": ""
}

"""


class IndeedJobTitleScraper:
    """Scraper that searches Indeed by specific job titles"""
    
    # Rotate through different user agents to avoid detection
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    def __init__(self, max_workers=5):
        self.jobs = []
        self.max_workers = max_workers  # Reduce to 3 to avoid rate limiting
        self.BASE_URL = 'https://au.indeed.com'
        
        # Initialize Gemini for ANZSCO validation
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')
        else:
            self.gemini_model = None
            print("⚠️  Warning: GEMINI_API_KEY not found. ANZSCO validation will be skipped.")
    
    def build_search_url(self, job_title, location, page=0):
        """Build Indeed search URL for specific job title and location"""
        # URL encode the job title and location
        encoded_title = urllib.parse.quote(job_title)
        encoded_location = urllib.parse.quote(location)
        
        # fromage=1 means last 24 hours
        url = f"{self.BASE_URL}/jobs?q={encoded_title}&l={encoded_location}&fromage=1&start={page * 10}"
        return url
    
    def fetch_job_with_description(self, job_url):
        """Fetch full job description from individual job page"""
        try:
            # Define human-like page actions (matching working scraper)
            def human_behavior(page: Page):
                """Simulate human browsing behavior - faster version"""
                try:
                    # Quick mouse movement
                    page.mouse.move(100 + int(random.random() * 300), 100 + int(random.random() * 300))
                    page.wait_for_timeout(100)
                    
                    # Quick scroll down
                    for i in range(2):
                        page.evaluate('window.scrollBy(0, 300)')
                        page.wait_for_timeout(200)
                    
                    # Brief pause
                    page.wait_for_timeout(300)
                    
                    # Scroll back up
                    page.evaluate('window.scrollBy(0, -200)')
                except Exception:
                    pass  # Ignore errors in human behavior
            
            response = StealthyFetcher.fetch(
                job_url,
                headless=True,
                hide_canvas=True,
                block_webrtc=True,
                network_idle=False,
                load_dom=True,  # Wait for JavaScript to execute
                wait_selector='#jobDescriptionText',  # Wait for description element
                wait=1500,  # Wait 1.5 seconds after everything loads
                timeout=90000,  # 90 second timeout (some pages redirect multiple times)
                page_action=human_behavior
            )
            
            if response.status == 200:
                # Now extract description - content should be loaded
                description = None
                
                # Try to get all text from description container with proper structure
                desc_elem = response.css_first('#jobDescriptionText')
                if desc_elem:
                    # Get the FULL inner HTML to preserve all structure
                    description = desc_elem.get_all_text(separator='\n', strip=True)
                    
                    # If that didn't work, try getting the raw text
                    if not description or len(description) < 50:
                        description = desc_elem.text.strip() if desc_elem.text else None
                
                # Another fallback
                if not description or len(description) < 50:
                    all_desc_divs = response.css('div[id*="jobDescription"], div[class*="jobDescription"]')
                    for div in all_desc_divs:
                        text = div.get_all_text(separator='\n', strip=True)
                        if text and len(text.strip()) > 50:
                            description = text.strip()
                            break
                
                if not description or description == '':
                    description = "Description not available"
                
                # Extract posted date
                posted_date = "Unknown"
                # Look for date metadata
                date_elements = response.css('[class*="date"], [class*="Date"], time, span')
                for elem in date_elements:
                    text = elem.text if elem.text else ''
                    text_lower = text.lower()
                    if any(word in text_lower for word in ['posted', 'ago', 'day', 'hour', 'today', 'yesterday']):
                        if len(text) < 50:  # Make sure it's not a long paragraph
                            posted_date = text.strip()
                            break
                
                return description, posted_date  # Return full description without truncation
            
            return f"Failed to load page (status {response.status})", "Unknown"
            
        except Exception as e:
            return f"Error: {str(e)}", "Unknown"
    
    def process_single_job(self, job_info):
        """Process a single job (for parallel execution)"""
        try:
            # Add small random delay to avoid hammering the server (matching working scraper)
            time.sleep(random.random() * 2)
            
            description, posted_date = self.fetch_job_with_description(job_info['url'])
            
            return {
                'job_title': job_info['title'],
                'employer_name': job_info['company'],
                'location': job_info['location'],
                'job_description': description,
                'posted_date': posted_date,
                'search_title': job_info['search_title'],
                'search_location': job_info['search_location'],
                'url': job_info['url'],
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"    ✗ Error processing {job_info.get('title', 'Unknown')}: {str(e)[:50]}")
            return None
    
    def scrape_job_title(self, job_title, location, max_pages=2):  # Reduced from 3 to 2 pages
        """Scrape jobs for a specific job title and location"""
        print(f"\n{'='*60}")
        print(f"Searching: {job_title} in {location}")
        print(f"{'='*60}")
        
        all_job_urls = []
        
        # Step 1: Collect all job URLs from listing pages
        for page_num in range(max_pages):
            url = self.build_search_url(job_title, location, page_num)
            print(f"\nFetching page {page_num + 1}: {url}")
            
            try:
                print(f"  Loading page {page_num + 1}...")
                
                # Use StealthyFetcher for listing page with simpler settings (matching working scraper)
                response = StealthyFetcher.fetch(
                    url,
                    headless=True,
                    timeout=45000,  # 45 second timeout (matching working scraper)
                    hide_canvas=True,
                    block_webrtc=True
                )
                
                if response.status != 200:
                    print(f"  ✗ Failed to load page {page_num + 1} (status: {response.status})")
                    continue
                
                print(f"  ✓ Page {page_num + 1} loaded successfully")
                
                # Find job cards using response.css()
                job_cards = response.css('div.job_seen_beacon')
                
                if not job_cards:
                    print(f"No more jobs found on page {page_num + 1}")
                    break
                
                print(f"Found {len(job_cards)} job listings on page {page_num + 1}")
                
                # Extract job info from each card (using working logic from indeed_scraper_dynamic.py)
                extracted = 0
                for i, card in enumerate(job_cards, 1):
                    try:
                        # Extract basic info from listing
                        all_spans = card.css('span')
                        title = all_spans[0].text.strip() if len(all_spans) > 0 and all_spans[0].text else None
                        company = all_spans[1].text.strip() if len(all_spans) > 1 and all_spans[1].text else None
                        
                        # Get location
                        location_divs = card.css('div')
                        job_location = None
                        for div in location_divs:
                            text = div.text if div.text else ''
                            if any(state in text for state in ['NSW', 'QLD', 'VIC', 'SA', 'WA', 'NT', 'ACT', 'TAS', 'Sydney', 'Melbourne', 'Brisbane']):
                                job_location = text.strip()
                                break
                        
                        if not job_location:
                            job_location = location  # Use search location as fallback
                        
                        # Get job URL
                        job_link = card.css_first('a')
                        job_url = None
                        if job_link and hasattr(job_link, 'attrib'):
                            href = job_link.attrib.get('href')
                            if href:
                                job_url = f"{self.BASE_URL}{href}" if not href.startswith('http') else href
                        
                        if title and company and job_url:
                            all_job_urls.append({
                                'title': title,
                                'company': company,
                                'location': job_location,
                                'url': job_url,
                                'search_title': job_title,
                                'search_location': location
                            })
                            extracted += 1
                        
                    except Exception as e:
                        print(f"    ✗ Error extracting job {i}: {e}")
                        continue
                
                print(f"  Extracted {extracted} job URLs from page {page_num + 1}")
                
                # Small delay between pages
                time.sleep(random.uniform(1, 2))  # Reduced from 2-4s to 1-2s
                
            except Exception as e:
                print(f"  ✗ Error fetching page {page_num + 1}: {e}")
                continue
        
        print(f"\n{'='*60}")
        print(f"Total jobs found: {len(all_job_urls)}")
        print(f"{'='*60}")
        
        # Step 2: Process jobs in parallel (5 at a time)
        if not all_job_urls:
            print("  ⚠️  No jobs to process")
            return []
        
        print(f"\n[Processing Jobs]")
        print(f"Processing {len(all_job_urls)} jobs with {self.max_workers} parallel workers...")
        print(f"This may take a few minutes...\n")
        
        jobs_with_descriptions = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_job = {executor.submit(self.process_single_job, job_info): job_info for job_info in all_job_urls}
            
            completed = 0
            for future in as_completed(future_to_job):
                completed += 1
                try:
                    result = future.result()
                    if result:
                        jobs_with_descriptions.append(result)
                        desc_len = len(result['job_description'])
                        if desc_len > 200:
                            print(f"    ✓ [{completed}/{len(all_job_urls)}] {result['job_title'][:40]} - {desc_len} chars")
                        else:
                            print(f"    ⚠️  [{completed}/{len(all_job_urls)}] {result['job_title'][:40]} - Short description")
                    else:
                        print(f"    ✗ [{completed}/{len(all_job_urls)}] Failed")
                except Exception as e:
                    print(f"    ✗ [{completed}/{len(all_job_urls)}] Error: {str(e)[:50]}")
        
        return jobs_with_descriptions
    
    def assess_anzsco_eligibility(self, job_title, job_description):
        """Assess job against ANZSCO 482 occupation list using Gemini"""
        if not self.gemini_model:
            return {
                "eligible": False,
                "occupation": "",
                "anzsco_code": "",
                "confidence_score": 0,
                "reason": "ANZSCO validation skipped (no API key)"
            }
        
        user_prompt = f"""Job Title: {job_title}

Job Description:
{job_description}
"""
        
        try:
            full_prompt = f"{SYSTEM_PROMPT}\n\nUSER:\n{user_prompt}"
            response = self.gemini_model.generate_content(full_prompt)
            
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            assessment = json.loads(response_text.strip())
            return assessment
            
        except Exception as e:
            return {
                "eligible": False,
                "occupation": "",
                "anzsco_code": "",
                "confidence_score": 0,
                "reason": f"Error during assessment: {str(e)}"
            }
    
    def validate_jobs_with_anzsco(self, jobs):
        """Validate all jobs against ANZSCO 482"""
        print(f"\n{'='*60}")
        print(f"Validating {len(jobs)} jobs against ANZSCO 482...")
        print(f"{'='*60}")
        
        validated_jobs = []
        
        for i, job in enumerate(jobs, 1):
            print(f"\n[{i}/{len(jobs)}] Assessing: {job['job_title']}")
            
            # Skip jobs with error descriptions
            if job['job_description'].startswith('Error:') or len(job['job_description']) < 100:
                print(f"  ⚠️  Skipping (invalid description)")
                assessment = {
                    "eligible": False,
                    "occupation": "",
                    "anzsco_code": "",
                    "confidence_score": 0,
                    "reason": "Invalid or missing job description"
                }
            else:
                assessment = self.assess_anzsco_eligibility(
                    job['job_title'],
                    job['job_description']
                )
                
                if assessment['eligible']:
                    print(f"  ✓ ELIGIBLE: {assessment['occupation']} ({assessment['anzsco_code']}) - Confidence: {assessment['confidence_score']}")
                else:
                    print(f"  ✗ NOT ELIGIBLE: {assessment['reason'][:100]}")
            
            # Add assessment to job data
            validated_job = {
                **job,
                'anzsco_assessment': assessment
            }
            
            validated_jobs.append(validated_job)
            
            # Small delay to avoid rate limits
            time.sleep(1)
        
        return validated_jobs
    
    def scrape_multiple_titles(self, job_titles, location):
        """Scrape multiple job titles from the same location"""
        all_jobs = []
        
        for i, job_title in enumerate(job_titles, 1):
            print(f"\n[Job Title {i}/{len(job_titles)}]")
            jobs = self.scrape_job_title(job_title, location, max_pages=2)  # 2 pages per title
            all_jobs.extend(jobs)
            
            # Delay between different job title searches
            if i < len(job_titles):  # Don't delay after last one
                delay = random.uniform(3, 6)  # Reduced from 45-60s to 3-6s (matching working scraper pattern)
                print(f"\nWaiting {delay:.1f}s before next search...")
                time.sleep(delay)
        
        return all_jobs
    
    def save_to_json(self, jobs, filename):
        """Save jobs to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(jobs)} jobs to {filename}")
    
    def print_summary(self, jobs):
        """Print summary statistics"""
        print(f"\n{'='*60}")
        print(f"SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total jobs scraped: {len(jobs)}")
        
        # Count by search title
        by_title = {}
        for job in jobs:
            search_title = job.get('search_title', 'Unknown')
            by_title[search_title] = by_title.get(search_title, 0) + 1
        
        print(f"\nJobs by search title:")
        for title, count in by_title.items():
            print(f"  {title}: {count}")
        
        # Count eligible vs not eligible
        if jobs and 'anzsco_assessment' in jobs[0]:
            eligible = sum(1 for j in jobs if j.get('anzsco_assessment', {}).get('eligible', False))
            not_eligible = len(jobs) - eligible
            
            print(f"\n{'='*60}")
            print(f"ANZSCO 482 ELIGIBILITY SUMMARY")
            print(f"{'='*60}")
            print(f"✓ Eligible jobs: {eligible} ({eligible/len(jobs)*100:.1f}%)")
            print(f"✗ Not eligible: {not_eligible} ({not_eligible/len(jobs)*100:.1f}%)")
            
            # Show eligible jobs
            if eligible > 0:
                print(f"\nEligible jobs:")
                for job in jobs:
                    if job.get('anzsco_assessment', {}).get('eligible', False):
                        assessment = job['anzsco_assessment']
                        print(f"  • {job['job_title']} - {assessment['occupation']} ({assessment['anzsco_code']})")


def main():
    """Main execution function"""
    
    # Configuration
    JOB_TITLES = [
        "ICT Project Manager",
        # "Software Engineer",
        # "Data Scientist",
        # "Production Manager (Manufacturing)"
    ]
    
    LOCATION = "Sydney NSW"  # Can be: "Sydney NSW", "Melbourne VIC", "Brisbane QLD", "NSW", etc.
    
    OUTPUT_FILE_SCRAPED = "indeed_jobs_by_title_scraped.json"
    OUTPUT_FILE_VALIDATED = "indeed_jobs_by_title_validated.json"
    
    print(f"{'='*60}")
    print(f"Indeed Job Scraper by Title with ANZSCO 482 Validation")
    print(f"{'='*60}")
    print(f"Job Titles: {', '.join(JOB_TITLES)}")
    print(f"Location: {LOCATION}")
    print(f"Date Range: Last 24 hours")
    print(f"Parallel Workers: 3")
    print(f"{'='*60}")
    
    # Initialize scraper with 3 parallel workers (reduced to avoid rate limiting)
    scraper = IndeedJobTitleScraper(max_workers=3)
    
    # Scrape all job titles
    jobs = scraper.scrape_multiple_titles(JOB_TITLES, LOCATION)
    
    # Save scraped jobs (before validation)
    if jobs:
        scraper.save_to_json(jobs, OUTPUT_FILE_SCRAPED)
        
        # Validate against ANZSCO 482
        validated_jobs = scraper.validate_jobs_with_anzsco(jobs)
        
        # Save validated jobs (with ANZSCO assessment)
        scraper.save_to_json(validated_jobs, OUTPUT_FILE_VALIDATED)
        
        # Print summary
        scraper.print_summary(validated_jobs)
    else:
        print("\n⚠️  No jobs found!")


if __name__ == "__main__":
    main()
