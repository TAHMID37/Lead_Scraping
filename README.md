# Indeed Australia Job Scraper

A powerful web scraper for Indeed Australia using Scrapling library. This scraper collects fresh job postings (last 24 hours) from Queensland (QLD), New South Wales (NSW), Western Australia (WA), and South Australia (SA).

## Features

- ✅ Scrapes jobs from 4 Australian states: QLD, NSW, WA, SA
- ✅ Filters for jobs posted within the last 24 hours
- ✅ Bypasses anti-bot protection using StealthyFetcher
- ✅ Extracts: Job title, Employer name, Job description, Posted date
- ✅ Saves results to both JSON and CSV formats
- ✅ Respectful scraping with delays between requests

## Installation

### Step 1: Install Python dependencies

```bash
pip install "scrapling[fetchers]"
```

### Step 2: Install browser dependencies

```bash
scrapling install
```

This command downloads all required browsers and their dependencies for the StealthyFetcher.

## Usage

### Basic Usage

Simply run the scraper:

```bash
python indeed_scraper.py
```

This will:
1. Scrape jobs from QLD, NSW, WA, and SA
2. Filter for jobs posted in the last 24 hours
3. Save results to `indeed_jobs.json` and `indeed_jobs.csv`

### Advanced Usage

You can modify the scraper by editing `indeed_scraper.py`:

```python
from indeed_scraper import IndeedScraper

# Create scraper instance
scraper = IndeedScraper()

# Scrape with custom page limit (default is 3 pages per state)
jobs = scraper.scrape_all_states(max_pages_per_state=5)

# Save results
scraper.save_to_json('my_jobs.json')
scraper.save_to_csv('my_jobs.csv')

# Print summary
scraper.print_summary()
```

### Scrape Specific State Only

```python
from indeed_scraper import IndeedScraper

scraper = IndeedScraper()

# Scrape only Queensland
qld_jobs = scraper.scrape_state('QLD', max_pages=5)

scraper.jobs = qld_jobs
scraper.save_to_json('qld_jobs.json')
```

## Output Format

### JSON Format
```json
[
  {
    "job_title": "Software Engineer",
    "employer_name": "Tech Company",
    "job_description": "We are looking for...",
    "posted_date": "Today",
    "state": "NSW",
    "location": "Sydney NSW",
    "job_url": "https://au.indeed.com/...",
    "scraped_at": "2026-01-11T..."
  }
]
```

### CSV Format
The CSV contains the same fields in a tabular format, perfect for Excel or data analysis.

## How It Works

1. **URL Building**: Constructs Indeed search URLs with:
   - `fromage=1` - filters for last 24 hours
   - `l={STATE}` - filters by state
   - Pagination support

2. **Stealth Scraping**: Uses Scrapling's `StealthyFetcher` to:
   - Bypass anti-bot protection
   - Simulate real browser behavior
   - Handle dynamic content loading

3. **Data Extraction**: Parses job cards to extract:
   - Job title from `h2.jobTitle`
   - Company name from `[data-testid="company-name"]`
   - Description from `.job-snippet`
   - Posted date from `.date` elements

4. **Respectful Scraping**: 
   - 2-second delay between pages
   - 3-second delay between states
   - Proper error handling

## Troubleshooting

### Browser installation issues
If `scrapling install` fails, try:
```bash
pip install "scrapling[fetchers]" --upgrade
scrapling install --force
```

### No jobs found
- Indeed may have changed their HTML structure
- Try adjusting the CSS selectors in `scrape_job_card()`
- Enable debug mode to see the HTML structure

### Rate limiting
If you get blocked:
- Increase delays between requests
- Reduce `max_pages_per_state`
- Try running the scraper with `headless=False` to see what's happening

## Customization

### Change States
Edit the `STATES` dictionary in `IndeedScraper` class:
```python
STATES = {
    'VIC': 'Victoria',
    'QLD': 'Queensland',
    # Add more states
}
```

### Adjust Time Filter
Modify the `build_search_url()` method:
```python
# fromage=1 for 24 hours
# fromage=3 for 3 days
# fromage=7 for 7 days
url = f"{self.BASE_URL}/jobs?q=&l={state_code}&fromage=1&start={page * 10}"
```

### Add Search Keywords
```python
def build_search_url(self, state_code, page=0, keyword=""):
    url = f"{self.BASE_URL}/jobs?q={keyword}&l={state_code}&fromage=1&start={page * 10}"
    return url
```

## Notes

- The scraper respects Indeed's robots.txt and implements delays
- Results may vary based on Indeed's current job availability
- For production use, consider implementing more robust error handling
- StealthyFetcher helps bypass anti-bot measures, but use responsibly

## License

MIT License - Feel free to modify and use as needed.

## Disclaimer

This scraper is for educational purposes. Always respect website terms of service and scraping policies. Use responsibly and ethically.
# Lead_Scraping
