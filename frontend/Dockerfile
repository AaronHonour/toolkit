# Multi-stage Dockerfile for Frontend Toolkit
# Optimized for size, security, and build speed

# =============================================================================
# Stage 1: Dependencies
# =============================================================================
FROM node:20-alpine as dependencies

# Set working directory
WORKDIR /app

# Install dependencies only when needed
COPY package.json package-lock.json* ./
COPY packages/atoms/package.json ./packages/atoms/
COPY packages/performance/package.json ./packages/performance/
COPY packages/design-tokens/package.json ./packages/design-tokens/

# Install dependencies with frozen lockfile
RUN npm ci --prefer-offline --no-audit

# =============================================================================
# Stage 2: Builder
# =============================================================================
FROM node:20-alpine as builder

WORKDIR /app

# Copy dependencies from previous stage
COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=dependencies /app/packages ./packages

# Copy source code
COPY . .

# Build all packages
RUN npm run build

# Build production bundles
ENV NODE_ENV=production
RUN npm run build:prod || npm run build

# =============================================================================
# Stage 3: Production Runtime (Nginx)
# =============================================================================
FROM nginx:alpine as production

# Copy custom nginx configuration
COPY frontend/nginx.conf /etc/nginx/nginx.conf

# Copy built static files
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/packages/atoms/dist /usr/share/nginx/html/atoms
COPY --from=builder /app/packages/performance/dist /usr/share/nginx/html/performance
COPY --from=builder /app/packages/design-tokens/dist /usr/share/nginx/html/design-tokens

# Create non-root user
RUN addgroup -g 1000 toolkit && \
    adduser -D -u 1000 -G toolkit toolkit && \
    chown -R toolkit:toolkit /usr/share/nginx/html && \
    chown -R toolkit:toolkit /var/cache/nginx && \
    chown -R toolkit:toolkit /var/log/nginx && \
    chown -R toolkit:toolkit /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R toolkit:toolkit /var/run/nginx.pid

USER toolkit

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8080/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# Stage 4: Development Runtime
# =============================================================================
FROM node:20-alpine as development

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 3000

# Start development server with hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# =============================================================================
# Stage 5: Testing Runtime
# =============================================================================
FROM node:20-alpine as testing

WORKDIR /app

# Install dependencies including Playwright browsers
COPY package.json package-lock.json* ./
RUN npm ci

# Install Playwright browsers
RUN npx playwright install --with-deps chromium

# Copy source code
COPY . .

# Run tests by default
CMD ["npm", "test"]
