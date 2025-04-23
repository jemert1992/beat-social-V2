// Next.js API route for TikTok account information
import axios from 'axios';

export default async function handler(req, res) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({ success: false, message: 'Method not allowed' });
  }

  try {
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

    // Make request to TikTok API
    const response = await axios.get('https://api.tiktok.com/v1/account/info', { headers });

    // Return the response from TikTok API
    return res.status(200).json({
      success: true,
      message: 'Successfully retrieved TikTok account information',
      data: response.data
    });
  } catch (error) {
    console.error('Error fetching TikTok account info:', error);
    
    // Return error response
    return res.status(500).json({
      success: false,
      message: `Failed to get TikTok account information: ${error.message}`,
      error: error.response?.data || error.message
    });
  }
}
