import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { JOB_TITLES, LOCATIONS } from '../constants';
import JobDetail from './JobDetail';
import API_BASE_URL from '../config';

function SeekTab() {
  const [selectedTitles, setSelectedTitles] = useState([]);
  const [location, setLocation] = useState('Sydney-NSW');
  const [maxWorkers, setMaxWorkers] = useState(3);
  const [maxPages, setMaxPages] = useState(2);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [latestData, setLatestData] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [availableFiles, setAvailableFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState('latest');

  useEffect(() => {
    loadAvailableFiles();
    loadLatestData();
  }, []);

  const loadAvailableFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/files/seek`);
      setAvailableFiles(response.data.files || []);
    } catch (error) {
      console.error('Error loading available files:', error);
    }
  };

  const loadLatestData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/latest/seek`);
      setLatestData(response.data);
    } catch (error) {
      console.error('Error loading latest data:', error);
    }
  };

  const loadFileData = async (filename) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/file/seek/${filename}`);
      setLatestData(response.data);
    } catch (error) {
      console.error('Error loading file data:', error);
    }
  };

  const handleFileChange = (e) => {
    const filename = e.target.value;
    setSelectedFile(filename);
    if (filename === 'latest') {
      loadLatestData();
    } else {
      loadFileData(filename);
    }
  };

  const handleTitleChange = (e) => {
    const options = Array.from(e.target.selectedOptions, option => option.value);
    setSelectedTitles(options);
  };

  const handleScrape = async () => {
    if (selectedTitles.length === 0) {
      alert('Please select at least one job title');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      // Convert location format for Seek (Sydney-NSW)
      const seekLocation = location.replace(' ', '-');
      const response = await axios.post(`${API_BASE_URL}/api/scrape/seek`, {
        job_titles: selectedTitles,
        location: seekLocation,
        max_workers: maxWorkers,
        max_pages: maxPages
      });
      setResult(response.data);
      loadLatestData();
    } catch (error) {
      console.error('Error scraping:', error);
      setResult({ success: false, message: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="platform-tab">
      <h2>Seek Job Scraper</h2>
      
      <div className="form-section">
        <div className="form-group">
          <label>Job Titles (hold Ctrl/Cmd to select multiple):</label>
          <select multiple value={selectedTitles} onChange={handleTitleChange} size="8">
            {JOB_TITLES.map(title => (
              <option key={title} value={title}>{title}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Location:</label>
          <select value={location} onChange={(e) => setLocation(e.target.value)}>
            {LOCATIONS.map(loc => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Max Workers (1-10):</label>
            <input 
              type="number" 
              min="1" 
              max="10" 
              value={maxWorkers}
              onChange={(e) => setMaxWorkers(parseInt(e.target.value))}
            />
          </div>

          <div className="form-group">
            <label>Max Pages (1-5):</label>
            <input 
              type="number" 
              min="1" 
              max="5" 
              value={maxPages}
              onChange={(e) => setMaxPages(parseInt(e.target.value))}
            />
          </div>
        </div>

        <button 
          className="scrape-button" 
          onClick={handleScrape}
          disabled={loading}
        >
          {loading ? 'Scraping...' : 'Start Scraping'}
        </button>
      </div>

      {loading && (
        <div className="loading-status">
          <div className="spinner"></div>
          <p>Scraping Seek jobs... This may take a few minutes.</p>
        </div>
      )}

      {result && (
        <div className={`result-section ${result.success ? 'success' : 'error'}`}>
          <h3>Scraping Result</h3>
          {result.success ? (
            <>
              <p><strong>Platform:</strong> {result.platform}</p>
              <p><strong>Total Jobs:</strong> {result.total_jobs}</p>
              <p><strong>Scraped File:</strong> {result.scraped_file}</p>
              <p><strong>Validated File:</strong> {result.validated_file}</p>
              <p><strong>Timestamp:</strong> {result.timestamp}</p>
              <p className="success-message">{result.message}</p>
            </>
          ) : (
            <p className="error-message">{result.message}</p>
          )}
        </div>
      )}

      {latestData && latestData.jobs && latestData.jobs.length > 0 && (
        <div className="preview-section">
          <div className="preview-header">
            <h3>Latest Scraped Data Preview</h3>
            <div className="file-selector">
              <label>Select Data File:</label>
              <select value={selectedFile} onChange={handleFileChange}>
                <option value="latest">Latest</option>
                {availableFiles.map((file, index) => (
                  <option key={index} value={file.filename}>
                    {file.display_name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <p className="preview-info">
            Showing {latestData.jobs.length} jobs
            {latestData.timestamp && ` (Fetched: ${latestData.timestamp})`}
          </p>
          <div className="jobs-grid">
            {latestData.jobs.map((job, index) => (
              <div key={index} className="job-card" onClick={() => setSelectedJob(job)}>
                <h4>{job.job_title}</h4>
                <p className="company">{job.employer_name}</p>
                {job.anzsco_assessment?.eligible !== undefined && (
                  <span className={`eligibility ${job.anzsco_assessment.eligible ? 'eligible' : 'not-eligible'}`}>
                    {job.anzsco_assessment.eligible ? '✓ ANZSCO 482 Eligible' : '✗ Not Eligible'}
                  </span>
                )}
                {job.anzsco_assessment?.occupation && (
                  <p className="occupation"><strong>Occupation:</strong> {job.anzsco_assessment.occupation} ({job.anzsco_assessment.anzsco_code})</p>
                )}
                {job.anzsco_assessment?.confidence_score && (
                  <p className="confidence"><strong>Confidence:</strong> {(job.anzsco_assessment.confidence_score * 100).toFixed(0)}%</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedJob && (
        <JobDetail job={selectedJob} onClose={() => setSelectedJob(null)} />
      )}
    </div>
  );
}

export default SeekTab;
