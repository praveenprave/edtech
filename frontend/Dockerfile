# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package.json .

# Install Dependencies
RUN npm install

# Copy source code
COPY . .

# Bake in Backend URL for Next.js Config
ARG BACKEND_URL
ENV BACKEND_URL=$BACKEND_URL

# Build
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
