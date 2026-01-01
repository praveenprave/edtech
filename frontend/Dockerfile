# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package.json .

# Install Dependencies
RUN npm install

# Copy source code
COPY . .

# Build
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
