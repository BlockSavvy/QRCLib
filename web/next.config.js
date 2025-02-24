/** @type {import('next').NextConfig} */
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const nextConfig = {
  experimental: {
    esmExternals: true
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, './app'),
      '@/lib': path.resolve(__dirname, './lib'),
      '@/pqcl': path.resolve(__dirname, './lib/pqcl'),
      '@/components': path.resolve(__dirname, './components')
    }
    return config
  }
}

export default nextConfig 