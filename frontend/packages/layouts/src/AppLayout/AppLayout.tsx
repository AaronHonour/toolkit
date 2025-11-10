/**
 * AppLayout Component
 * Consistent layout wrapper for all applications
 * Provides header, footer, navigation, and responsive container
 */

import React from 'react';

export interface AppLayoutProps {
  /** Application title shown in header */
  title: string;
  /** Application description/subtitle */
  description?: string;
  /** Icon or emoji for the app */
  icon?: string;
  /** Navigation items */
  navigationItems?: Array<{
    label: string;
    href: string;
    active?: boolean;
  }>;
  /** Show footer */
  showFooter?: boolean;
  /** Footer content (defaults to app info) */
  footerContent?: React.ReactNode;
  /** Main content */
  children: React.ReactNode;
  /** Header actions (buttons, etc.) */
  headerActions?: React.ReactNode;
}

export const AppLayout = React.memo<AppLayoutProps>(({
  title,
  description,
  icon,
  navigationItems,
  showFooter = true,
  footerContent,
  children,
  headerActions,
}) => {
  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-neutral-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3">
                {icon && <span className="text-2xl">{icon}</span>}
                <div>
                  <h1 className="text-2xl font-bold text-neutral-900 truncate">
                    {title}
                  </h1>
                  {description && (
                    <p className="text-sm text-neutral-600 mt-1">
                      {description}
                    </p>
                  )}
                </div>
              </div>
            </div>
            {headerActions && (
              <div className="ml-4 flex items-center gap-2">
                {headerActions}
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        {navigationItems && navigationItems.length > 0 && (
          <nav className="border-t border-neutral-200 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex gap-1 overflow-x-auto">
                {navigationItems.map((item, index) => (
                  <a
                    key={index}
                    href={item.href}
                    className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                      item.active
                        ? 'border-primary-600 text-primary-600'
                        : 'border-transparent text-neutral-600 hover:text-neutral-900 hover:border-neutral-300'
                    }`}
                  >
                    {item.label}
                  </a>
                ))}
              </div>
            </div>
          </nav>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>

      {/* Footer */}
      {showFooter && (
        <footer className="mt-auto border-t border-neutral-200 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {footerContent || (
              <div className="flex items-center justify-between text-sm text-neutral-600">
                <div>
                  <span className="font-semibold">Toolkit Frontend</span>
                  <span className="mx-2">•</span>
                  <span>{title}</span>
                </div>
                <div className="text-neutral-500">
                  Powered by composable architecture
                </div>
              </div>
            )}
          </div>
        </footer>
      )}
    </div>
  );
});

AppLayout.displayName = 'AppLayout';
