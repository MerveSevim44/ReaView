# ReaView Frontend

Static HTML/CSS/JavaScript frontend for ReaView application.

## Local Development

Simply open `index.html` in a browser, or use a local server:

```bash
# Python
python -m http.server 8080

# Node.js
npx http-server -p 8080

# PHP
php -S localhost:8080
```

Then visit: http://localhost:8080

## Deployment to Vercel

### Quick Deploy

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
cd frontend
vercel --prod
```

### Configuration

Update the API endpoint in `js/core/api-config.js`:

```javascript
const API_CONFIG = {
  BASE_URL: 'https://your-backend.vercel.app'
};
```

## Project Structure

```
frontend/
├── index.html          # Landing/home page
├── login.html          # User login
├── register.html       # User registration
├── feed.html           # Activity feed
├── explore.html        # Browse content
├── items.html          # Item details
├── profile.html        # User profile
├── settings.html       # User settings
├── list-detail.html    # Custom list view
├── css/               # Stylesheets
├── js/                # JavaScript
│   ├── core/          # Core configuration
│   ├── components/    # UI components
│   ├── pages/         # Page scripts
│   └── utils/         # Utilities
└── avatars/           # User avatars
```

## Technologies

- Pure HTML5/CSS3/JavaScript (no build step required)
- Responsive design
- Progressive Web App ready

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers
