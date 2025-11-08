# Frontend Toolkit - High-Performance React Components

Production-grade React component library and applications built with Vite + TypeScript + Tailwind CSS.

## 🎯 Overview

**Complete frontend toolkit** matching all 19 backend examples with:
- **Atomic Design System** (atoms, molecules, organisms)
- **Performance-First Components** (virtualization, memoization)
- **19 Production Apps** (one per backend example)
- **Design Tokens** (configurable, composable)
- **TypeScript** (full type safety)

## 🏗️ Monorepo Structure

```
frontend/
├── packages/
│   ├── design-tokens/      # Foundation design tokens
│   ├── atoms/               # Basic components (Button, Input, Badge)
│   ├── molecules/           # Composed components (SearchBar, Card)
│   ├── organisms/           # Complex components (DataTable, Chart)
│   ├── performance/         # Performance utilities
│   ├── state/               # State management patterns
│   └── hooks/               # Reusable React hooks
│
├── apps/
│   ├── 01-rest-api-admin/          # Admin UI for Example 1
│   ├── 02-analytics-dashboard/     # Real-time dashboard for Example 2
│   ├── 03-file-processor-ui/       # File upload UI for Example 3
│   ├── 04-gateway-admin/           # Gateway admin for Example 4
│   ├── 05-export-manager/          # Export UI for Example 5
│   ├── 06-stream-monitor/          # Kappa UI for Example 6
│   ├── 07-event-sourcing-ui/       # Event store UI for Example 7
│   ├── 08-tsdb-dashboard/          # Time-series dashboard for Example 8
│   ├── 09-cache-admin/             # Cache admin for Example 9
│   ├── 10-queue-manager/           # Queue UI for Example 10
│   ├── 11-rate-limit-console/      # Rate limiter console for Example 11
│   ├── 12-lambda-dashboard/        # Lambda architecture UI for Example 12
│   ├── 13-cdc-monitor/             # CDC pipeline UI for Example 13
│   ├── 14-recommendation-ui/       # Recommendations UI for Example 14
│   ├── 15-search-interface/        # Search UI for Example 15 ⭐
│   ├── 16-feature-monitor/         # Feature store UI for Example 16
│   ├── 17-olap-dashboard/          # OLAP dashboard for Example 17
│   ├── 18-trace-viewer/            # Tracing UI for Example 18 ⭐
│   └── 19-probabilistic-console/   # Probabilistic structures UI for Example 19
│
└── .storybook/             # Component documentation
```

## 🚀 Quick Start

### Prerequisites
```bash
node >= 20.x
npm >= 10.x
```

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
# Run all apps in development mode
npm run dev

# Run specific app
cd apps/15-search-interface
npm run dev

# Run Storybook (component docs)
npm run storybook
```

### Build
```bash
# Build all packages and apps
npm run build

# Build specific app
cd apps/15-search-interface
npm run build
```

## 📊 Performance Targets

### Component Performance
```
Metric                    Target          Backend Equivalent
──────────────────────────────────────────────────────────────
Button Render             < 1ms           fast_hash (886K ops/sec)
Input Change Handler      < 5ms           RingBuffer push
Table Scroll (1M rows)    60fps           Virtual scrolling
Search Autocomplete       < 50ms          Search Engine P99
Chart Update              < 100ms         Analytics ingestion
Form Validation           < 10ms          Rate limiter check
State Update              < 16ms (60fps)  LRUCache lookup
```

### Bundle Size Targets
```
Package                   Size            Gzipped
──────────────────────────────────────────────────
Atoms                     < 20KB          < 7KB
Molecules                 < 50KB          < 18KB
Organisms                 < 100KB         < 35KB
Full Toolkit             < 200KB          < 70KB
```

## 🎨 Design Tokens

Configuration-driven design system (similar to backend toolkit pattern):

```typescript
import { tokens } from '@frontend-toolkit/design-tokens';

// Colors
tokens.colors.primary[600]  // #0284c7
tokens.colors.success[500]  // #22c55e

// Spacing (matches 8px grid)
tokens.spacing[4]  // 1rem (16px)

// Typography
tokens.typography.fontSize.lg  // ['1.125rem', { lineHeight: '1.75rem' }]

// Animation (performance-optimized)
tokens.animation.duration.fast  // '150ms'
tokens.animation.easing.smooth  // 'cubic-bezier(...)'

