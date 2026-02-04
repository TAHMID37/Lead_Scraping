# Job Scraper API Documentation

A FastAPI-based REST API for scraping job listings from Indeed, Seek, and CareerOne with ANZSCO 482 validation.

## 🚀 Quick Start

### Start the Server

```bash
cd /Users/tahmid/scraping_data
.venv/bin/uvicorn api_main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Docs (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`

## 📋 API Endpoints

### Root Endpoint
```http
GET /
```
Returns API information and available endpoints.

### Health Check
```http
GET /health
```
Returns server health status.

### Scrape Indeed Jobs
```http
POST /api/scrape/indeed
```

**Request Body:**
```json
{
  "job_titles": ["Software Engineer", "Data Scientist"],
  "location": "Sydney NSW",
  "max_workers": 3,
  "max_pages": 2
}
```

### Scrape Seek Jobs
```http
POST /api/scrape/seek
```

**Request Body:**
```json
{
  "job_titles": ["ICT Project Manager", "Software Engineer"],
  "location": "Sydney-NSW",
  "max_workers": 3,
  "max_pages": 2
}
```

**Note**: Seek uses hyphenated locations (e.g., "Sydney-NSW", "Melbourne-VIC")

### Scrape CareerOne Jobs
```http
POST /api/scrape/careerone
```

**Request Body:**
```json
{
  "job_titles": ["Accountant", "Nurse"],
  "location": "Sydney",
  "max_workers": 3,
  "max_pages": 2
}
```

## 📝 Request Parameters

| Parameter | Type | Required | Description | Default | Constraints |
|-----------|------|----------|-------------|---------|-------------|
| `job_titles` | List[str] | ✅ Yes | List of job titles to search | - | 1-10 titles |
| `location` | str | ✅ Yes | Location to search | - | Min 1 character |
| `max_workers` | int | ❌ No | Number of parallel workers | 3 | 1-10 |
| `max_pages` | int | ❌ No | Max pages per title | 2 | 1-5 |

## 📤 Response Format

```json
{
  "success": true,
  "platform": "indeed",
  "total_jobs": 25,
  "scraped_file": "indeed_jobs_20260129_143025_scraped.json",
  "validated_file": "indeed_jobs_20260129_143025_validated.json",
  "timestamp": "2026-01-29T14:30:25.123456",
  "message": "Successfully scraped 25 jobs from Indeed"
}
```

## 📁 Output Files

Each API call generates TWO JSON files with timestamps:

1. **Scraped File**: `{platform}_jobs_{timestamp}_scraped.json`
   - Contains raw scraped job data

2. **Validated File**: `{platform}_jobs_{timestamp}_validated.json`
   - Contains jobs with ANZSCO 482 eligibility assessment

### File Naming Format
```
{platform}_jobs_YYYYMMDD_HHMMSS_{scraped|validated}.json
```

Example:
- `indeed_jobs_20260129_143025_scraped.json`
- `indeed_jobs_20260129_143025_validated.json`

## 🔧 Example Usage

### Using cURL

```bash
# Indeed
curl -X POST "http://localhost:8000/api/scrape/indeed" \
  -H "Content-Type: application/json" \
  -d '{
    "job_titles": ["Software Engineer", "Data Scientist"],
    "location": "Sydney NSW",
    "max_workers": 3,
    "max_pages": 2
  }'

# Seek
curl -X POST "http://localhost:8000/api/scrape/seek" \
  -H "Content-Type: application/json" \
  -d '{
    "job_titles": ["ICT Project Manager"],
    "location": "Sydney-NSW",
    "max_workers": 3,
    "max_pages": 2
  }'

# CareerOne
curl -X POST "http://localhost:8000/api/scrape/careerone" \
  -H "Content-Type: application/json" \
  -d '{
    "job_titles": ["Accountant", "Nurse"],
    "location": "Sydney",
    "max_workers": 3,
    "max_pages": 2
  }'
```

### Using Python (requests)

```python
import requests

url = "http://localhost:8000/api/scrape/indeed"
payload = {
    "job_titles": ["Software Engineer", "Data Scientist"],
    "location": "Sydney NSW",
    "max_workers": 3,
    "max_pages": 2
}

response = requests.post(url, json=payload)
print(response.json())
```

### Using JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/api/scrape/indeed', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    job_titles: ['Software Engineer', 'Data Scientist'],
    location: 'Sydney NSW',
    max_workers: 3,
    max_pages: 2
  })
});

const data = await response.json();
console.log(data);
```

## 🌍 Location Formats

### Indeed
- Format: `"City State"` (space-separated)
- Examples: `"Sydney NSW"`, `"Melbourne VIC"`, `"Brisbane QLD"`

### Seek
- Format: `"City-State"` (hyphen-separated)
- Examples: `"Sydney-NSW"`, `"Melbourne-VIC"`, `"Brisbane-QLD"`

### CareerOne
- Format: `"City"` (simple city name)
- Examples: `"Sydney"`, `"Melbourne"`, `"Brisbane"`

## 🎯 ANZSCO 482 Validation

Each scraped job is automatically validated against the ANZSCO 482 occupation list. The validation includes:

- **Eligibility Assessment**: Whether the job matches ANZSCO 482 criteria
- **Occupation Match**: The matched ANZSCO occupation
- **ANZSCO Code**: The official 6-digit code
- **Confidence Score**: Assessment confidence (0-5)
- **Reason**: Explanation for the decision

## ⚙️ CORS Configuration

The API is configured with permissive CORS settings for development:
- Allows all origins (`*`)
- Allows all methods
- Allows all headers

For production, update the CORS settings in `api_main.py` to specify allowed origins.

## 🛠️ Dependencies

- FastAPI
- Uvicorn
- Pydantic
- Scrapling
- BeautifulSoup4
- Google Generative AI (for ANZSCO validation)
- Python-dotenv

## 📊 Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful request
- `422 Unprocessable Entity`: Invalid request parameters
- `500 Internal Server Error`: Scraping or processing error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## 💡 Tips

1. **Rate Limiting**: Use `max_workers=3` (default) to avoid being blocked by job sites
2. **Page Limits**: Start with `max_pages=2` to test, increase carefully
3. **Job Titles**: Be specific with job titles for better results
4. **Locations**: Use the correct format for each platform
5. **File Management**: Files are saved with timestamps - clean up old files periodically

## 🔍 Monitoring

Check the terminal/console for real-time scraping progress:
- Job extraction counts
- Processing status
- ANZSCO validation results
- File save confirmations

## 📞 Support

For issues or questions:
1. Check the interactive docs at `/docs`
2. Review the console output for detailed logs
3. Verify your `.env` file has the `GEMINI_API_KEY` for ANZSCO validation
