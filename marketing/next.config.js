/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['i.ytimg.com', 'yt3.ggpht.com'],
  },
  env: {
    NEXT_PUBLIC_APP_URL: process.env.NODE_ENV === 'production' 
      ? 'https://app.titletesterpro.com'
      : 'http://localhost:5173'
  }
}

module.exports = nextConfig