import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: 'Composable Toolkit',
  description: 'Enterprise-grade toolkit for building scalable, composable applications',

  base: '/',

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
  ],

  // Enable Mermaid diagrams
  markdown: {
    config: (md) => {
      // Mermaid plugin will be added here
    },
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    }
  },

  themeConfig: {
    logo: '/logo.svg',

    nav: [
      { text: 'Guide', link: '/guide/introduction' },
      { text: 'Architecture', link: '/architecture/overview' },
      { text: 'API', link: '/api/overview' },
      { text: 'Patterns', link: '/patterns/overview' },
      { text: 'GitHub', link: 'https://github.com/yourusername/toolkit' }
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Introduction',
          items: [
            { text: 'What is Toolkit?', link: '/guide/introduction' },
            { text: 'Quick Start', link: '/guide/quick-start' },
            { text: 'Installation', link: '/guide/installation' },
          ]
        },
        {
          text: 'Core Concepts',
          items: [
            { text: 'Composability', link: '/guide/composability' },
            { text: 'Performance', link: '/guide/performance' },
            { text: 'Testing', link: '/guide/testing' },
          ]
        },
        {
          text: 'Backend',
          items: [
            { text: 'Overview', link: '/guide/backend/overview' },
            { text: 'Configuration', link: '/guide/backend/configuration' },
            { text: 'Caching', link: '/guide/backend/caching' },
            { text: 'Rate Limiting', link: '/guide/backend/rate-limiting' },
          ]
        },
        {
          text: 'Frontend',
          items: [
            { text: 'Overview', link: '/guide/frontend/overview' },
            { text: 'Atomic Design', link: '/guide/frontend/atomic-design' },
            { text: 'Performance Hooks', link: '/guide/frontend/performance-hooks' },
          ]
        }
      ],
      '/architecture/': [
        {
          text: 'Architecture',
          items: [
            { text: 'Overview', link: '/architecture/overview' },
            { text: 'System Design', link: '/architecture/system-design' },
            { text: 'Backend Architecture', link: '/architecture/backend' },
            { text: 'Frontend Architecture', link: '/architecture/frontend' },
            { text: 'Data Flow', link: '/architecture/data-flow' },
            { text: 'Deployment', link: '/architecture/deployment' },
          ]
        }
      ],
      '/api/': [
        {
          text: 'API Reference',
          items: [
            { text: 'Overview', link: '/api/overview' },
            { text: 'Backend APIs', link: '/api/backend' },
            { text: 'Frontend Components', link: '/api/frontend' },
          ]
        }
      ],
      '/patterns/': [
        {
          text: 'Pattern Library',
          items: [
            { text: 'Overview', link: '/patterns/overview' },
            { text: '01 - REST API', link: '/patterns/01-rest-api' },
            { text: '02 - Analytics Engine', link: '/patterns/02-analytics' },
            { text: '03 - File Processor', link: '/patterns/03-file-processor' },
            { text: '04 - API Gateway', link: '/patterns/04-api-gateway' },
            { text: '05 - Data Export', link: '/patterns/05-data-export' },
            { text: '06 - Kappa Architecture', link: '/patterns/06-kappa' },
            { text: '07 - Event Sourcing', link: '/patterns/07-event-sourcing' },
            { text: '08 - TimeSeries DB', link: '/patterns/08-timeseries' },
            { text: '09 - Distributed Cache', link: '/patterns/09-cache' },
            { text: '10 - Message Queue', link: '/patterns/10-message-queue' },
            { text: '11 - Rate Limiter', link: '/patterns/11-rate-limiter' },
            { text: '12 - Lambda Architecture', link: '/patterns/12-lambda' },
            { text: '13 - CDC', link: '/patterns/13-cdc' },
            { text: '14 - Recommendation Engine', link: '/patterns/14-recommendation' },
            { text: '15 - Search System', link: '/patterns/15-search' },
            { text: '16 - Feature Store', link: '/patterns/16-feature-store' },
            { text: '17 - OLAP Dashboard', link: '/patterns/17-olap' },
            { text: '18 - Distributed Tracing', link: '/patterns/18-tracing' },
            { text: '19 - Probabilistic Structures', link: '/patterns/19-probabilistic' },
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/yourusername/toolkit' }
    ],

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024-present'
    },

    search: {
      provider: 'local'
    },

    editLink: {
      pattern: 'https://github.com/yourusername/toolkit/edit/main/docs/:path'
    }
  }
})
