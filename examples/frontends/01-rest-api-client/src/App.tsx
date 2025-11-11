/**
 * REST API Client - E-commerce Inventory Management
 * Example 1: High-Performance REST API (445K RPS, P99 < 100ms)
 *
 * Features:
 * - Product search and filtering
 * - Inventory management
 * - Stock operations (reserve, release, fulfill)
 * - Real-time performance metrics
 *
 * REFACTORED: Now uses unified design system components
 */

import { useState, useEffect } from 'react';
import { Button, Badge, Input, Select } from '@unistax/atoms';
import {
  AppLayout,
  StatsBar,
  LoadingState,
  EmptyState,
  DataCard,
} from '@unistax/layouts';
import { useDebounce } from '@unistax/performance';

interface Product {
  id: string;
  sku: string;
  name: string;
  description: string;
  category: string;
  price: number;
  cost: number;
  status: string;
  tags: string[];
}

interface Inventory {
  id: string;
  product_id: string;
  quantity: number;
  reserved: number;
  reorder_point: number;
  warehouse_location: string;
  status: string;
}

interface Stats {
  total_products?: number;
  total_requests?: number;
  avg_response_time_ms?: number;
  cache_hit_rate?: number;
}

const API_URL = 'http://localhost:8001';

export function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [inventory, setInventory] = useState<Map<string, Inventory>>(new Map());
  const [stats, setStats] = useState<Stats>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const debouncedSearch = useDebounce(searchQuery, 300);

  // Fetch stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/stats`);
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Stats error:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  // Fetch products
  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        let url = `${API_URL}/api/v1/products?limit=50`;

        if (debouncedSearch) {
          url = `${API_URL}/api/v1/products/search/query?q=${encodeURIComponent(debouncedSearch)}`;
        } else if (categoryFilter !== 'all') {
          url = `${API_URL}/api/v1/products/category/${encodeURIComponent(categoryFilter)}`;
        }

        const response = await fetch(url);
        const data = await response.json();
        setProducts(Array.isArray(data) ? data : data.products || []);
      } catch (error) {
        console.error('Products error:', error);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [debouncedSearch, categoryFilter]);

  // Fetch inventory for selected product
  const fetchInventory = async (productId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/inventory/product/${productId}`);
      const data = await response.json();
      setInventory(prev => new Map(prev).set(productId, data));
    } catch (error) {
      console.error('Inventory error:', error);
    }
  };

  // Reserve stock
  const reserveStock = async (productId: string, quantity: number) => {
    try {
      await fetch(`${API_URL}/api/v1/inventory/product/${productId}/reserve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity })
      });
      await fetchInventory(productId);
    } catch (error) {
      console.error('Reserve error:', error);
    }
  };

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'electronics', label: 'Electronics' },
    { value: 'widgets', label: 'Widgets' },
    { value: 'gadgets', label: 'Gadgets' },
    { value: 'tools', label: 'Tools' },
    { value: 'accessories', label: 'Accessories' },
  ];

  // Convert stats to StatsBar format
  const statsData = [
    {
      label: 'Products',
      value: stats.total_products?.toLocaleString() || '0',
    },
    {
      label: 'Requests',
      value: stats.total_requests?.toLocaleString() || '0',
    },
    {
      label: 'Avg Response',
      value: `${stats.avg_response_time_ms?.toFixed(2) || 0}ms`,
      variant: 'success' as const,
    },
    {
      label: 'Cache Hit Rate',
      value: `${((stats.cache_hit_rate || 0) * 100).toFixed(1)}%`,
    },
  ];

  return (
    <AppLayout
      title="E-commerce Inventory"
      description="High-Performance REST API (445K RPS, P99 < 100ms)"
      icon="🛍️"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8000
          </div>
          <div>
            <span className="font-semibold">Powered by:</span> LRUCache (203K+ cache hits/sec)
          </div>
        </div>
      }
    >
      {/* Stats Bar */}
      <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-8 mb-8">
        <StatsBar stats={statsData} variant="compact" />
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search products by name, SKU, or description..."
              fullWidth
              leftIcon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              }
            />
          </div>
          <div className="w-full sm:w-48">
            <Select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              options={categories}
              fullWidth
            />
          </div>
        </div>
      </div>

      {/* Products Grid */}
      {loading ? (
        <LoadingState message="Loading products..." />
      ) : products.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {products.map((product) => (
            <DataCard
              key={product.id}
              title={product.name}
              subtitle={product.sku}
              badge={{
                label: product.status,
                variant: product.status === 'active' ? 'success' : 'secondary',
              }}
              metadata={[
                { label: 'Price', value: `$${product.price.toFixed(2)}` },
                { label: 'Cost', value: `$${product.cost.toFixed(2)}` },
              ]}
              tags={product.tags?.slice(0, 3)}
              onClick={() => {
                setSelectedProduct(product);
                fetchInventory(product.id);
              }}
            >
              <p className="line-clamp-2">{product.description}</p>
              <div className="mt-2">
                <Badge variant="primary" size="sm">{product.category}</Badge>
              </div>
            </DataCard>
          ))}
        </div>
      ) : (
        <EmptyState
          icon="📦"
          title="No products found"
          description="Try adjusting your search or filters to find what you're looking for."
        />
      )}

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedProduct(null)}
        >
          <div
            className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-neutral-900">{selectedProduct.name}</h2>
                  <p className="text-sm text-neutral-500 font-mono">{selectedProduct.sku}</p>
                </div>
                <button
                  onClick={() => setSelectedProduct(null)}
                  className="text-neutral-400 hover:text-neutral-600"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <p className="text-neutral-600 mb-4">{selectedProduct.description}</p>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="p-3 bg-neutral-50 rounded">
                  <div className="text-sm text-neutral-600">Price</div>
                  <div className="text-xl font-bold text-neutral-900">${selectedProduct.price.toFixed(2)}</div>
                </div>
                <div className="p-3 bg-neutral-50 rounded">
                  <div className="text-sm text-neutral-600">Cost</div>
                  <div className="text-xl font-bold text-neutral-900">${selectedProduct.cost.toFixed(2)}</div>
                </div>
              </div>

              {/* Inventory Section */}
              {inventory.has(selectedProduct.id) && (
                <div className="mt-6 p-4 bg-primary-50 rounded-lg border border-primary-200">
                  <h3 className="font-semibold text-primary-900 mb-3">Inventory Status</h3>
                  {(() => {
                    const inv = inventory.get(selectedProduct.id)!;
                    const available = inv.quantity - inv.reserved;
                    return (
                      <>
                        <div className="grid grid-cols-3 gap-3 mb-4">
                          <div>
                            <div className="text-xs text-primary-700">Total</div>
                            <div className="text-lg font-bold text-primary-900">{inv.quantity}</div>
                          </div>
                          <div>
                            <div className="text-xs text-amber-700">Reserved</div>
                            <div className="text-lg font-bold text-amber-900">{inv.reserved}</div>
                          </div>
                          <div>
                            <div className="text-xs text-success-700">Available</div>
                            <div className="text-lg font-bold text-success-900">{available}</div>
                          </div>
                        </div>
                        <div className="text-xs text-primary-700 mb-2">
                          Location: <span className="font-semibold">{inv.warehouse_location}</span>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => reserveStock(selectedProduct.id, 1)}
                          disabled={available <= 0}
                        >
                          Reserve 1 Unit
                        </Button>
                      </>
                    );
                  })()}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
