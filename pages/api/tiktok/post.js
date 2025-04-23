// Next.js API route for posting content to TikTok
import axios from 'axios';

export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, message: 'Method not allowed' });
  }

  try {
    // Get request body
    const { video_url, caption, hashtags } = req.body;

    // Validate required fields
    if (!video_url) {
      return res.status(400).json({ success: false, message: 'No video URL provided' });
    }

    // Get environment variables
    const apiKey = process.env.TIKTOK_API_KEY;
    const apiSecret = process.env.SOCIAL_MEDIA_TOKEN;

    if (!apiKey || !apiSecret) {
      return res.status(500).json({
        success: false,
        message: 'API credentials not configured. Please set TIKTOK_API_KEY and SOCIAL_MEDIA_TOKEN environment variables.'
      });
    }

    // Create headers with authentication
    const headers = {
      'X-API-KEY': apiKey,
      'X-API-SECRET': apiSecret,
      'Content-Type': 'application/json'
    };

    // Prepare request body
    const requestBody = {
      video_url,
      caption: caption || '',
      hashtags: hashtags || []
    };

    // Make request to TikTok API
    const response = await axios.post('https://api.tiktok.com/v1/video/upload', requestBody, { headers });

    // Return the response from TikTok API
    return res.status(200).json({
      success: true,
      message: 'Successfully posted to TikTok',
      data: response.data
    });
  } catch (error) {
    console.error('Error posting to TikTok:', error);
    
    // Return error response
    return res.status(500).json({
      success: false,
      message: `Failed to post to TikTok: ${error.message}`,
      error: error.response?.data || error.message
    });
  }
}
