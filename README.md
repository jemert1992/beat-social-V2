# Simplified TikTok API Integration Guide

This guide explains how to integrate the simplified TikTok API client with your existing Social Media Automation System. This implementation uses direct API access with your TikTok API credentials stored in Vercel environment variables, avoiding the complexity of OAuth flows.

## Files Overview

1. **tiktok_api.py**: Core API client that handles direct communication with TikTok's API
2. **tiktok_service.py**: Service layer that provides higher-level functions and error handling
3. **example_usage.py**: Example script showing how to use the integration
4. **__init__.py**: Package initialization file

## Integration Steps

### 1. Add Files to Your Repository

Add these files to your GitHub repository in the following structure:

```
your-project/
  ├── api/
  │   ├── tiktok_integration/
  │   │   ├── __init__.py
  │   │   ├── tiktok_api.py
  │   │   └── tiktok_service.py
  │   └── app.py (your existing app)
```

### 2. Update Your API Routes

In your `app.py` or main API file, add routes to use the TikTok integration:

```python
from .tiktok_integration import TikTokService

# Initialize TikTok service
tiktok_service = TikTokService()

@app.route('/api/tiktok/post', methods=['POST'])
def post_to_tiktok():
    data = request.json
    video_url = data.get('video_url')
    caption = data.get('caption', '')
    hashtags = data.get('hashtags', [])
    
    response = tiktok_service.post_video(video_url, caption, hashtags)
    return jsonify(response)

@app.route('/api/tiktok/account', methods=['GET'])
def get_tiktok_account():
    response = tiktok_service.get_account_info()
    return jsonify(response)
```

### 3. Vercel Environment Variables

Make sure you have these environment variables set in your Vercel project:

- `TIKTOK_API_KEY`: Your TikTok API key (Client Key)
- `SOCIAL_MEDIA_TOKEN`: Your TikTok API secret (Client Secret)

### 4. Testing the Integration

You can test the integration by:

1. Making a POST request to `/api/tiktok/post` with:
   ```json
   {
     "video_url": "https://example.com/video.mp4",
     "caption": "Check out this video!",
     "hashtags": ["fyp", "viral", "trending"]
   }
   ```

2. Making a GET request to `/api/tiktok/account` to verify your account connection

## Troubleshooting

- **API Key Issues**: Ensure your API keys are correctly set in Vercel environment variables
- **Video Format**: TikTok only accepts certain video formats (MP4 is recommended)
- **Rate Limiting**: TikTok may rate limit your requests if you make too many in a short period
- **Error Handling**: Check the response for detailed error messages

## Next Steps

- Add more TikTok API features as needed
- Implement similar direct API integration for Instagram
- Create a simple dashboard to manage your posts

For any questions or issues, refer to the TikTok API documentation or contact support.
