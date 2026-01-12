# Quick Setup Guide for Indeed Australia Scraper

## Step-by-Step Installation

### 1. Install Scrapling with fetchers support
```bash
pip install "scrapling[fetchers]"
```

### 2. Install browser dependencies (Required for StealthyFetcher)
```bash
scrapling install
```

This command will download:
- Chromium browser
- Required system dependencies
- Fingerprint manipulation tools

**Note**: This may take a few minutes and requires ~500MB disk space.

### 3. Verify installation
```bash
python -c "from scrapling.fetchers import StealthyFetcher; print('Installation successful!')"
```

## Running the Scraper

### Quick Start
```bash
python indeed_scraper.py
```

This will:
- Scrape jobs from QLD, NSW, WA, and SA
- Filter for jobs posted in the last 24 hours only
- Save results to `indeed_jobs.json` and `indeed_jobs.csv`

### View Examples
```bash
python examples.py
```

## Expected Output

When you run the scraper, you'll see:
```
============================================================
Indeed Australia Job Scraper
States: QLD, NSW, WA, SA
Filter: Last 24 hours only
============================================================

Scraping jobs from Queensland (QLD)...
  Fetching page 1: https://au.indeed.com/jobs?q=&l=QLD&fromage=1&start=0
  Found 15 job cards on page 1
  Successfully parsed 15 jobs from page 1
  ...
```

## Troubleshooting

### Issue: "Module not found: scrapling"
**Solution**: Install scrapling with fetchers
```bash
pip install "scrapling[fetchers]"
```

### Issue: "Browser not found" or StealthyFetcher errors
**Solution**: Install browser dependencies
```bash
scrapling install
```

If that fails, try:
```bash
pip install "scrapling[fetchers]" --upgrade
scrapling install --force
```

### Issue: "No jobs found"
**Possible causes**:
- Indeed's HTML structure changed - check the CSS selectors
- No jobs available for the last 24 hours in those states
- Being rate-limited by Indeed

**Solution**: Try adding debug output:
```python
print(response.html[:1000])  # Print first 1000 chars of HTML
```

### Issue: Getting blocked by Indeed
**Solution**: 
- The scraper already includes delays (2 sec between pages, 3 sec between states)
- If still blocked, increase delays in `indeed_scraper.py`
- Try with `headless=False` to see browser behavior

## File Structure

```
scraping_data/
├── indeed_scraper.py      # Main scraper class
├── examples.py            # Usage examples
├── requirements.txt       # Python dependencies
├── README.md             # Full documentation
├── SETUP.md              # This file
└── indeed_jobs.json      # Output (created after running)
└── indeed_jobs.csv       # Output (created after running)
```

## Next Steps

1. Run the basic scraper: `python indeed_scraper.py`
2. Check the output files: `indeed_jobs.json` and `indeed_jobs.csv`
3. Try different examples: `python examples.py`
4. Customize for your needs (see README.md)

## Important Notes

- ✅ The scraper uses StealthyFetcher to bypass anti-bot protection
- ✅ Built-in delays to be respectful to Indeed's servers
- ✅ Filters strictly for last 24 hours only (`fromage=1`)
- ✅ Scrapes only QLD, NSW, WA, and SA as requested
- ⚠️ Use responsibly and respect Indeed's terms of service

## Need Help?

Check the README.md for:
- Advanced usage examples
- Customization options
- Detailed API documentation
- More troubleshooting tips
