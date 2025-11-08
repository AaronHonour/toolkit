# Frontend Architecture

The frontend is built with **React 18** and **TypeScript**, following **Atomic Design** principles for maximum composability and reusability.

## Package Organization

```mermaid
graph TB
    subgraph "Monorepo Structure"
        ROOT[Frontend Root<br/>Turbo Orchestration]
    end

    subgraph "Foundation Packages"
        TOKENS[Design Tokens<br/>Colors, Spacing, Typography]
        UTILS[Utils<br/>Shared Utilities]
    end

    subgraph "Component Packages"
        ATOMS[Atoms<br/>Button, Input, Badge, etc.]
        MOLECULES[Molecules<br/>Form groups, Cards]
        ORGANISMS[Organisms<br/>Navigation, Modals]
    end

    subgraph "Performance Packages"
        PERF[Performance<br/>6 Hooks]
        MONITOR[Monitoring<br/>FPS, Memory]
    end

    subgraph "Applications"
        APP1[App 01-10<br/>Core Examples]
        APP2[App 11-19<br/>Advanced Patterns]
    end

    ROOT --> TOKENS
    ROOT --> UTILS

    ATOMS --> TOKENS
    MOLECULES --> ATOMS
    MOLECULES --> TOKENS
    ORGANISMS --> MOLECULES
    ORGANISMS --> ATOMS

    PERF --> UTILS
    MONITOR --> UTILS

    APP1 --> ATOMS
    APP1 --> MOLECULES
    APP1 --> ORGANISMS
    APP1 --> PERF
    APP1 --> TOKENS

    APP2 --> ATOMS
    APP2 --> MOLECULES
    APP2 --> ORGANISMS
    APP2 --> PERF
    APP2 --> TOKENS
```

## Atomic Design System

Following Brad Frost's Atomic Design methodology:

```mermaid
graph LR
    subgraph "Atoms"
        A1[Button]
        A2[Input]
        A3[Badge]
        A4[Spinner]
        A5[Icon]
    end

    subgraph "Molecules"
        M1[Form Field<br/>Input + Label + Error]
        M2[Search Bar<br/>Input + Icon + Button]
        M3[Badge Group<br/>Multiple Badges]
        M4[Loading Card<br/>Spinner + Text]
    end

    subgraph "Organisms"
        O1[Form<br/>Multiple Fields + Submit]
        O2[Navigation<br/>Logo + Menu + Search]
        O3[Data Table<br/>Headers + Rows + Pagination]
        O4[Modal<br/>Overlay + Card + Actions]
    end

    subgraph "Templates"
        T1[Dashboard Layout]
        T2[Form Layout]
        T3[List Layout]
    end

    A1 --> M1
    A1 --> M2
    A2 --> M1
    A2 --> M2
    A3 --> M3
    A4 --> M4

    M1 --> O1
    M2 --> O2
    M1 --> O3

    O1 --> T2
    O2 --> T1
    O3 --> T3
```

### Atoms

Smallest building blocks - cannot be broken down further.

**Button Component Architecture**:

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> Hover: Mouse Enter
    Idle --> Focus: Keyboard Focus
    Idle --> Loading: onClick (async)
    Idle --> Disabled: disabled=true

    Hover --> Idle: Mouse Leave
    Hover --> Active: Mouse Down

    Active --> Idle: Mouse Up
    Active --> Loading: onClick (async)

    Focus --> Idle: Blur
    Focus --> Loading: Enter Key

    Loading --> Idle: Promise Resolved
    Loading --> Error: Promise Rejected

    Error --> Idle: Timeout

    Disabled --> Idle: disabled=false
```

**Example Button Component**:
```tsx
import { memo, forwardRef } from 'react'
import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { Spinner } from '../Spinner'

type ButtonVariant = 'primary' | 'secondary' | 'success' | 'danger' | 'ghost'
type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  loading?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
}

