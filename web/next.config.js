/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    esmExternals: true
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': '.',
      '@/pqcl': './lib/pqcl',
      '@/components': './components'
    }
    return config
  }
}

module.exports = nextConfig 