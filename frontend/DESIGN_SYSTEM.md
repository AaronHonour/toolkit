# Frontend Design System

**Version:** 2.0
**Date:** 2025-11-10
**Status:** ✅ Implemented

---

## Overview

This document defines the unified design system for all 19 frontend applications in the toolkit. The system ensures visual consistency, improved UX, and maintainable code through reusable components and patterns.

### Design Principles

1. **Consistency** - All apps share the same visual language
2. **Composability** - Components work together seamlessly
3. **Performance** - < 1ms render targets for all components
4. **Accessibility** - WCAG 2.1 AA compliant
5. **Responsive** - Mobile-first, works on all devices

---

## Architecture

### Package Structure

```
frontend/packages/
├── design-tokens/     # Design tokens (colors, spacing, typography)
├── atoms/             # Basic UI components (Button, Input, Badge, etc.)
├── layouts/           # Compound components (AppLayout, DataCard, etc.)
└── performance/       # Performance optimization hooks
```

### Component Hierarchy

```
Layouts (Organisms)
  ↓ uses
Atoms (Molecules)
  ↓ uses
Design Tokens (Atoms)
```

---

## Design Tokens

**Package:** `@frontend-toolkit/design-tokens`
**File:** `/frontend/packages/design-tokens/src/tokens.ts`

### Colors

```typescript
colors: {
  // Primary (Blue)
  primary: { 50, 100, 200, ..., 900, 950 }  // Base: #0ea5e9

  // Neutral (Gray)
  neutral: { 50, 100, 200, ..., 900, 950 }

  // Semantic
  success: { 50, 500, 700 }  // Green
  warning: { 50, 500, 700 }  // Amber
  error: { 50, 500, 700 }    // Red
  info: { 50, 500, 700 }     // Blue
}
```

### Typography

```typescript
fontFamily: {
  sans: ['Inter', 'system-ui', 'sans-serif']
  mono: ['Fira Code', 'Monaco', 'monospace']
}

fontSize: {
  xs: 0.75rem    // 12px
  sm: 0.875rem   // 14px
  base: 1rem     // 16px
  lg: 1.125rem   // 18px
  xl: 1.25rem    // 20px
  2xl: 1.5rem    // 24px
  3xl: 1.875rem  // 30px
  4xl: 2.25rem   // 36px
  5xl: 3rem      // 48px
}

fontWeight: {
  thin: 100
  light: 300
  normal: 400
  medium: 500
  semibold: 600
  bold: 700
  black: 900
}
```

### Spacing

8px base grid system:

```typescript
spacing: {
  0: '0px'
  0.5: '0.125rem'  // 2px
  1: '0.25rem'     // 4px
  2: '0.5rem'      // 8px
  3: '0.75rem'     // 12px
  4: '1rem'        // 16px
  6: '1.5rem'      // 24px
  8: '2rem'        // 32px
  // ... up to 32
}
```

### Shadows

```typescript
shadows: {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)'
  DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1)'
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)'
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)'
  2xl: '0 25px 50px -12px rgb(0 0 0 / 0.25)'
}
```

---

## Atomic Components

**Package:** `@frontend-toolkit/atoms`

### Button

**File:** `/frontend/packages/atoms/src/Button/Button.tsx`

Versatile button component with multiple variants and sizes.

**Props:**
```typescript
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onClick?: () => void;
}
```

**Usage:**
```tsx
import { Button } from '@frontend-toolkit/atoms';

<Button variant="primary" size="md">Save Changes</Button>
<Button variant="outline" leftIcon={<Icon />}>Add Item</Button>
<Button loading>Processing...</Button>
```

### Input

**File:** `/frontend/packages/atoms/src/Input/Input.tsx`

Text input with consistent styling, labels, and error states.

**Props:**
```typescript
interface InputProps {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  // + standard HTML input props
}
```

**Usage:**
```tsx
import { Input } from '@frontend-toolkit/atoms';

<Input
  label="Email"
  type="email"
  placeholder="you@example.com"
  fullWidth
/>
<Input error="Required field" />
```

### Select

**File:** `/frontend/packages/atoms/src/Select/Select.tsx`

Dropdown select with consistent styling.

**Props:**
```typescript
interface SelectProps {
  label?: string;
  error?: string;
  helperText?: string;
  options: Array<{
    value: string;
    label: string;
    disabled?: boolean;
  }>;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  // + standard HTML select props
}
```

