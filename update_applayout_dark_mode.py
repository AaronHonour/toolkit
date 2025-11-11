#!/usr/bin/env python3
"""Update AppLayout to support dark mode and include logo."""

from pathlib import Path

def update_applayout():
    file_path = Path(__file__).parent / 'frontend' / 'packages' / 'layouts' / 'src' / 'AppLayout' / 'AppLayout.tsx'

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add Logo import
    content = content.replace(
        "import React from 'react';",
        "import React, { useState, useEffect } from 'react';\nimport { Logo } from '@unistax/atoms';"
    )

    # Add dark mode toggle in the component
    new_component = '''export const AppLayout = React.memo<AppLayoutProps>(({
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

  useEffect(() => {
    // Check system preference
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-dark-300 flex flex-col transition-colors duration-300">
      {/* Header */}
      <header className="bg-white dark:bg-dark-200 shadow-sm border-b border-neutral-200 dark:border-dark-100 sticky top-0 z-40 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1 min-w-0">
              {/* Unistax Logo */}
              <Logo size={36} />

              <div className="flex items-center gap-3 flex-1 min-w-0">
                {icon && <span className="text-2xl">{icon}</span>}
                <div className="flex-1 min-w-0">
                  <h1 className="text-2xl font-bold text-neutral-900 dark:text-white truncate">
                    {title}
                  </h1>
                  {description && (
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                      {description}
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="ml-4 flex items-center gap-2">
              {/* Dark mode toggle */}
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-dark-100 transition-colors glow-on-hover"
                aria-label="Toggle dark mode"
              >
                {darkMode ? (
                  <svg className="w-5 h-5 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-neutral-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>
              {headerActions}
            </div>
          </div>
        </div>

        {/* Navigation */}
        {navigationItems && navigationItems.length > 0 && (
          <nav className="border-t border-neutral-200 dark:border-dark-100 bg-white dark:bg-dark-200 transition-colors">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex gap-1 overflow-x-auto">
                {navigationItems.map((item, index) => (
                  <a
                    key={index}
                    href={item.href}
                    className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                      item.active
                        ? 'border-primary-500 text-primary-500 dark:text-primary-400'
                        : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:border-neutral-300 dark:hover:border-dark-100'
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
        <footer className="mt-auto border-t border-neutral-200 dark:border-dark-100 bg-white dark:bg-dark-200 transition-colors">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {footerContent || (
              <div className="flex items-center justify-between text-sm text-neutral-600 dark:text-neutral-400">
                <div className="flex items-center gap-2">
                  <Logo size={20} />
                  <span className="mx-2">•</span>
                  <span>{title}</span>
                </div>
                <div className="text-neutral-500 dark:text-neutral-500">
                  Powered by composable architecture
                </div>
              </div>
            )}
          </div>
        </footer>
      )}
    </div>
  );
});'''

    # Replace the component
    start = content.find('export const AppLayout = React.memo<AppLayoutProps>(')
    if start != -1:
        end = content.find('});', start) + 3
        content = content[:start] + new_component + content[end:]

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Updated AppLayout.tsx with dark mode and logo")

if __name__ == '__main__':
    update_applayout()
