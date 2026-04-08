// 6 Chart color themes for Recharts visualizations
export const CHART_THEMES = {
  default: {
    name: 'Default',
    preview: ['#8b5cf6', '#06b6d4', '#10b981'],
    colors: ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1', '#14b8a6'],
    primary: '#8b5cf6',
    secondary: '#06b6d4',
    accent: '#10b981',
    gradient: ['#8b5cf6', '#06b6d4'],
  },
  forest: {
    name: 'Forest',
    preview: ['#22c55e', '#16a34a', '#a3e635'],
    colors: ['#22c55e', '#16a34a', '#a3e635', '#84cc16', '#4ade80', '#15803d', '#65a30d', '#bef264'],
    primary: '#22c55e',
    secondary: '#16a34a',
    accent: '#a3e635',
    gradient: ['#22c55e', '#a3e635'],
  },
  azure: {
    name: 'Azure',
    preview: ['#3b82f6', '#60a5fa', '#2563eb'],
    colors: ['#3b82f6', '#60a5fa', '#2563eb', '#93c5fd', '#1d4ed8', '#818cf8', '#38bdf8', '#7dd3fc'],
    primary: '#3b82f6',
    secondary: '#60a5fa',
    accent: '#2563eb',
    gradient: ['#3b82f6', '#60a5fa'],
  },
  mint: {
    name: 'Mint',
    preview: ['#2dd4bf', '#14b8a6', '#5eead4'],
    colors: ['#2dd4bf', '#14b8a6', '#5eead4', '#99f6e4', '#0d9488', '#6ee7b7', '#34d399', '#a7f3d0'],
    primary: '#2dd4bf',
    secondary: '#14b8a6',
    accent: '#5eead4',
    gradient: ['#2dd4bf', '#14b8a6'],
  },
  violet: {
    name: 'Violet',
    preview: ['#a855f7', '#c084fc', '#7c3aed'],
    colors: ['#a855f7', '#c084fc', '#7c3aed', '#d8b4fe', '#9333ea', '#e879f9', '#f0abfc', '#c026d3'],
    primary: '#a855f7',
    secondary: '#c084fc',
    accent: '#7c3aed',
    gradient: ['#a855f7', '#c084fc'],
  },
  ocean: {
    name: 'Ocean',
    preview: ['#0ea5e9', '#06b6d4', '#0284c7'],
    colors: ['#0ea5e9', '#06b6d4', '#0284c7', '#22d3ee', '#0369a1', '#38bdf8', '#67e8f9', '#7dd3fc'],
    primary: '#0ea5e9',
    secondary: '#06b6d4',
    accent: '#0284c7',
    gradient: ['#0ea5e9', '#06b6d4'],
  },
};

export const getTheme = (themeKey) => CHART_THEMES[themeKey] || CHART_THEMES.default;
