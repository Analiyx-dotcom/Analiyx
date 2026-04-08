import React, { useState, useEffect } from 'react';
import { Palette, Check } from 'lucide-react';
import { CHART_THEMES } from '../constants/chartThemes';
import api from '../services/api';
import { toast } from '../hooks/use-toast';

const ChartThemeSelector = ({ currentTheme, onThemeChange }) => {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSelect = async (key) => {
    setSaving(true);
    try {
      await api.put('/charts/theme', { theme: key });
      onThemeChange(key);
      toast({ title: 'Theme Updated', description: `Chart theme set to ${CHART_THEMES[key].name}` });
    } catch {
      toast({ title: 'Error', description: 'Failed to save theme', variant: 'destructive' });
    } finally {
      setSaving(false);
      setOpen(false);
    }
  };

  return (
    <div className="relative" data-testid="chart-theme-selector">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800 border border-gray-700 hover:border-purple-500/50 transition-colors text-sm text-gray-300"
        data-testid="chart-theme-trigger"
      >
        <Palette className="w-4 h-4 text-purple-400" />
        <span>{CHART_THEMES[currentTheme]?.name || 'Default'}</span>
        <div className="flex gap-0.5 ml-1">
          {(CHART_THEMES[currentTheme]?.preview || CHART_THEMES.default.preview).map((c, i) => (
            <div key={i} className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: c }} />
          ))}
        </div>
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full mt-2 z-50 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl shadow-black/50 p-3 w-64" data-testid="chart-theme-dropdown">
            <p className="text-xs text-gray-500 mb-2 font-medium uppercase tracking-wider">Chart Theme</p>
            <div className="space-y-1">
              {Object.entries(CHART_THEMES).map(([key, theme]) => (
                <button
                  key={key}
                  onClick={() => handleSelect(key)}
                  disabled={saving}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all ${
                    currentTheme === key
                      ? 'bg-purple-500/15 border border-purple-500/30'
                      : 'hover:bg-gray-800 border border-transparent'
                  }`}
                  data-testid={`chart-theme-option-${key}`}
                >
                  <div className="flex gap-1">
                    {theme.preview.map((c, i) => (
                      <div key={i} className="w-4 h-4 rounded-full" style={{ backgroundColor: c }} />
                    ))}
                  </div>
                  <span className="text-sm text-gray-200 flex-1">{theme.name}</span>
                  {currentTheme === key && <Check className="w-4 h-4 text-purple-400" />}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ChartThemeSelector;
