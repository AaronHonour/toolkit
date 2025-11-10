# Dockerfile for VitePress Documentation Site

FROM node:20-alpine as base

WORKDIR /app

# =============================================================================
# Development
# =============================================================================
FROM base as development

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy source
COPY . .

# Expose VitePress port
EXPOSE 5173

# Start dev server
CMD ["npm", "run", "docs:dev", "--", "--host", "0.0.0.0"]

# =============================================================================
# Builder
# =============================================================================
FROM base as builder

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy source
COPY . .

# Build static site
RUN npm run docs:build

# =============================================================================
# Production
# =============================================================================
FROM nginx:alpine as production

# Copy built static files
COPY --from=builder /app/.vitepress/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
