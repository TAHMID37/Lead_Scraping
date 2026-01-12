# Configuration file for Indeed Scraper

# States to scrape (Australian state codes)
# Options: QLD, NSW, VIC, SA, WA, TAS, NT, ACT
STATES_TO_SCRAPE = ['QLD', 'NSW', 'WA', 'SA']

# Maximum pages to scrape per state
# Each page typically has 10-15 jobs
# Be careful with high numbers to avoid rate limiting
MAX_PAGES_PER_STATE = 3

# Time filter for job postings
# 1 = last 24 hours (as required)
# 3 = last 3 days
# 7 = last 7 days
# 14 = last 14 days
DAYS_POSTED = 1

# Search keyword (leave empty for all jobs)
# Example: "software engineer", "nurse", "accountant"
SEARCH_KEYWORD = ""

# Delay between page requests (seconds)
# Increase if getting rate limited
PAGE_DELAY = 2

# Delay between different states (seconds)
STATE_DELAY = 3

# Browser settings for StealthyFetcher
HEADLESS_MODE = True  # True = runs in background, False = shows browser
NETWORK_IDLE = True   # Wait for network to be idle before scraping

# Output file names
JSON_OUTPUT = "indeed_jobs.json"
CSV_OUTPUT = "indeed_jobs.csv"

# Additional settings
VERBOSE = True  # Print detailed progress information
