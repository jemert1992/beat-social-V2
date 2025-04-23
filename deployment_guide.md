# Social Media Automation System - Vercel Deployment Guide

This guide will walk you through deploying your Social Media Automation System to Vercel. The system has been simplified and optimized for Vercel deployment to avoid the import issues encountered with Render.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. [Git](https://git-scm.com/downloads) installed on your computer
3. Your TikTok API credentials (API key and secret)

## Project Structure

The project has been simplified to work seamlessly with Vercel:

```
social_media_automation/
├── api/
│   ├── app.py         # Main Flask application with all functionality
│   └── index.py       # Vercel serverless function handler
├── vercel.json        # Vercel configuration file
└── requirements.txt   # Python dependencies
```

## Deployment Steps

### 1. Push Your Code to GitHub

First, push your code to a GitHub repository:

```bash
# Initialize Git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for Vercel deployment"

# Add your GitHub repository as remote
git remote add origin https://github.com/yourusername/your-repo-name.git

# Push to GitHub
git push -u origin main
```

### 2. Deploy to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: Leave empty
   - Output Directory: Leave empty
5. Add Environment Variables:
   - TIKTOK_API_SECRET: Your TikTok API secret key
   - TIKTOK_API_KEY: Your TikTok API key (if available)
   - FLASK_ENV: production
6. Click "Deploy"

Vercel will automatically detect the Python application and deploy it as serverless functions.

### 3. Verify Deployment

Once deployment is complete:

1. Click on the generated URL to access your application
2. Test the API endpoints:
   - `/api/status` - Should return system status information
   - `/api/configure` - Test configuring the system with a POST request
   - `/api/plan` - Test generating a content plan

## API Endpoints

The Social Media Automation System provides the following API endpoints:

1. **GET /api/status**
   - Returns the current system status and configuration

2. **POST /api/configure**
   - Configures the system with your preferences
   - Example request body:
     ```json
     {
       "niche": "fitness",
       "tiktok_frequency": 2,
       "instagram_frequency": 1,
       "content_preferences": {
         "video_ratio": 0.8,
         "trending_ratio": 0.7,
         "reuse_ratio": 0.3
       }
     }
     ```

3. **POST /api/plan**
   - Generates a content plan for a specified number of days
   - Example request body:
     ```json
     {
       "days": 7
     }
     ```

4. **POST /api/execute**
   - Executes a content plan by scheduling posts
   - Example request body:
     ```json
     {
       "plan_id": "plan_20250423123456"
     }
     ```

5. **GET /api/report**
   - Generates a performance report with metrics and recommendations

## Monitoring and Maintenance

Vercel provides built-in monitoring for your application:

1. **Logs**: Access logs from the Vercel dashboard to troubleshoot issues
2. **Analytics**: Monitor API usage and performance
3. **Environment Variables**: Update environment variables as needed

## Troubleshooting

If you encounter any issues during deployment:

1. Check the Vercel deployment logs for error messages
2. Verify that all environment variables are correctly set
3. Ensure your TikTok API credentials are valid

## Next Steps

After successful deployment, you can:

1. Integrate with actual TikTok and Instagram APIs
2. Add more sophisticated content generation capabilities
3. Implement user authentication for a multi-user system
4. Create a frontend interface for easier management

## Support

If you need further assistance, please contact our support team or refer to the technical documentation.
