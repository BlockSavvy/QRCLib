import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

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
      '@/pqcl/dilithium': path.join(__dirname, 'lib/pqcl/dilithium.ts'),
      '@/components': path.join(__dirname, 'components'),
      '@/lib': path.join(__dirname, 'lib')
    }
    
    return config
  }
}

export default config 