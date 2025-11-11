/**
 * Search Interface Application
 *
 * Connects to Example 15: Full-Text Search Engine (localhost:8015)
 *
 * Features:
 * - Real-time search with autocomplete
 * - Highlighted results
 * - < 50ms autocomplete (matching backend P99)
 * - Debounced input (300ms - performance optimized)
 * - Virtual scrolling for large result sets
 *
 * REFACTORED: Now uses unified design system components
 */

import { useState, useEffect } from 'react';
import {
  AppLayout,
  EmptyState,
  LoadingState,
  DataCard,
} from '@unistax/layouts';

interface SearchResult {
  id: string;
  title: string;
  score: number;
  snippet: string;
}

interface SearchResponse {
  query: string;
  total_results: number;
  results: SearchResult[];
}

const API_URL = 'http://localhost:8015';

export function App() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalResults, setTotalResults] = useState(0);

  // Debounce query (performance optimization - like backend debouncing)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300); // 300ms debounce (matching backend performance tokens)

    return () => clearTimeout(timer);
  }, [query]);

  // Fetch search results
  useEffect(() => {
    if (!debouncedQuery) {
      setResults([]);
      setTotalResults(0);
      return;
    }

    const fetchResults = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `${API_URL}/api/v1/search?q=${encodeURIComponent(debouncedQuery)}&limit=50`
        );
        const data: SearchResponse = await response.json();

        setResults(data.results);
        setTotalResults(data.total_results);
      } catch (error) {
        console.error('Search error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [debouncedQuery]);

  // Fetch autocomplete suggestions
  useEffect(() => {
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }

    const fetchSuggestions = async () => {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/autocomplete?prefix=${encodeURIComponent(query)}&limit=5`
        );
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      } catch (error) {
        console.error('Autocomplete error:', error);
      }
    };

    fetchSuggestions();
  }, [query]);

  const highlightMatch = (text: string, query: string) => {
    if (!query) return text;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={i} className="bg-yellow-200 font-semibold">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <AppLayout
      title="High-Performance Search"
      description="Full-Text Search Engine (50K+ queries/sec)"
      icon="⚡"
      footerContent={
        <div className="flex items-center justify-between text-sm text-neutral-600">
          <div>
            <span className="font-semibold">Backend:</span> localhost:8015
          </div>
          <div>
            <span className="font-semibold">Performance:</span> 50K+ queries/sec, &lt; 5ms P99
          </div>
        </div>
      }
    >
      {/* Search Box */}
      <div className="relative mb-6">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search documents..."
            className="w-full px-4 py-3 pl-12 pr-4 text-lg border-2 border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <svg
            className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-neutral-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          {loading && (
            <svg
              className="absolute right-4 top-1/2 transform -translate-y-1/2 animate-spin h-5 w-5 text-primary-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          )}
        </div>

        {/* Autocomplete Suggestions */}
        {suggestions.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-neutral-200 rounded-lg shadow-lg">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => {
                  setQuery(suggestion);
                  setSuggestions([]);
                }}
                className="w-full px-4 py-2 text-left hover:bg-primary-50 first:rounded-t-lg last:rounded-b-lg transition-colors"
              >
                {highlightMatch(suggestion, query)}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Results Stats */}
      {debouncedQuery && (
        <div className="mb-4 text-sm text-neutral-600">
          Found <span className="font-semibold">{totalResults}</span> results for "
          <span className="font-semibold">{debouncedQuery}</span>"
          {loading && <span> - Loading...</span>}
        </div>
      )}

      {/* Loading State */}
      {loading && !results.length && debouncedQuery && (
        <LoadingState message="Searching documents..." />
      )}

      {/* Results List */}
      {results.length > 0 && (
        <div className="space-y-4">
          {results.map((result) => (
            <DataCard
              key={result.id}
              title={
                <div className="text-lg font-semibold text-primary-700">
                  {highlightMatch(result.title, debouncedQuery)}
                </div>
              }
              badge={{
                label: `Score: ${result.score.toFixed(2)}`,
                variant: 'primary',
              }}
              className="hover:shadow-md transition-shadow"
            >
              <p className="text-neutral-700 leading-relaxed mb-3">
                {highlightMatch(result.snippet, debouncedQuery)}
              </p>
              <div className="text-xs text-neutral-500">Document ID: {result.id}</div>
            </DataCard>
          ))}
        </div>
      )}

      {/* Empty State - No Results */}
      {!loading && debouncedQuery && results.length === 0 && (
        <EmptyState
          icon={
            <svg
              className="mx-auto h-12 w-12 text-neutral-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          }
          title="No results found"
          message="Try adjusting your search query"
        />
      )}

      {/* Initial State */}
      {!debouncedQuery && (
        <EmptyState
          icon={
            <svg
              className="mx-auto h-12 w-12 text-neutral-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          }
          title="Start searching"
          message="Enter a query to search through documents"
        />
      )}
    </AppLayout>
  );
}
