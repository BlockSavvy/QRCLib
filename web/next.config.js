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
      '@/pqcl': './lib/pqcl',
      '@/components': './components',
      '@/lib': './lib'
    }
    
    return config
  }
}

export default config 