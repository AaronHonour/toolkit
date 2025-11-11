/**
 * AppLayout Component - Professional Application Shell
 *
 * Sophisticated layout with refined aesthetics and smooth interactions
 */

import React, { useState, useEffect } from 'react';
import { Logo } from '@unistax/atoms';

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
  const [darkMode, setDarkMode] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    // Check system preference
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add('dark');
    }

    // Handle scroll for header elevation
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-dark-300 flex flex-col transition-colors duration-300">
      {/* Header with sophisticated elevation */}
      <header
        className={`
          bg-white/80 dark:bg-dark-200/80 backdrop-blur-xl border-b border-neutral-200 dark:border-dark-100
          sticky top-0 z-50 transition-all duration-300
          ${scrolled ? 'shadow-lg' : 'shadow-sm'}
        `.trim()}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1 min-w-0">
              {/* Unistax Logo with hover effect */}
              <div className="glow-on-hover">
                <Logo size={40} />
              </div>

              <div className="h-8 w-px bg-neutral-300 dark:bg-dark-100" />

              <div className="flex items-center gap-3 flex-1 min-w-0">
                {icon && (
                  <span className="text-3xl animate-scale-in">{icon}</span>
                )}
                <div className="flex-1 min-w-0">
                  <h1 className="text-2xl font-bold text-neutral-900 dark:text-white truncate tracking-tight">
                    {title}
                  </h1>
                  {description && (
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-0.5">
                      {description}
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="ml-4 flex items-center gap-2">
              {/* Dark mode toggle with smooth animation */}
              <button
                onClick={toggleDarkMode}
                className="p-2.5 rounded-xl hover:bg-neutral-100 dark:hover:bg-dark-100 transition-all duration-normal glow-on-hover"
                aria-label="Toggle dark mode"
              >
                {darkMode ? (
                  <svg className="w-5 h-5 text-primary-400 animate-fade-in" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-neutral-600 animate-fade-in" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>
              {headerActions}
            </div>
          </div>
        </div>

        {/* Navigation with refined hover states */}
        {navigationItems && navigationItems.length > 0 && (
          <nav className="border-t border-neutral-200 dark:border-dark-100 bg-white/50 dark:bg-dark-200/50 backdrop-blur-sm transition-colors">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex gap-1 overflow-x-auto custom-scrollbar">
                {navigationItems.map((item, index) => (
                  <a
                    key={index}
                    href={item.href}
                    className={`
                      px-4 py-3 text-sm font-medium border-b-2 transition-all duration-normal whitespace-nowrap
                      ${
                        item.active
                          ? 'border-primary-500 text-primary-500 dark:text-primary-400 bg-primary-50/50 dark:bg-primary-950/20'
                          : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:border-neutral-300 dark:hover:border-dark-100 hover:bg-neutral-50 dark:hover:bg-dark-100/50'
                      }
                    `.trim()}
                  >
                    {item.label}
                  </a>
                ))}
              </div>
            </div>
          </nav>
        )}
      </header>

      {/* Main Content with refined spacing */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-fade-in">
            {children}
          </div>
        </div>
      </main>

      {/* Footer with sophisticated styling */}
      {showFooter && (
        <footer className="mt-auto border-t border-neutral-200 dark:border-dark-100 bg-white/80 dark:bg-dark-200/80 backdrop-blur-xl transition-colors">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {footerContent || (
              <div className="flex items-center justify-between text-sm text-neutral-600 dark:text-neutral-400">
                <div className="flex items-center gap-3">
                  <Logo size={24} />
                  <span className="text-neutral-400 dark:text-neutral-500">•</span>
                  <span className="font-medium">{title}</span>
                </div>
                <div className="text-neutral-500 dark:text-neutral-500 font-medium">
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
