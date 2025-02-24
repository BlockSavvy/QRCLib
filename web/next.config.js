/** @type {import('next').NextConfig} */
const config = {
  output: 'standalone',
  experimental: {
    esmExternals: true
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': './app',
      '@/lib': './lib',
      '@/components': './components'
    }
    return config
  }
}

export default config 