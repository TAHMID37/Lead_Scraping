# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack Australian job scraping application with AI-powered ANZSCO 482 visa eligibility validation. Scrapes Indeed, Seek, and CareerOne, validates jobs against ANZSCO occupation codes using Google Gemini AI, and optionally syncs companies to HubSpot CRM.

## Common Commands

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 api_main.py                # starts FastAPI on port 3001
```

### Frontend
```bash
cd frontend
npm install
npm start                         # React dev server on port 3000
npm run build                     # production build
```

### Both (dev)
```bash
./start.sh                        # launches backend (8000) + frontend (3000)
```

### Production
```bash
docker build -t job-scraper .
docker run -e SPIDER_API_KEY=xxx -e GEMINI_API_KEY=xxx -e HUBSPOT_API_KEY=yyy -p 3001:3001 job-scraper
# OR
./run_server.sh                   # builds frontend, serves everything on port 8000
```

### Testing
```bash
cd backend
python test_integration.py        # full scrape→validate→enrich→sync workflow test
python hubspot_integration.py     # HubSpot API connectivity test
```

### API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

**Backend:** Python FastAPI + Spider.cloud API + BeautifulSoup + Google Gemini AI + HubSpot API

**Frontend:** React 18 (Create React App) + Axios

### Data Flow
1. React tab component sends `POST /api/scrape/{platform}` with job titles, location, config
2. FastAPI calls scraper directly (Spider.cloud is HTTP-based, no asyncio conflicts)
3. Scraper fetches listing pages via Spider API (`return_format="raw"`) → BeautifulSoup parses job cards
4. Detail pages fetched via Spider API (`return_format="markdown"`) in parallel
5. Raw jobs saved as `{platform}_jobs_{timestamp}_scraped.json`
6. Gemini AI validates each job against ANZSCO 482 eligible occupations
7. Validated jobs saved as `{platform}_jobs_{timestamp}_validated.json`
8. Company information extracted, enriched, and synced to HubSpot

### Scraper Pattern
Base class `SpiderBaseScraper` in `spider_base_scraper.py` provides:
- Spider.cloud API client with retry logic (429 backoff)
- `scrape_multiple_titles(titles, location, max_pages)` with **100-job cap** across all titles
- `validate_jobs_with_anzsco(jobs)` — Gemini AI validation (ANZSCO prompt defined once)

Three thin subclasses override: `build_search_url()`, `parse_listing_html()`, `parse_job_detail()`
- Location format differs: Indeed uses "Sydney NSW", Seek uses "Sydney-NSW", CareerOne uses "Sydney"

### API Endpoints
- `POST /api/scrape/{indeed|seek|careerone}` — trigger scraping (body: `ScrapeRequest`)
- `GET /api/latest/{platform}` — latest scraped data
- `GET /api/files/{platform}` — list all data files
- `GET /api/file/{platform}/{filename}` — specific file data
- `GET /health` — health check

### Frontend Structure
- `App.js` — tab layout (Indeed/Seek/CareerOne)
- `components/{IndeedTab,SeekTab,CareerOneTab}.js` — per-platform scraping UI
- `components/JobDetail.js` — job detail modal
- `constants.js` — 240+ ANZSCO job titles and 30+ Australian locations
- `config.js` — API base URL (relative in prod, localhost:8000 in dev)

### Environment Variables
- `SPIDER_API_KEY` — required for web scraping via Spider.cloud
- `GEMINI_API_KEY` — required for ANZSCO validation
- `HUBSPOT_API_KEY` — optional, for CRM company sync
- `DATA_DIR` — scraped JSON storage directory (default: `backend/` or `/app/backend` in Docker)
- `REACT_APP_API_URL` — frontend API base URL

### Deployment
- **Dev:** Separate React dev server (3000) + FastAPI (8000) with CORS
- **Prod:** Single FastAPI process serving React static build + API, via Docker (3001) or systemd
