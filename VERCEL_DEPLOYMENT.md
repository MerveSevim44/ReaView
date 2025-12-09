# Vercel Deployment Guide for ReaView Backend

## Prerequisites
1. A Vercel account (sign up at https://vercel.com)
2. A PostgreSQL database (e.g., from Vercel Postgres, Neon, Supabase, or Railway)
3. Vercel CLI installed (optional): `npm i -g vercel`

## Project Structure for Vercel
```
ReaView/
├── api/
│   └── index.py          # Vercel serverless function entry point
├── backend/
│   └── app/              # Your FastAPI application
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies (root level)
└── .vercelignore         # Files to exclude from deployment
```

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Easiest)

1. **Push your code to GitHub/GitLab/Bitbucket**

2. **Import to Vercel**
   - Go to https://vercel.com/dashboard
   - Click "Add New" → "Project"
   - Import your repository
   - Vercel will auto-detect the configuration from `vercel.json`

3. **Set Environment Variables**
   - In your Vercel project settings, go to "Environment Variables"
   - Add the following:
     - `DATABASE_URL`: Your PostgreSQL connection string
       - Format: `postgresql://user:password@host:port/database`
       - Example: `postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/dbname`

4. **Deploy**
   - Click "Deploy"
   - Wait for the deployment to complete
   - Your API will be available at `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```
   - Follow the prompts to link/create a project
   - Set up environment variables when prompted

4. **Set Environment Variables** (if not done during deployment)
   ```bash
   vercel env add DATABASE_URL
   ```
   - Paste your PostgreSQL connection string when prompted
   - Select "Production", "Preview", and "Development" environments

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

## Database Setup

### Important Notes:
- **Migrations**: The current setup runs migrations on startup, which may not work reliably in serverless environments
- **Recommended Approach**: 
  1. Run migrations manually on your database before deploying
  2. Or use a dedicated migration tool like Alembic
  3. Or ensure your database is pre-populated

### Running Migrations Manually:
1. Connect to your PostgreSQL database
2. Run all SQL files from the `migrations/` folder in order (000, 001, 002, etc.)

## Testing Your Deployment

Once deployed, test your API:

1. **Health Check**
   ```
   https://your-project.vercel.app/health
   ```

2. **API Endpoints**
   ```
   https://your-project.vercel.app/auth/...
   https://your-project.vercel.app/items/...
   https://your-project.vercel.app/reviews/...
   ```

## Common Issues & Solutions

### Issue: Database Connection Fails
**Solution**: Verify your `DATABASE_URL` is correct and the database is accessible from Vercel's servers

### Issue: "Module not found" errors
**Solution**: Make sure all dependencies are in `requirements.txt` at the root level

### Issue: Static files (avatars) not loading
**Solution**: Consider using external storage (S3, Cloudinary, Vercel Blob) for serverless deployments

### Issue: Cold starts are slow
**Solution**: This is normal for serverless. Consider:
- Using Vercel's Edge Functions for critical endpoints
- Upgrading to Vercel Pro for faster cold starts
- Implementing proper caching strategies

## Updating Your Frontend

Update your frontend API endpoints to point to your Vercel deployment:
```javascript
const API_BASE_URL = 'https://your-project.vercel.app';
```

## File Upload (Avatars) Considerations

For serverless deployments, local file storage doesn't persist. Consider:
- **Vercel Blob Storage**: https://vercel.com/docs/storage/vercel-blob
- **AWS S3**: Traditional cloud storage
- **Cloudinary**: Image hosting service
- **Supabase Storage**: Free tier available

## Environment Variables Reference

Required:
- `DATABASE_URL`: PostgreSQL connection string

Optional:
- Any API keys for external services
- `PYTHONPATH`: Usually not needed, but can be set to `/var/task` if import issues occur

## Monitoring & Logs

- View logs in Vercel Dashboard → Your Project → Deployments → [Select Deployment] → Logs
- Use `print()` statements for debugging (they appear in logs)

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Set up DATABASE_URL
3. ✅ Verify health endpoint works
4. ✅ Test all API endpoints
5. ✅ Update frontend to use new API URL
6. ⚠️ Set up proper file storage for avatars
7. ⚠️ Implement proper migration strategy
8. ⚠️ Add authentication secrets if needed

## Support

- Vercel Docs: https://vercel.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com/
- Issues: Check your Vercel deployment logs for detailed error messages
