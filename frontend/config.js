/**
 * config.js — OMR Checker Frontend Configuration
 * 
 * The API_BASE_URL is read from:
 *   1. localStorage key "omr_api_url"  (user-configured via Settings panel)
 *   2. This file's DEFAULT_API_URL     (fallback)
 *
 * When running locally:  http://localhost:5000/api
 * When backend is on Render/Railway: https://your-app.onrender.com/api
 */

const DEFAULT_API_URL = 'http://localhost:5000/api';

// Read from localStorage or fall back to default
const API = (() => {
  const stored = localStorage.getItem('omr_api_url');
  return (stored && stored.trim()) ? stored.trim() : DEFAULT_API_URL;
})();
