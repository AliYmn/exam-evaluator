# Multi-stage build for production
FROM node:18-alpine AS deps

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Builder stage
FROM node:18-alpine AS builder

WORKDIR /app

# Build arguments for API URLs
ARG NEXT_PUBLIC_AUTH_API_URL
ARG NEXT_PUBLIC_CONTENT_API_URL
ENV NEXT_PUBLIC_AUTH_API_URL=$NEXT_PUBLIC_AUTH_API_URL
ENV NEXT_PUBLIC_CONTENT_API_URL=$NEXT_PUBLIC_CONTENT_API_URL

# Copy package files
COPY frontend/package*.json ./

# Install all dependencies (including dev)
RUN npm ci

# Copy source files
COPY frontend .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set correct permissions
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
