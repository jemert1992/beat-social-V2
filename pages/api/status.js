// Next.js API route for checking API status
export default function handler(req, res) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({ success: false, message: 'Method not allowed' });
  }

  // Check if environment variables are set
  const apiKey = process.env.TIKTOK_API_KEY;
  const apiSecret = process.env.SOCIAL_MEDIA_TOKEN;

  // Return status information
  return res.status(200).json({
    success: true,
    message: 'Social Media Automation API is operational',
    environment: {
      tiktok_api_key_set: !!apiKey,
      social_media_token_set: !!apiSecret
    },
    endpoints: {
      status: '/api/status',
      tiktok_account: '/api/tiktok/account',
      tiktok_post: '/api/tiktok/post'
    },
    version: '1.0.0'
  });
}
