/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    esmExternals: true
  },
  webpack: (config) => {
    // Add PQCL to module directories
    config.resolve.modules = [
      'app',
      'lib',
      'components',
      'node_modules',
      ...config.resolve.modules || []
    ]
    
    // Add path aliases
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': './app',
      '@/lib': './lib',
      '@/pqcl/dilithium': './lib/pqcl/dilithium',
      '@/components': './components'
    }
    
    return config
  }
}

module.exports = nextConfig 