/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['i.ytimg.com', 'yt3.ggpht.com'],
  },
  webpack: (config, { dev, isServer }) => {
    // Log API base URL during build time
    if (!dev && isServer) {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://ttprov5.onrender.com';
      console.log(`🔗 TTPROv5 Frontend Build - API Base URL: ${apiBaseUrl}`);
      console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
      console.log(`📦 Build Target: ${process.env.VERCEL_ENV || 'local'}`);
    }
    return config;
  }
}

module.exports = nextConfig