// Performance settings (matching backend patterns)
tokens.performance.virtualScrollOverscan  // 5 (like RingBuffer capacity)
tokens.performance.memoizationCacheSize   // 100 (like LRUCache)
tokens.performance.debounceDelay.normal   // 300ms
```

## 🧩 Atomic Components

### Atoms (Basic Building Blocks)

```typescript
import { Button, Input, Badge, Icon, Spinner } from '@frontend-toolkit/atoms';

// Button with variants (similar to backend service types)
<Button variant="primary" size="md" loading={isLoading}>
  Submit
</Button>

// Input with validation
<Input
  type="email"
  placeholder="Email"
  error={errors.email}
  onChange={handleChange}
/>

// Badge for status
<Badge variant="success">Active</Badge>
```

### Molecules (Composed Components)

```typescript
import { SearchBar, Card, FormField } from '@frontend-toolkit/molecules';

// SearchBar with autocomplete (for Example 15)
<SearchBar
  onSearch={handleSearch}
  suggestions={suggestions}
  debounce={300}  // Performance-optimized
/>

// Card container
<Card title="Metrics" action={<Button>Refresh</Button>}>
  {content}
</Card>
```

### Organisms (Complex Components)

```typescript
import { DataTable, Chart, Form } from '@frontend-toolkit/organisms';

// DataTable with virtualization (60fps with 1M+ rows)
<DataTable
  data={largeDataset}
  columns={columns}
  virtualized={true}
  pageSize={50}
  onSort={handleSort}
/>

// Real-time Chart (for analytics dashboards)
<Chart
  type="line"
  data={metricsData}
  streaming={true}
  updateInterval={1000}
/>
```

## ⚡ Performance Utilities

### Virtual Scrolling (RingBuffer Pattern)

```typescript
import { useVirtualScroll } from '@frontend-toolkit/performance';

const VirtualList = ({ items }) => {
  const { visibleItems, containerRef, scrollHandler } = useVirtualScroll({
    items,
    itemHeight: 50,
    overscan: 5,  // Like RingBuffer capacity planning
  });

  return (
    <div ref={containerRef} onScroll={scrollHandler}>
      {visibleItems.map(item => <Item key={item.id} {...item} />)}
    </div>
  );
};

// Performance: 60fps with 1M+ items
```

### Memoization (LRUCache Pattern)

```typescript
import { useLRUMemo } from '@frontend-toolkit/performance';

const ExpensiveComponent = ({ data }) => {
  // Cache expensive computations (like backend LRUCache)
  const processed = useLRUMemo(
    () => expensiveProcessing(data),
    [data],
    { capacity: 100 }  // LRU cache size
  );

  return <div>{processed}</div>;
};
```

### Web Worker Pool (ObjectPool Pattern)

```typescript
import { useWorkerPool } from '@frontend-toolkit/performance';

const HeavyComputation = () => {
  const workerPool = useWorkerPool({
    workerCount: 4,  // Like backend worker pool
  });

  const handleCompute = async () => {
    const result = await workerPool.execute({
      type: 'PROCESS_DATA',
      payload: largeDataset,
    });
    setResult(result);
  };

  // Offloads to workers (non-blocking UI)
};
```

### Debounce & Throttle

```typescript
import { useDebounce, useThrottle } from '@frontend-toolkit/hooks';

// Debounce search (like backend rate limiting)
const SearchInput = () => {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);  // 300ms delay

  useEffect(() => {
    if (debouncedQuery) {
      fetchResults(debouncedQuery);
    }
  }, [debouncedQuery]);
};

// Throttle scroll events (performance optimization)
const ScrollHandler = () => {
  const throttledScroll = useThrottle(handleScroll, 100);  // Max 10 calls/sec

  return <div onScroll={throttledScroll}>...</div>;
};
```

## 📱 Frontend Apps

### Featured Applications

#### 🔍 **Search Interface** (App 15)
Connects to **Example 15: Full-Text Search Engine**

**Features:**
- Real-time search with autocomplete
- Highlighted results
- Fuzzy matching UI
- 50K+ queries/sec (backend)
- < 50ms autocomplete (P99)

```typescript
// apps/15-search-interface/
<SearchInterface
  apiUrl="http://localhost:8015"
  features={['autocomplete', 'highlight', 'fuzzy']}
/>
```

#### 📊 **Analytics Dashboard** (App 02)
Connects to **Example 2: Real-Time Analytics**

**Features:**
- Real-time metrics charts
- WebSocket streaming
- Event tables (virtualized)
- 1M+ events/min (backend)
- < 10ms UI update lag

#### 🔗 **Trace Viewer** (App 18)
Connects to **Example 18: Distributed Tracing**

**Features:**
- Waterfall trace visualization
- Service dependency graph
- Span filtering
- 1M+ spans/sec ingestion (backend)
- Interactive span details

## 🧪 Testing

```bash
# Run all tests
npm run test

