// API Configuration for ReaView Frontend
// This file centralizes all API endpoint configurations
// Update API_BASE_URL to point to your deployed backend

const API_CONFIG = {
  // Change this to your Vercel backend URL after deployment
  // Example: 'https://rea-view.vercel.app' or 'https://your-backend.vercel.app'
  BASE_URL: 'https://reaview.vercel.app',
  
  // Alternative: Use environment-based URL
  // BASE_URL: window.location.hostname === 'localhost' 
  //   ? 'http://localhost:8000' 
  //   : 'https://rea-view.vercel.app'
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = API_CONFIG;
}
