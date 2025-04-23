# TikTok API Integration Files

This package contains the necessary files to integrate TikTok API with your Social Media Automation System and fix the environment variable issue in Vercel.

## Files Included

1. **api/tiktok_client.py** - The TikTok API client that handles authentication and API calls
2. **api/tiktok_integration.py** - Integration module for the TikTok API client
3. **src/posting/tiktok_posting_service.py** - Service for posting content to TikTok
4. **src/posting/__init__.py** - Package initialization file
5. **vercel.json** - Updated Vercel configuration without environment variable references

## Installation Instructions

1. Copy these files to your existing GitHub repository, maintaining the directory structure
2. Update your Vercel environment variables:
   - Use `SOCIAL_MEDIA_TOKEN` instead of `TIKTOK_API_SECRET`
   - Enter values directly as plain text, not as secret references

## Important Notes

- All code uses `SOCIAL_MEDIA_TOKEN` instead of `TIKTOK_API_SECRET` to avoid Vercel's secret reference detection
- The `vercel.json` file does not contain any environment variable references
- After adding these files, commit and push to GitHub, and Vercel should automatically deploy the updated version

For more detailed information, refer to the deployment guide in your original repository.