**Usage:**
```tsx
import { Select } from '@frontend-toolkit/atoms';

<Select
  label="Category"
  options={[
    { value: 'all', label: 'All Categories' },
    { value: 'electronics', label: 'Electronics' },
  ]}
  fullWidth
/>
```

### Badge

**File:** `/frontend/packages/atoms/src/Badge/Badge.tsx`

Status indicators and labels.

**Props:**
```typescript
interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'neutral';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  dotColor?: string;
}
```

**Usage:**
```tsx
import { Badge } from '@frontend-toolkit/atoms';

<Badge variant="success">Active</Badge>
<Badge variant="error" size="sm">Error</Badge>
<Badge dot dotColor="green">Online</Badge>
```

### Spinner

**File:** `/frontend/packages/atoms/src/Spinner/Spinner.tsx`

Loading indicator.

**Props:**
```typescript
interface SpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}
```

**Usage:**
```tsx
import { Spinner } from '@frontend-toolkit/atoms';

<Spinner size="md" />
```

### ErrorMessage

**File:** `/frontend/packages/atoms/src/ErrorMessage/ErrorMessage.tsx`

User-facing error display.

**Props:**
```typescript
interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  variant?: 'inline' | 'banner' | 'toast';
}
```

**Usage:**
```tsx
import { ErrorMessage } from '@frontend-toolkit/atoms';

<ErrorMessage
  title="Failed to load data"
  message="Unable to connect to the server"
  onRetry={() => refetch()}
  variant="inline"
/>
```

---

## Layout Components

**Package:** `@frontend-toolkit/layouts`

### AppLayout

**File:** `/frontend/packages/layouts/src/AppLayout/AppLayout.tsx`

Main application wrapper providing consistent header, footer, and responsive container.

**Props:**
```typescript
interface AppLayoutProps {
  title: string;
  description?: string;
  icon?: string;  // Emoji or icon
  navigationItems?: Array<{
    label: string;
    href: string;
    active?: boolean;
  }>;
  showFooter?: boolean;
  footerContent?: React.ReactNode;
  headerActions?: React.ReactNode;
  children: React.ReactNode;
}
```

**Usage:**
```tsx
import { AppLayout } from '@frontend-toolkit/layouts';

<AppLayout
  title="E-commerce Inventory"
  description="High-Performance REST API"
  icon="🛍️"
  headerActions={<Button>Add Product</Button>}
>
  {/* Your app content */}
</AppLayout>
```

**Features:**
- Sticky header with title, description, icon
- Optional navigation bar with active state indicators
- Responsive max-width container with proper padding
- Consistent footer
- Optional header actions (buttons, menus)

### StatsBar

**File:** `/frontend/packages/layouts/src/StatsBar/StatsBar.tsx`

Display dashboard statistics consistently.

**Props:**
```typescript
interface StatsBarProps {
  stats: Array<{
    label: string;
    value: string | number;
    trend?: {
      value: number;
      direction: 'up' | 'down';
    };
    variant?: 'default' | 'success' | 'warning' | 'error';
  }>;
  variant?: 'compact' | 'expanded';
}
```

**Usage:**
```tsx
import { StatsBar } from '@frontend-toolkit/layouts';

<StatsBar
  variant="compact"
  stats={[
    { label: 'Total Users', value: '1,234' },
    { label: 'Active', value: '890', variant: 'success' },
    {
      label: 'Revenue',
      value: '$45.2K',
      trend: { value: 12.5, direction: 'up' }
    },
  ]}
/>
```

**Variants:**
- `compact` - Horizontal bar with primary background (for under header)
- `expanded` - Card-based grid with more visual emphasis

### EmptyState

**File:** `/frontend/packages/layouts/src/EmptyState/EmptyState.tsx`

Consistent empty state display.

**Props:**
```typescript
interface EmptyStateProps {
  icon?: React.ReactNode | string;  // Emoji or SVG
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: ButtonProps['variant'];
    leftIcon?: React.ReactNode;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
}
```

**Usage:**
```tsx
import { EmptyState } from '@frontend-toolkit/layouts';

<EmptyState
  icon="📦"
  title="No products found"
  description="Try adjusting your search or filters"
  action={{
    label: "Clear filters",
    onClick: () => clearFilters(),
  }}
/>
```

### LoadingState

**File:** `/frontend/packages/layouts/src/LoadingState/LoadingState.tsx`

Consistent loading indicators.

