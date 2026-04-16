import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Table, RefreshCw, FileSpreadsheet, Clock, Rows3 } from 'lucide-react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '../services/api';
import { toast } from '../hooks/use-toast';

const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#06b6d4'];

const GoogleSheetsDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeSheet, setActiveSheet] = useState(0);

  const fetchReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/google-sheets/report');
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch Sheets data.');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchReport(); }, [fetchReport]);

  if (loading) return <div className="flex items-center justify-center py-12"><div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin" /></div>;
  if (error) return (
    <div className="text-center py-12" data-testid="sheets-error">
      <FileSpreadsheet className="w-10 h-10 text-gray-600 mx-auto mb-3" />
      <p className="text-gray-400 mb-1 text-sm">{error}</p>
      <Button size="sm" variant="outline" className="mt-3 border-green-600 text-green-400" onClick={fetchReport}><RefreshCw className="w-3 h-3 mr-1" /> Retry</Button>
    </div>
  );
  if (!data || !data.sheets?.length) return null;

  const sheet = data.sheets[activeSheet];
  const preview = sheet.preview_data;

  return (
    <div className="space-y-6" data-testid="sheets-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-green-400" /> Google Sheets
          </h3>
          <p className="text-gray-500 text-xs">{data.total_sheets} connected sheets {data.is_sample_data && <Badge variant="outline" className="ml-2 text-yellow-500 border-yellow-600 text-[10px]">Sample Data</Badge>}</p>
        </div>
        <Button size="sm" variant="ghost" onClick={fetchReport} className="text-gray-500 hover:text-white"><RefreshCw className="w-4 h-4" /></Button>
      </div>

      {/* Sheet Tabs */}
      <div className="flex gap-2">
        {data.sheets.map((s, i) => (
          <button
            key={i}
            onClick={() => setActiveSheet(i)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all ${
              activeSheet === i ? 'bg-green-600/15 border border-green-500/30 text-green-300' : 'bg-gray-800 border border-gray-700 text-gray-400 hover:border-gray-600'
            }`}
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span className="max-w-[150px] truncate">{s.title}</span>
          </button>
        ))}
      </div>

      {/* Sheet Info */}
      <div className="grid grid-cols-3 gap-3">
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="pt-4 pb-3 px-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-gray-500 text-xs">Sheets</span>
              <FileSpreadsheet className="w-4 h-4 text-green-400" />
            </div>
            <p className="text-white text-lg font-bold">{sheet.sheet_count}</p>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="pt-4 pb-3 px-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-gray-500 text-xs">Total Rows</span>
              <Rows3 className="w-4 h-4 text-blue-400" />
            </div>
            <p className="text-white text-lg font-bold">{sheet.row_count}</p>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="pt-4 pb-3 px-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-gray-500 text-xs">Last Modified</span>
              <Clock className="w-4 h-4 text-amber-400" />
            </div>
            <p className="text-white text-sm font-bold">{new Date(sheet.last_modified).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Data Preview Table */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Data Preview — {sheet.title}</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-gray-800">
                  {preview.headers.map(h => <th key={h} className="text-left py-2 px-3 text-gray-500 font-medium text-xs">{h}</th>)}
                </tr></thead>
                <tbody>
                  {preview.rows.map((row, i) => (
                    <tr key={i} className="border-b border-gray-800/50">
                      {row.map((cell, j) => <td key={j} className="py-2 px-3 text-gray-300 text-xs">{cell}</td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Chart */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Visual Summary</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={230}>
              {sheet.chart_data[0]?.revenue !== undefined ? (
                <BarChart data={sheet.chart_data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                  <Bar dataKey="revenue" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              ) : (
                <PieChart>
                  <Pie data={sheet.chart_data} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={{ stroke: '#6b7280' }}>
                    {sheet.chart_data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                </PieChart>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default GoogleSheetsDashboard;
