// Central API configuration
// In production this is served from the same server so we use relative URLs
// In development it points to localhost:8000

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

export default API_BASE_URL;