**Props:**
```typescript
interface LoadingStateProps {
  size?: SpinnerProps['size'];
  message?: string;
  variant?: 'overlay' | 'inline' | 'fullscreen';
}
```

**Usage:**
```tsx
import { LoadingState } from '@frontend-toolkit/layouts';

// Inline in content area
<LoadingState message="Loading products..." />

// Overlay over existing content
<LoadingState variant="overlay" message="Saving..." />

// Full screen loading
<LoadingState variant="fullscreen" />
```

**Variants:**
- `inline` - Display in content area (default)
- `overlay` - Overlay current content with backdrop
- `fullscreen` - Full screen loading indicator

### DataCard

**File:** `/frontend/packages/layouts/src/DataCard/DataCard.tsx`

Reusable card component for displaying data items.

**Props:**
```typescript
interface DataCardProps {
  title: string;
  subtitle?: string;
  badge?: {
    label: string;
    variant?: BadgeProps['variant'];
  };
  metadata?: Array<{
    label: string;
    value: string | number;
  }>;
  tags?: string[];
  onClick?: () => void;
  actions?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}
```

**Usage:**
```tsx
import { DataCard } from '@frontend-toolkit/layouts';

<DataCard
  title="Product Name"
  subtitle="SKU-12345"
  badge={{ label: 'Active', variant: 'success' }}
  metadata={[
    { label: 'Price', value: '$49.99' },
    { label: 'Stock', value: 120 },
  ]}
  tags={['electronics', 'featured']}
  onClick={() => viewDetails()}
>
  <p>Product description...</p>
</DataCard>
```

**Features:**
- Automatic hover effects if onClick provided
- Flexible badge and metadata display
- Tag support
- Optional action buttons
- Responsive layout

### DataTable

**File:** `/frontend/packages/layouts/src/DataTable/DataTable.tsx`

Responsive table for tabular data.

**Props:**
```typescript
interface DataTableProps<T> {
  columns: Array<{
    key: keyof T | string;
    label: string;
    render?: (value: any, row: T) => React.ReactNode;
    width?: string;
    align?: 'left' | 'center' | 'right';
  }>;
  data: T[];
  getRowKey: (row: T) => string | number;
  onRowClick?: (row: T) => void;
  compact?: boolean;
  striped?: boolean;
}
```

**Usage:**
```tsx
import { DataTable } from '@frontend-toolkit/layouts';

<DataTable
  columns={[
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' },
    {
      key: 'status',
      label: 'Status',
      render: (status) => (
        <Badge variant={status === 'active' ? 'success' : 'secondary'}>
          {status}
        </Badge>
      ),
    },
  ]}
  data={users}
  getRowKey={(user) => user.id}
  onRowClick={(user) => viewUser(user)}
  striped
/>
```

---

## Usage Patterns

### Basic Application Structure

```tsx
import { AppLayout, StatsBar, LoadingState, EmptyState } from '@frontend-toolkit/layouts';
import { Button, Input, Select } from '@frontend-toolkit/atoms';

export function MyApp() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);

  return (
    <AppLayout
      title="My Application"
      description="Application description"
      icon="🚀"
    >
      {/* Stats section */}
      <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
        <StatsBar variant="compact" stats={stats} />
      </div>

      {/* Filters/Search */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <div className="flex gap-4">
          <Input placeholder="Search..." fullWidth />
          <Select options={categories} />
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <LoadingState message="Loading data..." />
      ) : data.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data.map(item => (
            <DataCard key={item.id} {...item} />
          ))}
        </div>
      ) : (
        <EmptyState
          icon="📭"
          title="No data found"
          description="Try adjusting your filters"
        />
      )}
    </AppLayout>
  );
}
```

### Form Patterns

```tsx
import { Input, Select, Button, ErrorMessage } from '@frontend-toolkit/atoms';

function MyForm() {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <ErrorMessage
          message={error}
          onDismiss={() => setError('')}
        />
      )}

      <div className="space-y-4">
        <Input
          label="Name"
          name="name"
          required
          fullWidth
        />

        <Select
          label="Category"
          name="category"
          options={categories}
          fullWidth
        />

        <div className="flex gap-3">
          <Button
            type="submit"
            variant="primary"
            loading={loading}
          >
            Submit
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
          >
            Cancel
          </Button>
        </div>
      </div>
    </form>
  );
}
```

### Data Display Patterns

**Grid of Cards:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(item => (
    <DataCard
      key={item.id}
      title={item.title}
      subtitle={item.subtitle}
      metadata={item.metadata}
      onClick={() => viewItem(item.id)}
    />
  ))}
