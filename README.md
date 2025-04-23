# Next.js Proxy for TikTok API Integration

This README provides instructions for setting up and deploying the Next.js proxy for your TikTok API integration.

## Overview

This application uses Next.js to create a proxy for your TikTok API integration. It provides:

1. A clean web interface for interacting with the API
2. API routes that maintain all your existing TikTok functionality
3. Proper environment variable handling
4. Vercel-compatible deployment configuration

## Files Included

- `pages/index.js` - Main UI page
- `pages/api/status.js` - API status endpoint
- `pages/api/tiktok/account.js` - TikTok account information endpoint
- `pages/api/tiktok/post.js` - TikTok posting endpoint
- `package.json` - Dependencies and scripts
- `next.config.js` - Next.js configuration

## Local Development

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
Create a `.env.local` file with:
```
TIKTOK_API_KEY=your_tiktok_api_key
SOCIAL_MEDIA_TOKEN=your_social_media_token
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment to Vercel

1. Push this code to your GitHub repository

2. Connect your repository to Vercel:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Configure the project:
     - Framework Preset: Next.js
     - Root Directory: ./
     - Build Command: next build
     - Output Directory: .next

3. Set environment variables in Vercel:
   - TIKTOK_API_KEY
   - SOCIAL_MEDIA_TOKEN

4. Deploy!

## API Endpoints

- `GET /api/status` - Check API status and environment variables
- `GET /api/tiktok/account` - Get TikTok account information
- `POST /api/tiktok/post` - Post content to TikTok

## Example API Usage

### Posting to TikTok

```javascript
fetch('/api/tiktok/post', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    video_url: 'https://example.com/video.mp4',
    caption: 'Check out this video!',
    hashtags: ['fyp', 'viral', 'trending']
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

## Troubleshooting

If you encounter any issues:

1. Check that environment variables are set correctly in Vercel
2. Verify that your TikTok API credentials are valid
3. Check the Vercel deployment logs for any errors
4. Ensure your repository has all the necessary files
