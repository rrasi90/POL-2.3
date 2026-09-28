import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: ["@pol/tokens", "@pol/types", "@pol/api-client", "@pol/ui"],
};

export default nextConfig;