</div>
```

**Table:**
```tsx
<DataTable
  columns={columns}
  data={data}
  getRowKey={(row) => row.id}
  onRowClick={(row) => viewDetails(row)}
/>
```

---

## Migration Guide

### Step 1: Update package.json

Add the new packages to your app:

```json
{
  "dependencies": {
    "@frontend-toolkit/atoms": "*",
    "@frontend-toolkit/layouts": "*",
    "@frontend-toolkit/performance": "*",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
```

### Step 2: Replace Manual Layouts

**Before:**
```tsx
<div className="min-h-screen bg-neutral-50">
  <header className="bg-white shadow-sm border-b">
    <div className="max-w-7xl mx-auto px-4 py-4">
      <h1>My App</h1>
    </div>
  </header>

  <main className="max-w-7xl mx-auto px-4 py-8">
    {/* content */}
  </main>

  <footer>...</footer>
</div>
```

**After:**
```tsx
<AppLayout title="My App" description="..." icon="🚀">
  {/* content */}
</AppLayout>
```

### Step 3: Replace Raw HTML Inputs

**Before:**
```tsx
<input
  type="text"
  className="px-4 py-2 border rounded..."
/>
```

**After:**
```tsx
<Input placeholder="..." fullWidth />
```

### Step 4: Replace Custom Loading States

**Before:**
```tsx
{loading && (
  <div className="text-center py-12">
    <div className="animate-spin..."></div>
    <p>Loading...</p>
  </div>
)}
```

**After:**
```tsx
{loading && <LoadingState message="Loading..." />}
```

### Step 5: Standardize Empty States

**Before:**
```tsx
{data.length === 0 && (
  <div className="text-center">
    <p>No data</p>
  </div>
)}
```

**After:**
```tsx
{data.length === 0 && (
  <EmptyState
    icon="📭"
    title="No data found"
    description="Try adjusting your filters"
  />
)}
```

---

## Best Practices

### Component Usage

1. **Always use AppLayout** for consistent headers/footers
2. **Use atomic components** instead of raw HTML elements
3. **Use LoadingState** for all loading indicators
4. **Use EmptyState** for all empty views
5. **Use DataCard** for grid layouts
6. **Use DataTable** for tabular data

### Styling

1. **Use Tailwind utilities** for custom styling
2. **Follow the 8px spacing grid** (space-2, space-4, space-6, space-8)
3. **Use design token colors** (primary-*, neutral-*, success-*, etc.)
4. **Maintain responsive padding** (px-4 sm:px-6 lg:px-8)

### Responsive Design

1. **Mobile-first approach** - Use `md:` and `lg:` prefixes
2. **Responsive grids** - `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
3. **Responsive flex** - `flex-col sm:flex-row`
4. **AppLayout handles** container responsive padding automatically

### Performance

1. **All components use React.memo** for optimization
2. **Use performance hooks** from `@frontend-toolkit/performance`
3. **Lazy load images** and heavy components
4. **Debounce search inputs** with `useDebounce`

---

## Component Reference Summary

### Atoms
| Component | Purpose | When to Use |
|-----------|---------|-------------|
| Button | Primary actions | Forms, toolbars, CTAs |
| Input | Text input | Forms, search, filters |
| Select | Dropdown selection | Filters, forms with options |
| Badge | Status indicators | Product status, labels, counts |
| Spinner | Loading indicator | Inline loading (use LoadingState for layouts) |
| ErrorMessage | User-facing errors | API errors, validation errors |

### Layouts
| Component | Purpose | When to Use |
|-----------|---------|-------------|
| AppLayout | Page wrapper | Every app main component |
| StatsBar | Dashboard metrics | Apps with real-time statistics |
| LoadingState | Loading screens | While fetching data |
| EmptyState | Empty views | No search results, empty lists |
| DataCard | Item display | Grid of products, users, etc. |
| DataTable | Tabular data | Lists, reports, admin views |

---

## Examples

See migrated applications:
- **App 01 (REST API Client)**: `/frontend/apps/01-rest-api-client/src/App.tsx` - Complete example with all components

---

## Support & Questions

For questions or issues with the design system:
1. Review this documentation
2. Check the component source code in `/frontend/packages/`
3. See migrated app examples in `/frontend/apps/01-rest-api-client/`

---

**Last Updated:** 2025-11-10
**Maintained By:** Frontend Team
