import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

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