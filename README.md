# Job Scraper Application

A full-stack job scraping application that searches for jobs from Indeed, Seek, and CareerOne with ANZSCO 482 visa eligibility validation.

## 🚀 Features

- 🔍 **Multi-Platform Scraping**: Scrape jobs from Indeed, Seek, and CareerOne
- ✅ **ANZSCO 482 Validation**: Automatic visa eligibility assessment using Google Gemini AI
- 🎯 **Targeted Search**: Search by job titles from the ANZSCO occupation list
- 📍 **Location-Based**: Filter by Australian cities and suburbs
- ⚡ **Parallel Processing**: Fast scraping with concurrent workers
- 💾 **Timestamped Storage**: All results saved with timestamps
- 🎨 **Modern UI**: Clean, responsive React interface

## 📂 Project Structure

```
scraping_data/
├── backend/
│   ├── api_main.py                    # FastAPI application
│   ├── indeed_scraper_by_title.py     # Indeed scraper
│   ├── seek_scraper_by_title.py       # Seek scraper
│   ├── career_scraper_by_title.py     # CareerOne scraper
│   └── requirements.txt               # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── IndeedTab.js
│   │   │   ├── SeekTab.js
│   │   │   └── CareerOneTab.js
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── constants.js               # Job titles and locations
│   └── package.json
└── README.md
```

## 🛠️ Installation

### Backend Setup

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Create a `.env` file in the backend directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

6. Start the FastAPI server:
```bash
python api_main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## 💻 Usage

1. **Start the Backend**: Run the FastAPI server (port 8000)
2. **Start the Frontend**: Run the React app (port 3000)
3. **Select a Platform**: Choose between Indeed, Seek, or CareerOne tabs
4. **Configure Search**:
   - Select job titles from the dropdown (supports multiple selection with Ctrl/Cmd)
   - Choose a location from Australian cities
   - Set max workers (1-10) for parallel processing
   - Set max pages (1-5) to scrape per job title
5. **Start Scraping**: Click "Start Scraping" and wait for results
6. **View Results**: See the scraping status and preview the latest data

## 🔌 API Endpoints

## 🔌 API Endpoints

### Root & Health

- `GET /` - API information
- `GET /health` - Health check

### Job Scraping

- `POST /api/scrape/indeed` - Scrape jobs from Indeed.com.au
- `POST /api/scrape/seek` - Scrape jobs from Seek.com.au
- `POST /api/scrape/careerone` - Scrape jobs from CareerOne.com.au

### Latest Data

- `GET /api/latest/{platform}` - Get latest scraped data (platform: indeed/seek/careerone)

## 📝 Example Requests

### Scrape Jobs

### Scrape Jobs

**Indeed**:
```json
POST http://localhost:8000/api/scrape/indeed
{
  "job_titles": ["Software Engineer", "Data Scientist"],
  "location": "Sydney NSW",
  "max_workers": 3,
  "max_pages": 2
}
```

**Seek**:
```json
POST http://localhost:8000/api/scrape/seek
{
  "job_titles": ["Software Engineer"],
  "location": "Sydney-NSW",
  "max_workers": 3,
  "max_pages": 2
}
```

**CareerOne**:
```json
POST http://localhost:8000/api/scrape/careerone
{
  "job_titles": ["Software Engineer"],
  "location": "Sydney",
  "max_workers": 3,
  "max_pages": 2
}
```

### Get Latest Data

```bash
GET http://localhost:8000/api/latest/indeed
GET http://localhost:8000/api/latest/seek
GET http://localhost:8000/api/latest/careerone
```

## 📍 Location Formats

Each platform requires different location formats:
- **Indeed**: "Sydney NSW" (space-separated)
- **Seek**: "Sydney-NSW" (hyphen-separated)
- **CareerOne**: "Sydney" (city name only)

The frontend automatically converts the selected location to the correct format.

## 📄 Output Files

Each API call generates two JSON files in the backend directory:

1. **Scraped File**: `{platform}_jobs_{timestamp}_scraped.json` - Raw scraped data
2. **Validated File**: `{platform}_jobs_{timestamp}_validated.json` - ANZSCO validated data

Example:
- `indeed_jobs_20260129_143025_scraped.json`
- `indeed_jobs_20260129_143025_validated.json`

## ✅ ANZSCO 482 Validation

Jobs are validated against the ANZSCO Subclass 482 Eligible Occupation List using Google Gemini AI. The validation includes:
- Occupation matching
- ANZSCO code assignment
- Confidence score (0.0 - 1.0)
- Eligibility determination (true/false)
- Detailed reasoning

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Scrapling + Playwright** - Web scraping with stealth mode
- **Google Gemini API** - AI-powered ANZSCO validation
- **ThreadPoolExecutor** - Async handling for sync scrapers
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **Axios** - HTTP client
- **Modern CSS** - Gradient design with animations

## 🐛 Troubleshooting

### Backend Issues
- Ensure your Gemini API key is set in the `.env` file in the backend directory
- Check that Playwright browsers are installed: `playwright install`
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check that the backend is running on port 8000
- Verify CORS is enabled in the backend

### Common Errors
- **"It looks like you are using Playwright Sync API inside the asyncio loop"**: This has been fixed by using ThreadPoolExecutor
- **No data in preview**: Make sure you've run at least one scraping job first

## 📚 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📞 API Usage Examples

### Python Example

```python
import requests

response = requests.post(
    "http://localhost:8000/api/scrape/indeed",
    json={
        "job_titles": ["Software Engineer"],
        "location": "Sydney NSW",
        "max_workers": 3,
        "max_pages": 2
    }
)

print(response.json())
```

### JavaScript Example

```javascript
const response = await fetch('http://localhost:8000/api/scrape/indeed', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    job_titles: ['Software Engineer'],
    location: 'Sydney NSW',
    max_workers: 3,
    max_pages: 2
  })
});

const data = await response.json();
console.log(data);
```

## ⚙️ Configuration

### Request Parameters

- `job_titles`: List of job titles (1-10 titles)
- `location`: Search location
- `max_workers`: Parallel workers (1-10, default: 3)
- `max_pages`: Pages per title (1-5, default: 2)

### Location Formats

- **Indeed**: `"Sydney NSW"` (space-separated)
- **Seek**: `"Sydney-NSW"` (hyphen-separated)
- **CareerOne**: `"Sydney"` (simple city name)

## 🎯 ANZSCO 482 Validation

Each job is automatically assessed against ANZSCO 482 criteria:

- Eligibility determination
- Occupation matching
- ANZSCO code assignment
- Confidence scoring
- Reasoning explanation

## 📄 License

This project is for internal use.

## 🤝 Contributing

This is a private project. Contact the repository owner for contribution guidelines.
