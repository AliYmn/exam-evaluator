import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: true, // Skip ESLint during production build
  },
  typescript: {
    ignoreBuildErrors: true, // Skip TypeScript errors during production build
  },
  experimental: {
    serverComponentsExternalPackages: [],
  },
};

export default nextConfig;
