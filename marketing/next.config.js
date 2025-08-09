/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['i.ytimg.com', 'yt3.ggpht.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NODE_ENV === 'production' 
      ? 'https://ttprov4-k58o.onrender.com'
      : 'http://localhost:8000'
  }
}

module.exports = nextConfig