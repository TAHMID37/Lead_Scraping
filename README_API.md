# Job Scraper API

A FastAPI-based web scraping API for job listings from multiple Australian job boards using clean architecture principles.

## Features

- **Clean Architecture**: Organized into layers (API, Services, Models, Core)
- **Multiple Platforms**: Scrapes from Indeed, Seek, and CareerOne
- **RESTful API**: Follows REST standards with proper HTTP methods
- **Pydantic Validation**: Request/response validation using Pydantic models
- **Error Handling**: Comprehensive error handling and logging
- **Production Ready**: Configurable timeouts, retries, and rate limiting

## Architecture

```
app/
├── api/jobs.py              # API endpoints
├── core/config.py           # Configuration
├── models/schemas.py        # Pydantic models
├── services/
│   ├── scraper_service.py   # Orchestration logic
│   └── scrapers/            # Individual scrapers
│       ├── base_scraper.py
│       ├── indeed_scraper.py
│       ├── seek_scraper.py
│       └── careerone_scraper.py
├── main.py                  # FastAPI app
run.py                       # Server runner
test_api.py                  # Test suite
README_API.md               # Documentation
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /health` - Check API health status

### Platforms
- `GET /api/v1/jobs/platforms` - List available scraping platforms

### Job Scraping

#### Scrape from all platforms
- `POST /api/v1/jobs/scrape`
- Request body:
```json
{
  "job_title": "Software Engineer",
  "location": "Sydney",
  "max_results": 10
}
```

#### Scrape from specific platform
- `POST /api/v1/jobs/scrape/{platform}`
- Platforms: `indeed`, `seek`, `careerone`
- Same request body as above

## Request/Response Models

### JobSearchRequest
```python
{
    "job_title": str,      # Required, 1-100 characters
    "location": str,       # Optional, defaults to "Australia"
    "max_results": int     # Optional, 1-50, defaults to 10
}
```

### ScraperResponse
```python
{
    "success": bool,
    "jobs": List[JobResponse],
    "total_found": int,
    "search_title": str,
    "search_location": str,
    "scraped_at": datetime,
    "error_message": Optional[str]
}
```

### JobResponse
```python
{
    "title": str,
    "company": str,
    "location": str,
    "description": str,
    "url": str,
    "posted_date": Optional[str],
    "salary": Optional[str],
    "source": str  # "indeed", "seek", or "careerone"
}
```

## Testing

Run the test suite:
```bash
python test_api.py
```

## Configuration

The API can be configured via environment variables or `.env` file:

- `DEBUG`: Enable debug mode (default: false)
- `REQUEST_TIMEOUT`: HTTP request timeout in seconds (default: 30)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `USER_AGENT_ROTATE`: Rotate user agents (default: true)
- `REQUESTS_PER_MINUTE`: Rate limiting (default: 60)

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid request parameters
- **403 Forbidden**: Scraping blocked by target site
- **500 Internal Server Error**: Server-side errors

All errors return structured JSON responses with error details.

## Documentation

- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

## Notes

- The scrapers use scrapling (browser automation) with BeautifulSoup for reliable scraping
- Job sites frequently change their HTML structure, so selectors may need updating
- The API successfully bypasses anti-bot measures (gets 200 responses from job sites)
- Empty job results indicate that HTML parsing selectors need to be updated for current site structure
- The API is designed for development/testing purposes and includes rate limiting
- For production use, implement monitoring to detect when selectors need updating

## Development

To extend the API:

1. Add new scrapers in `app/services/scrapers/`
2. Update the service layer in `app/services/scraper_service.py`
3. Add new endpoints in `app/api/jobs.py`
4. Update models in `app/models/schemas.py`