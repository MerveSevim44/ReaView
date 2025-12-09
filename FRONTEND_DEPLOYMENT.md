# ReaView Frontend - Vercel Deployment Guide

## Frontend Deployment on Vercel

The frontend is a static HTML/CSS/JavaScript application that can be deployed independently from the backend.

### Quick Deploy Steps

#### Option 1: Deploy via Vercel Dashboard

1. **Create a separate repository for frontend** (recommended) OR use the same repo with configuration
   
2. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Click "Add New" → "Project"
   - Import your repository

3. **Configure the project:**
   - **Framework Preset:** Other
   - **Root Directory:** `frontend` (if deploying from main repo)
   - **Build Command:** Leave empty (static site)
   - **Output Directory:** Leave empty or set to `.`
   - **Install Command:** Leave empty

4. **Deploy!**

#### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Navigate to frontend folder
cd frontend

# Deploy
vercel

# Deploy to production
vercel --prod
```

### Update API Endpoints

After deploying your backend, update the API configuration:

**Edit `frontend/js/core/api-config.js`:**
```javascript
const API_CONFIG = {
  BASE_URL: 'https://your-backend-url.vercel.app'
};
```

### File Structure

```
frontend/
├── index.html          # Landing page
├── login.html          # Login page
├── register.html       # Register page
├── feed.html           # User feed
├── explore.html        # Browse/search
├── items.html          # Item details
├── profile.html        # User profile
├── settings.html       # User settings
├── list-detail.html    # List details
├── css/               # Stylesheets
├── js/                # JavaScript files
│   ├── core/          # Core utilities
│   │   └── api-config.js  # API configuration
│   ├── components/    # Reusable components
│   ├── pages/         # Page-specific scripts
│   └── utils/         # Utility functions
└── avatars/           # Avatar images
```

### Important Notes

1. **API URL Configuration**
   - All HTML files reference `http://rea-view.vercel.app`
   - Update these references to your deployed backend URL
   - Or use the centralized `api-config.js` file

2. **CORS Configuration**
   - Ensure your backend has CORS enabled for your frontend domain
   - Backend should allow origin: `https://your-frontend.vercel.app`

3. **Environment Variables**
   - Frontend doesn't need environment variables (static site)
   - All configuration is in the JavaScript files

4. **Static Assets**
   - Avatars and images are served directly from the frontend
   - No server-side processing needed

### Testing

After deployment:

1. Visit your Vercel URL (e.g., `https://your-project.vercel.app`)
2. Test login/register functionality
3. Verify API calls work correctly
4. Check browser console for any CORS or API errors

### Separate Backend and Frontend Deployments

**Recommended approach:**

1. **Backend:** Deploy to `https://reaview-api.vercel.app`
   - From `/api/index.py` (Python serverless function)
   
2. **Frontend:** Deploy to `https://reaview.vercel.app`
   - From `/frontend` (static HTML/CSS/JS)

3. **Update frontend** to point to backend:
   ```javascript
   // In api-config.js
   BASE_URL: 'https://reaview-api.vercel.app'
   ```

### Custom Domain (Optional)

1. Go to your Vercel project → Settings → Domains
2. Add your custom domain (e.g., `reaview.com`)
3. Update DNS records as instructed
4. Update API_CONFIG to use custom domain

### Troubleshooting

**Issue: API calls failing**
- Check browser console for CORS errors
- Verify backend URL is correct in `api-config.js`
- Ensure backend CORS allows frontend domain

**Issue: 404 on page refresh**
- Vercel should handle this automatically with `cleanUrls`
- Check vercel.json routing configuration

**Issue: Static assets not loading**
- Verify file paths are relative (e.g., `./css/style.css`)
- Check that all files are committed to git

### Next Steps

1. ✅ Deploy frontend to Vercel
2. ✅ Deploy backend to Vercel
3. ✅ Update `api-config.js` with backend URL
4. ✅ Test all functionality
5. ✅ Update backend CORS to allow frontend domain
6. ⚠️ Consider using environment detection for dev/prod
7. ⚠️ Set up custom domain (optional)
