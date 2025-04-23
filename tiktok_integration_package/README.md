# TikTok API Integration - README

This package provides a complete implementation for integrating TikTok's Content Posting API with your Social Media Automation System.

## Features

- Direct API integration with TikTok using API keys
- Post videos to TikTok using URLs or file uploads
- Retrieve account information
- Check video posting status
- Proper error handling and retry logic
- Compatible with Vercel deployment

## Key Components

- **TikTok API Client**: Handles direct communication with TikTok's API
- **TikTok Service**: Provides higher-level functions with proper error handling
- **API Endpoints**: Ready-to-use endpoints for posting content and getting account information
- **Vercel Configuration**: Optimized for deployment to Vercel

## Environment Variables

This implementation uses the following environment variables:

- `TIKTOK_API_KEY`: Your TikTok API key
- `SOCIAL_MEDIA_TOKEN`: Your TikTok API secret (using this name instead of TIKTOK_API_SECRET)

## Getting Started

1. Upload all files to your GitHub repository
2. Configure environment variables in Vercel
3. Deploy your application

For detailed instructions, see the `deployment_guide.md` file.

## API Endpoints

- `GET /`: API status and available endpoints
- `GET /api/status`: Current API status and configuration
- `POST /api/configure`: Update configuration settings
- `POST /api/plan`: Create a content posting plan
- `POST /api/execute`: Execute a content posting plan
- `GET /api/report`: Generate a performance report
- `POST /api/tiktok/post`: Post content to TikTok
- `GET /api/tiktok/account`: Get TikTok account information

## Example Usage

### Posting a Video to TikTok

```json
POST /api/tiktok/post
{
  "video_url": "https://example.com/video.mp4",
  "caption": "Check out this awesome video!",
  "hashtags": ["viral", "trending", "fyp"]
}
```

## Important Notes

This implementation uses `SOCIAL_MEDIA_TOKEN` instead of `TIKTOK_API_SECRET` to avoid Vercel's secret reference detection issue. Make sure to use this environment variable name in your Vercel configuration.