export const Button = memo(forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      disabled,
      leftIcon,
      rightIcon,
      children,
      className = '',
      ...props
    },
    ref
  ) {
    const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2'

    const variantClasses = {
      primary: 'bg-primary-500 text-white hover:bg-primary-600 focus:ring-primary-500',
      secondary: 'bg-secondary-500 text-white hover:bg-secondary-600 focus:ring-secondary-500',
      // ... other variants
    }

    const sizeClasses = {
      xs: 'px-2 py-1 text-xs',
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
      xl: 'px-8 py-4 text-xl',
    }

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
        {...props}
      >
        {loading && <Spinner size="sm" className="mr-2" />}
        {leftIcon && <span className="mr-2">{leftIcon}</span>}
        {children}
        {rightIcon && <span className="ml-2">{rightIcon}</span>}
      </button>
    )
  }
))
```

**Performance**: Button renders in < 1ms (memoized, optimized reconciliation)

### Design Tokens

Centralized design system with semantic tokens.

```mermaid
graph TB
    subgraph "Primitive Tokens"
        COLORS[Color Palette<br/>blue-50 to blue-900]
        SPACE[Spacing Scale<br/>0.25rem to 24rem]
        TYPO[Typography<br/>Font families, sizes]
    end

    subgraph "Semantic Tokens"
        PRIMARY[Primary Colors<br/>brand colors]
        NEUTRAL[Neutral Colors<br/>text, background]
        STATUS[Status Colors<br/>success, error, warning]
    end

    subgraph "Component Tokens"
        BTN[Button Tokens<br/>sizes, variants]
        INPUT[Input Tokens<br/>sizes, states]
        BADGE[Badge Tokens<br/>variants]
    end

    COLORS --> PRIMARY
    COLORS --> NEUTRAL
    COLORS --> STATUS

    PRIMARY --> BTN
    NEUTRAL --> BTN
    STATUS --> BADGE

    SPACE --> BTN
    SPACE --> INPUT
    TYPO --> BTN
    TYPO --> INPUT
```

**Example Token Structure**:
```typescript
// packages/design-tokens/src/colors.ts
export const colors = {
  // Primitive colors
  blue: {
    50: '#eff6ff',
    100: '#dbeafe',
    // ... 200-800
    900: '#1e3a8a',
  },

  // Semantic tokens
  primary: {
    50: 'var(--color-blue-50)',
    500: 'var(--color-blue-500)',
    900: 'var(--color-blue-900)',
  },

  // Status tokens
  success: {
    light: 'var(--color-green-100)',
    default: 'var(--color-green-500)',
    dark: 'var(--color-green-700)',
  },
}

// packages/design-tokens/src/spacing.ts
export const spacing = {
  0: '0',
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  // ... up to 96
}
```

## Performance Architecture

### Performance Hooks

Six specialized hooks for common performance patterns:

```mermaid
graph TB
    subgraph "Computation Optimization"
        LRU[useLRUMemo<br/>300K+ ops/sec<br/>LRU Cache]
        MEMO[useMemo<br/>React built-in]
    end

    subgraph "Event Optimization"
        DEBOUNCE[useDebounce<br/>±10ms accuracy<br/>300ms default]
        THROTTLE[useThrottle<br/>Rate limiting<br/>Configurable]
    end

    subgraph "Rendering Optimization"
        VIRTUAL[useVirtualScroll<br/>60fps @ 1M+ items<br/>Windowing]
        WORKER[useWorkerPool<br/>Background processing<br/>4 workers default]
    end

    subgraph "Monitoring"
        PERF[usePerformanceMonitor<br/>FPS tracking<br/>Memory usage]
    end

    LRU -.faster than.-> MEMO
    DEBOUNCE -.complements.-> THROTTLE
    VIRTUAL --> PERF
    WORKER --> PERF
```

### useLRUMemo Implementation

High-performance LRU memoization hook:

```mermaid
sequenceDiagram
    participant Component
    participant useLRUMemo
    participant LRUCache
    participant ComputeFn

    Component->>useLRUMemo: useLRUMemo(fn, deps, {maxSize: 100})
    useLRUMemo->>useLRUMemo: serialize(deps) → key

    alt Cache Hit
        useLRUMemo->>LRUCache: get(key)
        LRUCache-->>useLRUMemo: cached_value
        LRUCache->>LRUCache: move_to_front(key)
        useLRUMemo-->>Component: cached_value [< 3μs]
    else Cache Miss
        useLRUMemo->>ComputeFn: fn()
        ComputeFn-->>useLRUMemo: computed_value
        useLRUMemo->>LRUCache: set(key, computed_value)

        alt Cache Full
            LRUCache->>LRUCache: evict_least_recently_used()
        end

        useLRUMemo-->>Component: computed_value
    end
```

**Performance**: 300K+ cache lookups/sec, < 3μs per hit

**Example**:
```typescript
import { useLRUMemo } from '@composable/performance'

