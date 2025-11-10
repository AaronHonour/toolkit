/**
 * Tabs Component
 * Tabbed navigation for switching between content sections
 */

import React, { useState } from 'react';

export interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  badge?: string | number;
  disabled?: boolean;
}

export interface TabsProps {
  /** Array of tabs */
  tabs: Tab[];
  /** Currently active tab ID */
  activeTab?: string;
  /** Callback when tab changes */
  onChange?: (tabId: string) => void;
  /** Tab content */
  children?: React.ReactNode;
  /** Tab style variant */
  variant?: 'default' | 'pills';
  /** Full width tabs */
  fullWidth?: boolean;
}

export const Tabs = React.memo<TabsProps>(({
  tabs,
  activeTab: controlledActiveTab,
  onChange,
  children,
  variant = 'default',
  fullWidth = false,
}) => {
  const [internalActiveTab, setInternalActiveTab] = useState(tabs[0]?.id || '');

  const activeTab = controlledActiveTab ?? internalActiveTab;

  const handleTabClick = (tabId: string, disabled?: boolean) => {
    if (disabled) return;

    if (onChange) {
      onChange(tabId);
    } else {
      setInternalActiveTab(tabId);
    }
  };

  const baseTabClasses = `
    px-4 py-2 font-medium text-sm transition-colors cursor-pointer
    ${fullWidth ? 'flex-1 text-center' : ''}
  `;

  const variantClasses = {
    default: (isActive: boolean, disabled?: boolean) => `
      border-b-2
      ${isActive
        ? 'border-primary-600 text-primary-600'
        : 'border-transparent text-neutral-600 hover:text-neutral-900 hover:border-neutral-300'
      }
      ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
    `,
    pills: (isActive: boolean, disabled?: boolean) => `
      rounded-lg
      ${isActive
        ? 'bg-primary-100 text-primary-700'
        : 'text-neutral-600 hover:bg-neutral-100'
      }
      ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
    `,
  };

  return (
    <div>
      {/* Tab Headers */}
      <div className={`flex ${variant === 'default' ? 'border-b border-neutral-200' : 'gap-2'} ${fullWidth ? 'w-full' : ''}`}>
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab;

          return (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id, tab.disabled)}
              className={`${baseTabClasses} ${variantClasses[variant](isActive, tab.disabled)}`}
              disabled={tab.disabled}
              aria-selected={isActive}
              role="tab"
            >
              <div className="flex items-center gap-2 justify-center">
                {tab.icon}
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className={`
                    px-2 py-0.5 text-xs rounded-full
                    ${isActive
                      ? 'bg-primary-600 text-white'
                      : 'bg-neutral-200 text-neutral-700'
                    }
                  `}>
                    {tab.badge}
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {children && (
        <div className="mt-4" role="tabpanel">
          {children}
        </div>
      )}
    </div>
  );
});

Tabs.displayName = 'Tabs';

/** Helper component for tab panels */
export interface TabPanelProps {
  /** Tab ID this panel belongs to */
  value: string;
  /** Currently active tab */
  activeTab: string;
  /** Panel content */
  children: React.ReactNode;
  /** Keep mounted when inactive */
  keepMounted?: boolean;
}

export const TabPanel: React.FC<TabPanelProps> = ({
  value,
  activeTab,
  children,
  keepMounted = false,
}) => {
  const isActive = value === activeTab;

  if (!isActive && !keepMounted) {
    return null;
  }

  return (
    <div className={isActive ? 'block' : 'hidden'}>
      {children}
    </div>
  );
};
