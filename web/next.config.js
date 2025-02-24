import path from 'path'

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    esmExternals: true
  },
  webpack: (config) => {
    config.resolve.modules = [
      'node_modules',
      ...config.resolve.modules || []
    ]
    
    config.resolve.alias = {
      ...config.resolve.alias,
      '@/pqcl/dilithium': path.join(__dirname, 'lib/pqcl/dilithium'),
      '@/components': path.join(__dirname, 'components'),
      '@/lib': path.join(__dirname, 'lib')
    }
    
    return config
  }
}

module.exports = nextConfig 