function DataVisualization({ data, filters }) {
  // Cache last 100 computation results
  const processedData = useLRUMemo(
    () => {
      // Expensive data processing
      return data
        .filter(applyFilters(filters))
        .map(transform)
        .sort(customSort)
    },
    [data, filters],
    { maxSize: 100 }
  )

  return <Chart data={processedData} />
}
```

### useVirtualScroll Implementation

Efficient rendering of large lists:

```mermaid
graph TB
    subgraph "Virtual Scroll Algorithm"
        SCROLL[Scroll Event] --> CALC[Calculate Viewport]
        CALC --> VISIBLE[Determine Visible Items]
        VISIBLE --> OVERSCAN[Add Overscan Buffer]
        OVERSCAN --> RENDER[Render Window]
    end

    subgraph "Performance Optimization"
        RAF[requestAnimationFrame] --> BATCH[Batch Updates]
        BATCH --> MEMO[Memoize Items]
        MEMO --> RECYCLE[Recycle DOM Nodes]
    end

    SCROLL --> RAF
    OVERSCAN --> RECYCLE
```

**Performance**: 60fps with 1M+ items

**Example**:
```typescript
import { useVirtualScroll } from '@composable/performance'

function LargeList({ items }) {
  const {
    virtualItems,      // Only items in viewport + overscan
    totalHeight,       // Total scrollable height
    containerRef,      // Attach to scroll container
  } = useVirtualScroll({
    items,
    itemHeight: 50,    // Fixed or dynamic
    overscan: 5,       // Buffer items above/below
    estimateSize: (item) => item.height,  // For dynamic heights
  })

  return (
    <div
      ref={containerRef}
      style={{ height: '500px', overflow: 'auto' }}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {virtualItems.map(({ item, index, style }) => (
          <div key={item.id} style={style}>
            <ItemComponent item={item} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

### useDebounce Implementation

```mermaid
sequenceDiagram
    participant User
    participant Input
    participant useDebounce
    participant Timer
    participant Effect

    User->>Input: type "a"
    Input->>useDebounce: setValue("a")
    useDebounce->>Timer: clearTimeout(previous)
    useDebounce->>Timer: setTimeout(300ms)

    User->>Input: type "b" (100ms later)
    Input->>useDebounce: setValue("ab")
    useDebounce->>Timer: clearTimeout(previous)
    useDebounce->>Timer: setTimeout(300ms)

    Note over Timer: Wait 300ms (no more input)

    Timer->>useDebounce: timeout fired
    useDebounce->>useDebounce: setDebouncedValue("ab")
    useDebounce->>Effect: trigger useEffect
    Effect->>Effect: performSearch("ab")
```

**Performance**: ±10ms accuracy

**Example**:
```typescript
import { useDebounce } from '@composable/performance'
import { useState, useEffect } from 'react'

function SearchComponent() {
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 300)

  useEffect(() => {
    if (debouncedSearch) {
      // Only called 300ms after user stops typing
      performSearch(debouncedSearch)
    }
  }, [debouncedSearch])

  return (
    <input
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      placeholder="Search..."
    />
  )
}
```

### useWorkerPool Implementation

Background processing without blocking UI:

```mermaid
graph TB
    subgraph "Main Thread"
        COMP[Component]
        POOL[Worker Pool Manager]
    end

    subgraph "Worker Threads"
        W1[Worker 1]
        W2[Worker 2]
        W3[Worker 3]
        W4[Worker 4]
    end

    subgraph "Task Queue"
        Q[FIFO Queue]
    end

    COMP --> POOL
    POOL --> Q
    Q --> W1
    Q --> W2
    Q --> W3
    Q --> W4

    W1 -.result.-> POOL
    W2 -.result.-> POOL
    W3 -.result.-> POOL
    W4 -.result.-> POOL
    POOL -.result.-> COMP
```

**Example**:
```typescript
import { useWorkerPool } from '@composable/performance'

function ImageProcessor({ images }) {
  const { execute, isProcessing } = useWorkerPool({
    workerCount: 4,
    workerScript: '/workers/image-processor.js',
  })

  const processImages = async () => {
    // Distribute work across 4 workers
    const results = await execute({
      type: 'processImages',
      images: images,
    })

    setProcessedImages(results)
  }

  return (
    <button onClick={processImages} disabled={isProcessing}>
      {isProcessing ? 'Processing...' : 'Process Images'}
    </button>
  )
}
```

## State Management

### Component State Architecture

```mermaid
graph TB
    subgraph "Local State"
        US[useState<br/>Component-local]
        UR[useReducer<br/>Complex state]
    end

    subgraph "Shared State"
        CTX[Context API<br/>Tree-scoped]
        MEMO[Memoized Context<br/>Performance]
    end

    subgraph "Server State"
        CACHE[React Query<br/>Data caching]
        OPTIMISTIC[Optimistic Updates]
    end

    subgraph "URL State"
        PARAMS[URL Params]
        QUERY[Query String]
    end

    US --> CTX
    UR --> CTX
    CTX --> MEMO
    CACHE --> OPTIMISTIC
```

**Example Architecture**:
```typescript
// Local state
const [count, setCount] = useState(0)

// Complex state with reducer
const [state, dispatch] = useReducer(reducer, initialState)

// Shared state with context
const ThemeContext = createContext()

// Server state with caching
const { data, isLoading } = useQuery('users', fetchUsers)

// URL state
const [searchParams, setSearchParams] = useSearchParams()
```

## Build and Bundle Optimization

### Build Pipeline

```mermaid
graph LR
    subgraph "Source"
        TSX[.tsx files]
        CSS[.css files]
        ASSETS[Assets]
    end

    subgraph "Vite Pipeline"
        ESBUILD[esbuild<br/>Transform]
        ROLLUP[Rollup<br/>Bundle]
        TERSER[Terser<br/>Minify]
    end

    subgraph "Optimizations"
        SPLIT[Code Splitting]
        TREE[Tree Shaking]
        COMPRESS[Compression]
    end

    subgraph "Output"
        CHUNKS[Optimized Chunks]
        PRELOAD[Preload Hints]
        MAP[Source Maps]
    end

    TSX --> ESBUILD
    CSS --> ESBUILD
    ASSETS --> ROLLUP

    ESBUILD --> ROLLUP
    ROLLUP --> TERSER

    TERSER --> SPLIT
    SPLIT --> TREE
    TREE --> COMPRESS

    COMPRESS --> CHUNKS
    COMPRESS --> PRELOAD
    COMPRESS --> MAP
```

### Code Splitting Strategy

```typescript
// Route-based splitting
import { lazy, Suspense } from 'react'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Settings = lazy(() => import('./pages/Settings'))

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  )
}

// Component-based splitting
const HeavyChart = lazy(() => import('./components/HeavyChart'))

// Vendor splitting (vite.config.ts)
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['@composable/atoms'],
        },
      },
    },
  },
}
```

## Testing Strategy

### Component Testing Pyramid

```mermaid
graph TB
    subgraph "Testing Pyramid"
        E2E[E2E Tests<br/>Playwright<br/>5%]
        INT[Integration Tests<br/>Testing Library<br/>15%]
        UNIT[Unit Tests<br/>Vitest<br/>80%]
    end

    E2E --> INT
    INT --> UNIT
```

### Test Structure

```typescript
// Button.test.tsx
import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  describe('Rendering', () => {
    it('should render with children', () => {
      render(<Button>Click me</Button>)
      expect(screen.getByRole('button')).toHaveTextContent('Click me')
    })

    it('should render all variants', () => {
      const { rerender } = render(<Button variant="primary">Primary</Button>)
      expect(screen.getByRole('button')).toHaveClass('bg-primary-500')

      rerender(<Button variant="secondary">Secondary</Button>)
      expect(screen.getByRole('button')).toHaveClass('bg-secondary-500')
    })
  })

  describe('Interactions', () => {
    it('should call onClick when clicked', async () => {
      const handleClick = vi.fn()
      const user = userEvent.setup()

      render(<Button onClick={handleClick}>Click</Button>)
      await user.click(screen.getByRole('button'))

      expect(handleClick).toHaveBeenCalledTimes(1)
    })
  })

  describe('Performance', () => {
    it('should render quickly (< 5ms)', () => {
      const start = performance.now()
      render(<Button>Performance Test</Button>)
      const end = performance.now()

      expect(end - start).toBeLessThan(5)
    })
  })
})
```

## Deployment

### Production Build Checklist

```mermaid
graph TB
    START[Start Build] --> LINT[Run Linting]
    LINT --> TYPE[Type Check]
    TYPE --> TEST[Run Tests]
    TEST --> BUILD[Production Build]

    BUILD --> ANALYZE[Analyze Bundle]
    ANALYZE --> CHECK{Size OK?}

    CHECK -->|Yes| COMPRESS[Compress Assets]
    CHECK -->|No| OPTIMIZE[Optimize Bundle]
    OPTIMIZE --> BUILD

    COMPRESS --> DEPLOY[Deploy to CDN]
    DEPLOY --> VERIFY[Verify Deployment]
    VERIFY --> DONE[Done]
```

**Build Command**:
```bash
# Full production build
npm run build

# Build with analysis
npm run build -- --mode production --analyze

# Expected output:
# dist/
#   assets/
#     index-a1b2c3d4.js       # 45 KB
#     vendor-e5f6g7h8.js      # 120 KB (React, etc)
#     ui-i9j0k1l2.js          # 30 KB (Components)
```

---

Next: [Pattern Library](/patterns/overview) | [API Reference](/api/overview)
