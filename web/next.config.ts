import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      { source: "/examples/basic", destination: "/sign", permanent: false },
      { source: "/examples/messaging", destination: "/messages", permanent: false },
      { source: "/examples/bitcoin", destination: "/bitcoin", permanent: false },
      { source: "/examples/blockchain", destination: "/", permanent: false },
      { source: "/examples/storage", destination: "/envelope", permanent: false },
      { source: "/examples/api", destination: "/", permanent: false },
    ];
  },
};

export default nextConfig;
