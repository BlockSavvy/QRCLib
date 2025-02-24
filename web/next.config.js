/** @type {import('next').NextConfig} */
const config = {
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
      '@': './app',
      '@/lib': './lib',
      '@/pqcl': './lib/pqcl',
      '@/components': './components'
    }
    
    return config
  }
}

export default config 