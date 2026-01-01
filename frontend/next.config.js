/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: process.env.BACKEND_URL
                    ? `${process.env.BACKEND_URL}/api/:path*`
                    : 'http://127.0.0.1:8000/api/:path*', // Default to local for dev
            },
        ]
    },
}

module.exports = nextConfig