# Run tests for specific package
cd packages/atoms
npm run test

# Run tests with coverage
npm run test -- --coverage
```

## 📚 Storybook

Interactive component documentation:

```bash
# Start Storybook
npm run storybook

# Build static Storybook
npm run build-storybook

# View at http://localhost:6006
```

## 🎯 Best Practices

### 1. Performance-First

```typescript
// ✅ Good: Memoized component
const ExpensiveComponent = memo(({ data }) => {
  return <div>{expensiveRender(data)}</div>;
});

// ❌ Bad: Re-renders on every parent render
const ExpensiveComponent = ({ data }) => {
  return <div>{expensiveRender(data)}</div>;
};
```

### 2. Atomic Composition

```typescript
// ✅ Good: Compose from atoms
const LoginForm = () => (
  <form>
    <FormField>
      <Input type="email" />
    </FormField>
    <Button type="submit">Login</Button>
  </form>
);

// ❌ Bad: Monolithic component
const LoginForm = () => <div className="...">...</div>;
```

### 3. Type Safety

```typescript
// ✅ Good: Fully typed
interface User {
  id: string;
  name: string;
}

const UserCard = ({ user }: { user: User }) => {...};

// ❌ Bad: Any types
const UserCard = ({ user }: { user: any }) => {...};
```

## 🔗 Backend Integration

Each frontend app connects to its corresponding backend:

```typescript
// Example: Search Interface → Search Engine
const SearchApp = () => {
  const { data, loading } = useQuery({
    url: 'http://localhost:8015/api/v1/search',
    params: { q: query, limit: 10 }
  });

  return <SearchResults results={data.results} />;
};
```

### API Clients

```typescript
// Auto-generated from backend OpenAPI
import { SearchEngineClient } from './clients/search-engine';

const client = new SearchEngineClient({
  baseURL: 'http://localhost:8015'
});

const results = await client.search({ q: 'python', limit: 10 });
```

## 🚀 Deployment

### Production Build

```bash
# Build all apps
npm run build

# Output: apps/*/dist/
```

### Docker Deployment

Each app has a Dockerfile:

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY dist ./dist
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables

```bash
# .env.production
VITE_API_URL=https://api.production.com
VITE_WS_URL=wss://api.production.com
```

## 📊 Performance Monitoring

Built-in performance tracking:

```typescript
import { usePerformanceMonitor } from '@frontend-toolkit/hooks';

const App = () => {
  usePerformanceMonitor({
    metrics: ['FCP', 'LCP', 'FID', 'CLS'],
    reportEndpoint: '/api/metrics',
  });

  // Tracks Core Web Vitals
};
```

## 🎓 Learning Resources

- **Design Tokens**: `packages/design-tokens/README.md`
- **Atoms**: `packages/atoms/README.md`
- **Performance**: `packages/performance/README.md`
- **Storybook**: http://localhost:6006
- **TypeScript Docs**: Generated with TypeDoc

## 🌟 Highlights

**What Makes This Special:**

1. **Performance-Optimized**: 60fps, < 1ms renders, virtualization
2. **Atomic Design**: Composable, reusable, maintainable
3. **Type-Safe**: Full TypeScript coverage
4. **Backend-Matched**: 19 apps for 19 backend examples
5. **Production-Ready**: Docker, tests, monitoring
6. **Well-Documented**: Storybook, README, TypeDoc

## 📈 Comparison

| Feature | Our Toolkit | Typical UI Library |
|---------|-------------|-------------------|
| Performance | 60fps, virtualized | Often 30fps |
| Type Safety | 100% TypeScript | Partial or JS |
| Bundle Size | < 70KB gzipped | 100-200KB+ |
| Backend Integration | Built-in for 19 services | Manual |
| Documentation | Storybook + Docs | Limited |
| Design System | Atomic, configurable | Fixed patterns |

## 🛠️ Tech Stack

- **React 18**: Concurrent features, Suspense
- **Vite**: Lightning-fast builds (< 1s)
- **TypeScript**: Full type safety
- **Tailwind CSS**: Atomic styling
- **Zustand**: Lightweight state (< 1KB)
- **React Query**: Server state management
- **Vitest**: Fast testing
- **Storybook**: Component docs

## 📝 License

Same as backend toolkit - see root LICENSE file.

---

Built with ⚡ by the Toolkit Team

Matching **19 backend examples** with **19 frontend apps**!
