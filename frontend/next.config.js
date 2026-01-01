/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: process.env.BACKEND_URL
                    ? `${process.env.BACKEND_URL}/api/:path*`
                    : 'https://rag-backend-wztetzjbwq-uc.a.run.app/api/:path*', // Default to Prod if Env Missing
            },
        ]
    },
}

module.exports = nextConfig
