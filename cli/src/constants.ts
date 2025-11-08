export interface Pattern {
  name: string;
  value: string;
  description: string;
  recommended: boolean;
  dependencies?: string[];
}

export interface Framework {
  name: string;
  value: string;
  icon: string;
  language: string;
  description: string;
}

export interface Template {
  name: string;
  value: string;
  icon: string;
  description: string;
}

export const PATTERNS: Pattern[] = [
  {
    name: 'Cache',
    value: 'cache',
    description: 'Redis + in-memory caching',
    recommended: true,
    dependencies: ['redis'],
  },
  {
    name: 'Database',
    value: 'database',
    description: 'PostgreSQL with migrations',
    recommended: true,
    dependencies: ['postgresql'],
  },
  {
    name: 'Rate Limiting',
    value: 'ratelimit',
    description: 'Token bucket rate limiting',
    recommended: true,
  },
  {
    name: 'Authentication',
    value: 'auth',
    description: 'JWT + OAuth2 authentication',
    recommended: true,
  },
  {
    name: 'API Gateway',
    value: 'gateway',
    description: 'Reverse proxy + routing',
    recommended: false,
  },
  {
    name: 'Event Bus',
    value: 'events',
    description: 'Pub/sub event system',
    recommended: false,
    dependencies: ['kafka'],
  },
  {
    name: 'Queue',
    value: 'queue',
    description: 'Task queue with workers',
    recommended: false,
    dependencies: ['kafka', 'redis'],
  },
  {
    name: 'File Storage',
    value: 'storage',
    description: 'S3-compatible file storage',
    recommended: false,
  },
  {
    name: 'Search',
    value: 'search',
    description: 'Full-text search',
    recommended: false,
  },
  {
    name: 'Notifications',
    value: 'notifications',
    description: 'Email/SMS/Push notifications',
    recommended: false,
  },
  {
    name: 'Feature Flags',
    value: 'features',
    description: 'Dynamic feature toggles',
    recommended: false,
  },
  {
    name: 'Audit Logging',
    value: 'audit',
    description: 'Audit trail for compliance',
    recommended: false,
  },
  {
    name: 'Metrics',
    value: 'metrics',
    description: 'Prometheus metrics',
    recommended: false,
  },
  {
    name: 'Tracing',
    value: 'tracing',
    description: 'Distributed tracing',
    recommended: false,
  },
  {
    name: 'Pagination',
    value: 'pagination',
    description: 'Cursor + offset pagination',
    recommended: false,
  },
  {
    name: 'Webhooks',
    value: 'webhooks',
    description: 'Webhook delivery system',
    recommended: false,
  },
  {
    name: 'GraphQL',
    value: 'graphql',
    description: 'GraphQL API layer',
    recommended: false,
  },
  {
    name: 'Multi-tenant',
    value: 'multitenant',
    description: 'Multi-tenancy support',
    recommended: false,
  },
  {
    name: 'Scheduler',
    value: 'scheduler',
    description: 'Cron-like job scheduler',
    recommended: false,
  },
];

export const FRAMEWORKS: Framework[] = [
  {
    name: 'FastAPI',
    value: 'fastapi',
    icon: '⚡',
    language: 'python',
    description: 'Modern, fast Python web framework',
  },
  {
    name: 'Django',
    value: 'django',
    icon: '🎸',
    language: 'python',
    description: 'High-level Python web framework',
  },
  {
    name: 'Flask',
    value: 'flask',
    icon: '🌶️',
    language: 'python',
    description: 'Lightweight Python web framework',
  },
  {
    name: 'NestJS',
    value: 'nestjs',
    icon: '🐱',
    language: 'typescript',
    description: 'Progressive Node.js framework',
  },
];

export const TEMPLATES: Template[] = [
  {
    name: 'Monorepo',
    value: 'monorepo',
    icon: '📦',
    description: 'Single repository with multiple services',
  },
  {
    name: 'Microservices',
    value: 'microservices',
    icon: '🔷',
    description: 'Distributed services architecture',
  },
  {
    name: 'Serverless',
    value: 'serverless',
    icon: '☁️',
    description: 'AWS Lambda / GCP Functions ready',
  },
];

export const CLOUD_PROVIDERS = [
  {
    name: 'AWS',
    value: 'aws',
    services: ['ECS', 'EKS', 'Lambda', 'RDS', 'ElastiCache'],
  },
  {
    name: 'GCP',
    value: 'gcp',
    services: ['Cloud Run', 'GKE', 'Cloud Functions', 'Cloud SQL', 'Memorystore'],
  },
  {
    name: 'Azure',
    value: 'azure',
    services: ['Container Apps', 'AKS', 'Functions', 'Database', 'Cache'],
  },
];
