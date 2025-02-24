/** @type {import('next').NextConfig} */
const config = {
  output: 'standalone',
  experimental: {
    esmExternals: true
  },
  webpack: (config) => {
    config.resolve.modules.push('./');
    return config;
  }
}

export default config 