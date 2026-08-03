import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    // Pins the project root to this folder. Without it, Turbopack can get
    // confused by a stray lockfile elsewhere on disk (e.g. a Windows user
    // profile folder) and infer the wrong root directory.
    root: __dirname,
  },
};

export default nextConfig;
