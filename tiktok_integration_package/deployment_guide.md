# TikTok API Integration - Deployment Guide

This guide provides step-by-step instructions for deploying the TikTok API integration to Vercel.

## Prerequisites

- A GitHub account
- A Vercel account connected to your GitHub
- TikTok API credentials (API Key and Secret)

## Files Overview

This package includes:

- `api/tiktok_api.py`: Core TikTok API client that handles direct communication with TikTok's API
- `api/tiktok_service.py`: Service layer that provides higher-level functions with proper error handling
- `api/__init__.py`: Package initialization file
- `app.py`: Main application file with API endpoints
- `vercel.json`: Vercel configuration file

## Deployment Steps

### 1. Update Your GitHub Repository

1. Upload all files from this package to your GitHub repository, maintaining the directory structure
2. Ensure the `vercel.json` file is in the root directory
3. Commit and push the changes to your repository

### 2. Configure Environment Variables in Vercel

1. Log in to your Vercel dashboard
2. Select your project
3. Go to "Settings" > "Environment Variables"
4. Add the following environment variables:
   - `TIKTOK_API_KEY`: Your TikTok API key
   - `SOCIAL_MEDIA_TOKEN`: Your TikTok API secret (using this name instead of TIKTOK_API_SECRET)
5. Make sure to select all environments (Production, Preview, Development)
6. Click "Save" to apply the changes

### 3. Deploy Your Application

1. In your Vercel dashboard, go to the "Deployments" tab
2. Click "Deploy" or wait for Vercel to automatically deploy your application
3. Once deployment is complete, Vercel will provide a URL for your application

## Important Notes

- **CRITICAL**: Use `SOCIAL_MEDIA_TOKEN` as the environment variable name for your TikTok API secret, NOT `TIKTOK_API_SECRET`. This prevents Vercel's secret reference detection issue.
- The `vercel.json` file does not contain any environment variable references, which also helps avoid the secret reference issue.
- All API endpoints are accessible at your Vercel deployment URL, e.g., `https://your-app.vercel.app/api/tiktok/post`

## Testing Your Deployment

### Test the API Status

1. Open your browser and navigate to your Vercel deployment URL
2. You should see a JSON response with available endpoints and a status message

### Test TikTok Account Information

1. Send a GET request to `/api/tiktok/account`
2. If your environment variables are configured correctly, you should receive account information

### Test Posting to TikTok

1. Send a POST request to `/api/tiktok/post` with the following JSON body:
```json
{
  "video_url": "https://example.com/video.mp4",
  "caption": "Test video from my automation system",
  "hashtags": ["test", "automation", "tiktok"]
}
```
2. Check the response to verify the post was successful

## Troubleshooting

- If you encounter errors related to environment variables, double-check that you're using `SOCIAL_MEDIA_TOKEN` instead of `TIKTOK_API_SECRET`
- If you see "Module not found" errors, ensure all files are uploaded with the correct directory structure
- For API-related errors, verify your TikTok API credentials are correct and that your TikTok developer account has the necessary permissions

## Next Steps

- Implement additional features like content scheduling
- Add analytics tracking for posted content
- Create a user interface for easier management
- Expand to support other social media platforms

For any questions or issues, please refer to the TikTok API documentation or contact support.
