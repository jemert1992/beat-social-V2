/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    // These will be replaced by actual environment variables in Vercel
    // They're defined here for local development
    TIKTOK_API_KEY: process.env.TIKTOK_API_KEY,
    SOCIAL_MEDIA_TOKEN: process.env.SOCIAL_MEDIA_TOKEN
  }
}

module.exports = nextConfig
