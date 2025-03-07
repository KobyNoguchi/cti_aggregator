/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // This will suppress the hydration warning
  experimental: {
    // This allows Next.js to recover from certain hydration errors
    optimizeCss: true,
  },
}

export default nextConfig;
