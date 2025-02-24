/** @type {import('next').NextConfig} */
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const config = {
  output: 'standalone',
  experimental: {
    esmExternals: true
  },
  webpack: (config) => {
    config.resolve.modules = [
      'node_modules',
      resolve(__dirname),
      ...config.resolve.modules || []
    ]
    
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': resolve(__dirname, 'app'),
      '@/lib': resolve(__dirname, 'lib'),
      '@/pqcl/dilithium': resolve(__dirname, 'lib/pqcl/dilithium.ts'),
      '@/components': resolve(__dirname, 'components')
    }
    
    return config
  }
}

export default config 