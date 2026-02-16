/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,

    // Environment variables
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    },

    // Image domains for avatars
    images: {
        domains: ["lh3.googleusercontent.com", "graph.microsoft.com"],
    },
};

module.exports = nextConfig;
