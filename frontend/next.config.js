/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,

    // Environment variables
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    },

    // Image domains for avatars
    images: {
        domains: ["lh3.googleusercontent.com", "graph.microsoft.com"],
    },

    // Rewrite /api requests to the backend (Solves CORS & Cookie issues)
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
            },
        ]
    },
};

module.exports = nextConfig;
