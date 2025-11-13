# Service Dependency Graph Frontend

Interactive dashboard for visualizing, analyzing, and managing service dependencies.

## Features

### 📊 **Interactive Graph Visualization**
- D3.js force-directed graph with drag-and-drop nodes
- Color-coded service types (API, Gateway, Database, Cache, Queue, Worker)
- Health indicators on each node
- Click to see blast radius
- Zoom and pan controls
- Real-time legend

### 🔍 **Service Management**
- Add/delete services
- Configure service types and endpoints
- View service health scores
- Searchable and sortable table

### 🔗 **Dependency Management**
- Create dependencies between services
- Visualize dependency types (API call, database, queue, etc.)
- Monitor error rates and weights

### 📈 **Comprehensive Analysis**
- **Circular Dependencies**: Detect and visualize cycles
- **Critical Services**: PageRank-based criticality scoring
- **Bottleneck Detection**: Betweenness centrality analysis
- **Deployment Order**: Topological sort for safe deployments
- **Insights & Warnings**: Actionable recommendations

### 🎯 **Impact Analysis**
- Analyze service failures
- Assess deployment impact
- Evaluate breaking changes
- Calculate blast radius
- Risk-level assessment (LOW/MEDIUM/HIGH/CRITICAL)
- Pre-change actions and rollback plans

## Getting Started

### Prerequisites

Ensure the backend is running:
```bash
cd ../../backends/20_service_dependency_graph
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8020
```

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3020`

### Build for Production

```bash
npm run build
npm run preview
```

## Architecture

### Component Structure

```
src/
├── App.tsx                      # Main app with tabs and orchestration
├── main.tsx                     # React entry point
├── types/
│   └── index.ts                 # TypeScript type definitions
└── components/
    ├── DependencyGraph.tsx      # D3.js visualization
    ├── ServiceManagement.tsx    # Service CRUD interface
    ├── DependencyManagement.tsx # Dependency CRUD interface
    ├── AnalysisPanel.tsx        # Analysis results display
    └── ImpactAnalysis.tsx       # Impact analysis tool
```

### Tech Stack

- **React 18** with TypeScript
- **Vite** for fast dev and build
- **Tailwind CSS** for styling
- **D3.js** for graph visualization
- **Unistax Components**: Atoms & Layouts for UI
- **Unistax Performance**: Hooks for optimization

### Unistax Components Used

**Atoms:**
- `Button` - Primary actions, modal controls
- `Input` - Form inputs for services/dependencies
- `Select` - Dropdowns for service types
- `Badge` - Status indicators, labels
- `Spinner` - Loading indicators

**Layouts:**
- `AppLayout` - Main app shell with header/footer
- `StatsBar` - Dashboard metrics
- `DataTable` - Service and dependency tables
- `DataCard` - Analysis result cards
- `Modal` - Create forms
- `Tabs` - Tab navigation
- `EmptyState` - No data placeholders
- `LoadingState` - Loading screens

**Performance:**
- `useDebounce` - Debounce analysis updates

## Usage

### 1. Add Services

Navigate to the **Services** tab and click **Add Service**:
- Enter service name (e.g., "user-service")
- Select service type (API, Gateway, Database, etc.)
- Optionally add endpoints

### 2. Create Dependencies

Go to the **Dependencies** tab and click **Add Dependency**:
- Select source service
- Select target service
- Choose dependency type
- Set weight (importance)

### 3. Visualize Graph

Switch to the **Graph View** tab:
- See your service architecture
- Click nodes to see blast radius
- Drag nodes to reorganize
- Zoom/pan to explore

### 4. Analyze Dependencies

Check the **Analysis** tab for:
- Circular dependency warnings
- Critical service rankings
- Bottleneck identification
- Deployment recommendations

### 5. Assess Impact

Use the **Impact** tab to:
- Select a service
- Choose change type (failure, deployment, breaking change)
- View affected services
- Get risk assessment and mitigation steps

## Color Scheme

Following Unistax design tokens:

- **Primary (Cyan)**: `#00D9FF` - API services
- **Purple**: `#9D4EDD` - Gateway services
- **Green**: `#10B981` - Databases
- **Amber**: `#F59E0B` - Cache services
- **Pink**: `#EC4899` - Message queues
- **Blue**: `#3B82F6` - Worker services
- **Gray**: `#6B7280` - External services

## Performance Optimizations

- **Debounced Analysis**: Prevents excessive API calls
- **Polling**: Auto-refresh every 5 seconds
- **D3 Force Simulation**: Efficient graph rendering
- **Memoization**: React hooks for optimized re-renders
- **Virtual Scrolling**: Ready for large datasets

## API Endpoints

The frontend communicates with these backend endpoints:

- `GET /api/v1/services` - List all services
- `POST /api/v1/services` - Create service
- `DELETE /api/v1/services/{name}` - Delete service
- `GET /api/v1/dependencies` - List dependencies
- `POST /api/v1/dependencies` - Create dependency
- `GET /api/v1/visualize?format=d3` - Get graph data
- `GET /api/v1/analysis/graph` - Get full analysis
- `GET /api/v1/analysis/blast-radius/{service}` - Calculate impact
- `POST /api/v1/analysis/impact` - Analyze change impact

## Development

### Hot Reload

Changes to components automatically hot-reload during development.

### TypeScript

Full type safety with interfaces in `src/types/index.ts`.

### Styling

Uses Tailwind utility classes following Unistax patterns:
- Mobile-first responsive design
- Dark mode support
- 8px spacing grid
- Consistent shadows and borders

## Troubleshooting

### Backend Not Running

If you see connection errors:
1. Start backend: `cd ../../backends/20_service_dependency_graph && uvicorn src.main:app --reload --port 8020`
2. Verify it's running: `curl http://localhost:8020/health`

### Graph Not Rendering

Ensure:
- At least one service is added
- Browser supports SVG
- Console shows no D3.js errors

### CORS Errors

The Vite dev server proxies `/api` to `localhost:8020`. If you change the backend port, update `vite.config.ts`.

## License

Part of the Unistax toolkit. See main repository for license.
