import path from 'path'

/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config) => {
    // Add custom webpack config here
    config.resolve.alias = {
      ...config.resolve.alias,
      '@/pqcl': path.join(__dirname, 'lib/pqcl'),
      '@/components': path.join(__dirname, 'components')
    }
    return config
  }
}

export default nextConfig 