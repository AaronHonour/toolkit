/**
 * DataTable Component
 * Responsive table for displaying tabular data
 */

import React from 'react';

export interface Column<T> {
  key: keyof T | string;
  label: string;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

export interface DataTableProps<T> {
  /** Table columns */
  columns: Column<T>[];
  /** Table data */
  data: T[];
  /** Row key extractor */
  getRowKey: (row: T) => string | number;
  /** Row click handler */
  onRowClick?: (row: T) => void;
  /** Compact mode */
  compact?: boolean;
  /** Striped rows */
  striped?: boolean;
}

export function DataTable<T>({
  columns,
  data,
  getRowKey,
  onRowClick,
  compact = false,
  striped = false,
}: DataTableProps<T>) {
  const isClickable = Boolean(onRowClick);

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-neutral-200">
        <thead className="bg-neutral-50">
          <tr>
            {columns.map((column, index) => (
              <th
                key={index}
                scope="col"
                style={{ width: column.width }}
                className={`
                  ${compact ? 'px-3 py-2' : 'px-6 py-3'}
                  text-left text-xs font-medium text-neutral-700 uppercase tracking-wider
                  ${column.align === 'center' ? 'text-center' : ''}
                  ${column.align === 'right' ? 'text-right' : ''}
                `}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className={`bg-white divide-y divide-neutral-200 ${striped ? '[&>*:nth-child(even)]:bg-neutral-50' : ''}`}>
          {data.map((row) => (
            <tr
              key={getRowKey(row)}
              className={`
                ${isClickable ? 'hover:bg-neutral-50 cursor-pointer' : ''}
                transition-colors
              `}
              onClick={() => onRowClick?.(row)}
            >
              {columns.map((column, colIndex) => {
                const value = typeof column.key === 'string'
                  ? (row as any)[column.key]
                  : undefined;

                const content = column.render
                  ? column.render(value, row)
                  : value;

                return (
                  <td
                    key={colIndex}
                    className={`
                      ${compact ? 'px-3 py-2' : 'px-6 py-4'}
                      text-sm text-neutral-900 whitespace-nowrap
                      ${column.align === 'center' ? 'text-center' : ''}
                      ${column.align === 'right' ? 'text-right' : ''}
                    `}
                  >
                    {content}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

DataTable.displayName = 'DataTable';
