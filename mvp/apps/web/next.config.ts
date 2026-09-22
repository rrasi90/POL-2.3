import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@pol/tokens", "@pol/types", "@pol/api-client", "@pol/ui"],
};

export default nextConfig;
