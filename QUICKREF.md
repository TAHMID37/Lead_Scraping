# 🚀 Quick Reference - Indeed Australia Scraper

## Installation (One-time setup)

```bash
# 1. Install Scrapling with browser support
pip install "scrapling[fetchers]"

# 2. Install browser dependencies
scrapling install
```

## Basic Usage

### Option 1: Run with default settings
```bash
python indeed_scraper.py
```

### Option 2: Run with custom configuration
1. Edit `config.py` to customize settings
2. Run: `python run_scraper.py`

### Option 3: Run examples
```bash
python examples.py
```

## What Gets Scraped

- ✅ **States**: QLD, NSW, WA, SA (as requested)
- ✅ **Time filter**: Last 24 hours only
- ✅ **Data extracted**:
  - Job title
  - Employer name
  - Job description
  - Posted date
  - Location
  - Job URL

## Output Files

- `indeed_jobs.json` - JSON format (machine-readable)
- `indeed_jobs.csv` - CSV format (Excel-compatible)

## Quick Customization

Edit `config.py`:
```python
STATES_TO_SCRAPE = ['QLD', 'NSW']  # Scrape fewer states
MAX_PAGES_PER_STATE = 5             # Scrape more pages
SEARCH_KEYWORD = "software"         # Add keyword filter
DAYS_POSTED = 3                     # Change time filter
```

## Code Examples

### Scrape specific state only
```python
from indeed_scraper import IndeedScraper

scraper = IndeedScraper()
jobs = scraper.scrape_state('NSW', max_pages=3)
scraper.jobs = jobs
scraper.save_to_json('nsw_jobs.json')
```

### Filter results
```python
from indeed_scraper import IndeedScraper

scraper = IndeedScraper()
all_jobs = scraper.scrape_all_states()

# Get jobs posted today
today_jobs = [j for j in all_jobs if j['posted_date'] == 'Today']
print(f"Jobs posted today: {len(today_jobs)}")
```

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Module not found | `pip install "scrapling[fetchers]"` |
| Browser not found | `scrapling install` |
| No jobs found | Check `config.py` settings, verify Indeed is accessible |
| Rate limited | Increase delays in `config.py` |

## File Structure

```
📁 scraping_data/
├── 📄 indeed_scraper.py      ⭐ Main scraper (core functionality)
├── 📄 run_scraper.py         ⭐ Run with config.py settings
├── 📄 config.py              ⭐ Customize scraper settings
├── 📄 examples.py            📚 Usage examples
├── 📄 requirements.txt       📦 Dependencies
├── 📄 README.md             📖 Full documentation
├── 📄 SETUP.md              🔧 Setup instructions
└── 📄 QUICKREF.md           ⚡ This file
```

## Key Features

✅ **Anti-bot bypass**: Uses StealthyFetcher for reliable scraping  
✅ **Respectful**: Built-in delays between requests  
✅ **Flexible**: Easy configuration and customization  
✅ **Complete**: Extracts all required job information  
✅ **Multi-format**: Outputs both JSON and CSV  

## Performance

- ~10-15 jobs per page
- ~30-45 jobs per state (3 pages default)
- ~120-180 total jobs (4 states)
- Runtime: ~2-3 minutes (with default settings)

## Pro Tips

💡 **Start small**: Test with 1-2 pages per state first  
💡 **Check output**: Verify data quality before scaling up  
💡 **Monitor rate limits**: If blocked, increase delays  
💡 **Stay updated**: Indeed's HTML may change over time  

## Support

📖 Read: `README.md` for detailed documentation  
🔧 Check: `SETUP.md` for installation help  
💻 Try: `examples.py` for code samples  

---

**Ready to scrape?** Just run: `python indeed_scraper.py` 🚀
