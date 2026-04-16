import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { BarChart3, RefreshCw, TrendingUp, Eye, MousePointerClick, DollarSign, Users, Target } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, AreaChart } from 'recharts';
import api from '../services/api';
import { toast } from '../hooks/use-toast';

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];

const MetaAdsDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/meta-ads/report');
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch Meta Ads data.');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchReport(); }, [fetchReport]);

  if (loading) return <div className="flex items-center justify-center py-12"><div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" /></div>;
  if (error) return (
    <div className="text-center py-12" data-testid="meta-ads-error">
      <BarChart3 className="w-10 h-10 text-gray-600 mx-auto mb-3" />
      <p className="text-gray-400 mb-1 text-sm">{error}</p>
      <Button size="sm" variant="outline" className="mt-3 border-purple-600 text-purple-400" onClick={fetchReport}><RefreshCw className="w-3 h-3 mr-1" /> Retry</Button>
    </div>
  );
  if (!data) return null;

  const { summary, daily_performance, campaigns, age_breakdown, platform_breakdown } = data;
  const fmt = (n) => n?.toLocaleString('en-IN') ?? '0';
  const fmtCur = (n) => `₹${(n || 0).toLocaleString('en-IN')}`;

  return (
    <div className="space-y-6" data-testid="meta-ads-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" /> Meta Ads Performance
          </h3>
          <p className="text-gray-500 text-xs">Last 30 days {data.is_sample_data && <Badge variant="outline" className="ml-2 text-yellow-500 border-yellow-600 text-[10px]">Sample Data</Badge>}</p>
        </div>
        <Button size="sm" variant="ghost" onClick={fetchReport} className="text-gray-500 hover:text-white"><RefreshCw className="w-4 h-4" /></Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Impressions', value: fmt(summary.total_impressions), icon: Eye, color: 'text-blue-400' },
          { label: 'Reach', value: fmt(summary.total_reach), icon: Users, color: 'text-purple-400' },
          { label: 'Clicks', value: fmt(summary.total_clicks), icon: MousePointerClick, color: 'text-cyan-400' },
          { label: 'Spend', value: fmtCur(summary.total_spend), icon: DollarSign, color: 'text-pink-400' },
          { label: 'Conversions', value: fmt(summary.total_conversions), icon: Target, color: 'text-green-400' },
          { label: 'Avg CTR', value: `${summary.avg_ctr}%`, icon: TrendingUp, color: 'text-amber-400' },
          { label: 'Avg CPC', value: fmtCur(summary.avg_cpc), icon: DollarSign, color: 'text-rose-400' },
          { label: 'CPM', value: fmtCur(summary.avg_cpm), icon: DollarSign, color: 'text-indigo-400' },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label} className="bg-gray-900 border-gray-800">
            <CardContent className="pt-4 pb-3 px-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-500 text-xs">{label}</span>
                <Icon className={`w-4 h-4 ${color}`} />
              </div>
              <p className="text-white text-lg font-bold">{value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Daily Performance */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Daily Performance</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={daily_performance}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} interval={4} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                <Area type="monotone" dataKey="impressions" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.1} strokeWidth={2} />
                <Area type="monotone" dataKey="clicks" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.1} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Platform Breakdown */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Platform Breakdown</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={platform_breakdown} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={3} dataKey="value" label={({ platform, percent }) => `${platform} ${(percent * 100).toFixed(0)}%`} labelLine={{ stroke: '#6b7280' }}>
                  {platform_breakdown.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Age Breakdown */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Age Demographics</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={age_breakdown}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="age_group" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                <Bar dataKey="clicks" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="impressions" fill="#3b82f6" radius={[4, 4, 0, 0]} opacity={0.4} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Spend Trend */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Daily Spend & Conversions</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={daily_performance}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} interval={4} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                <Line type="monotone" dataKey="spend" stroke="#ec4899" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="conversions" stroke="#10b981" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Campaigns Table */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Campaigns</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-gray-800">
                {['Campaign', 'Status', 'Objective', 'Impressions', 'Reach', 'Clicks', 'CTR', 'CPC', 'Spend'].map(h => <th key={h} className="text-left py-2 px-3 text-gray-500 font-medium text-xs">{h}</th>)}
              </tr></thead>
              <tbody>
                {campaigns.map((c, i) => (
                  <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="py-2.5 px-3 text-gray-200 font-medium">{c.name}</td>
                    <td className="py-2.5 px-3"><Badge className={c.status === 'ACTIVE' ? 'bg-green-900/30 text-green-400 border-green-800' : 'bg-gray-800 text-gray-500 border-gray-700'}>{c.status}</Badge></td>
                    <td className="py-2.5 px-3 text-gray-400 text-xs">{c.objective}</td>
                    <td className="py-2.5 px-3 text-gray-300">{fmt(c.impressions)}</td>
                    <td className="py-2.5 px-3 text-gray-300">{fmt(c.reach)}</td>
                    <td className="py-2.5 px-3 text-gray-300">{fmt(c.clicks)}</td>
                    <td className="py-2.5 px-3 text-cyan-400">{c.ctr}%</td>
                    <td className="py-2.5 px-3 text-gray-300">{fmtCur(c.cpc)}</td>
                    <td className="py-2.5 px-3 text-pink-400">{fmtCur(c.spend)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MetaAdsDashboard;
